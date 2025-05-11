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
async def query_csv(query: str = Form(...), csv_id: str = Form(...)):
    """
    Execute a natural language query on a CSV file.

    Args:
        query: The natural language query
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
        response = process_dataframe_query(agent, query)

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
            visualization_keywords = ["plot", "chart", "graph", "visualize", "visualization", "bar chart", "line chart",
                                     "histogram", "pie chart", "scatter plot", "heatmap", "box plot"]

            needs_visualization = any(keyword in query.lower() for keyword in visualization_keywords)

            if needs_visualization:
                logger.info(f"Visualization requested in query: {query}")
                logger.info(f"DataFrame shape: {df.shape}, columns: {df.columns.tolist()}")

                # Use the fallback visualization which is more general and works with any data
                viz_data = create_fallback_visualization(df, query)

                if viz_data:
                    logger.info(f"Visualization created successfully")
                    # Log a sample of the visualization data to debug
                    if isinstance(viz_data, dict):
                        # Log the structure of the visualization data
                        logger.info(f"Visualization data structure: {list(viz_data.keys())}")

                        # Log layout information if available
                        if 'layout' in viz_data:
                            logger.info(f"Visualization layout title: {viz_data['layout'].get('title', 'No title')}")

                        # Log data information if available
                        if 'data' in viz_data:
                            logger.info(f"Visualization contains {len(viz_data['data'])} data traces")
                            for i, trace in enumerate(viz_data['data']):
                                logger.info(f"Trace {i} type: {trace.get('type', 'unknown')}")

                    visualization = {
                        "type": "plotly",
                        "figure": viz_data
                    }

                    # Log the final visualization object structure
                    logger.info(f"Final visualization object keys: {list(visualization.keys())}")
                    logger.info(f"Figure object keys: {list(visualization['figure'].keys()) if visualization['figure'] else 'Empty figure'}")
                else:
                    logger.error("Failed to create visualization data")
        except Exception as viz_error:
            logger.error(f"Error creating visualization: {str(viz_error)}")
            import traceback
            logger.error(f"Visualization error traceback: {traceback.format_exc()}")

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
