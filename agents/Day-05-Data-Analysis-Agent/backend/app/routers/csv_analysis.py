"""
Data Analysis Agent - CSV Analysis Router

This module contains FastAPI routes for CSV file analysis.
"""

import pandas as pd
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional

from app.models.schemas import QueryRequest, CSVUploadResponse, QueryResponse, AnalysisResult, VisualizationData
from app.services.llm_service import initialize_llm
from app.services.csv_service import load_csv_file, get_dataframe_info, get_dataframe_preview, initialize_dataframe_agent, process_dataframe_query
from app.services.visualization_service import create_plotly_visualization, create_fallback_visualization, generate_visualization_prompt

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/csv", tags=["CSV Analysis"])

# In-memory storage for uploaded CSV data
# In a production app, this would be replaced with a database or file storage
csv_data_store: Dict[str, pd.DataFrame] = {}
agent_store: Dict[str, Any] = {}


@router.post("/upload", response_model=CSVUploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload and process a CSV file.
    
    Args:
        file: The CSV file to upload
        
    Returns:
        CSVUploadResponse: Response with upload status and file information
    """
    if not file.filename.endswith('.csv'):
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Only CSV files are supported"}
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Load CSV file
        success, df, error = load_csv_file(file_content, file.filename)
        
        if not success:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": error}
            )
        
        # Generate a unique ID for this CSV data (using filename for simplicity)
        # In a production app, use a more robust ID generation method
        csv_id = file.filename
        
        # Store the DataFrame in memory
        csv_data_store[csv_id] = df
        
        # Get DataFrame info and preview
        info = get_dataframe_info(df)
        preview = get_dataframe_preview(df)
        
        # Initialize LLM and agent
        llm = initialize_llm()
        if llm:
            agent = initialize_dataframe_agent(llm, df)
            if agent:
                agent_store[csv_id] = agent
        
        return {
            "success": True,
            "message": f"Successfully uploaded and processed {file.filename}",
            "columns": info["columns"],
            "rows": info["shape"][0],
            "preview": preview
        }
    
    except Exception as e:
        logger.error(f"Error processing CSV upload: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Error processing CSV upload: {str(e)}"}
        )


@router.post("/query", response_model=QueryResponse)
async def query_csv(request: QueryRequest, csv_id: str = Form(...)):
    """
    Execute a natural language query on a CSV file.
    
    Args:
        request: The query request
        csv_id: ID of the CSV file to query
        
    Returns:
        QueryResponse: Response with query results
    """
    if csv_id not in csv_data_store:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "CSV file not found. Please upload a file first."}
        )
    
    if csv_id not in agent_store:
        # Initialize LLM and agent if not already done
        llm = initialize_llm()
        if not llm:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to initialize LLM"}
            )
        
        df = csv_data_store[csv_id]
        agent = initialize_dataframe_agent(llm, df)
        if not agent:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to initialize agent"}
            )
        
        agent_store[csv_id] = agent
    
    try:
        # Get the agent and DataFrame
        agent = agent_store[csv_id]
        df = csv_data_store[csv_id]
        
        # Process the query
        response = process_dataframe_query(agent, request.query)
        
        if not response["success"]:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": response["error"]}
            )
        
        # Extract the result
        result = response["result"]
        
        # Check if there's any tabular data in the result
        # This is a simplified approach - in a real app, you'd need more sophisticated parsing
        data = None
        if isinstance(result.get("output"), str) and "dataframe" in result.get("output", "").lower():
            # Try to extract a DataFrame from the agent's intermediate steps
            for step in result.get("intermediate_steps", []):
                if isinstance(step, tuple) and len(step) > 1:
                    action, action_result = step
                    if isinstance(action_result, pd.DataFrame):
                        data = action_result.to_dict(orient='records')
                        break
        
        # Create a visualization if appropriate
        visualization = None
        try:
            # Determine if visualization is needed based on the query
            if "plot" in request.query.lower() or "chart" in request.query.lower() or "graph" in request.query.lower() or "visualize" in request.query.lower():
                # Try to create a visualization
                viz_data = create_fallback_visualization(df, request.query)
                if viz_data:
                    visualization = {
                        "type": "plotly",
                        "figure": viz_data
                    }
        except Exception as viz_error:
            logger.error(f"Error creating visualization: {str(viz_error)}")
        
        # Create the analysis result
        analysis_result = AnalysisResult(
            text=result.get("output", "No output generated"),
            data=data,
            visualization=visualization if visualization else None,
            code=None  # We're not exposing code in this version
        )
        
        return {"success": True, "result": analysis_result}
    
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Error processing query: {str(e)}"}
        )
