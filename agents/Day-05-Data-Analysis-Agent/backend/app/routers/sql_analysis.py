"""
Data Analysis Agent - SQL Analysis Router

This module contains FastAPI routes for SQL database analysis.
"""

import pandas as pd
import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional

from app.models.schemas import QueryRequest, DBConnectionRequest, DBConnectionResponse, QueryResponse, AnalysisResult, VisualizationData
from app.services.llm_service import initialize_llm
from app.services.db_service import (
    create_db_connection,
    create_langchain_sql_database,
    initialize_sql_agent,
    initialize_sql_chain,
    get_table_names,
    get_database_info,
    process_sql_query,
    generate_sql_query,
    execute_sql_query
)
from app.services.visualization_service import create_plotly_visualization, create_fallback_visualization
from app.config import settings

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/db", tags=["SQL Analysis"])

# In-memory storage for database connections and agents
# In a production app, this would be replaced with a more robust solution
db_connections: Dict[str, Any] = {}
db_agents: Dict[str, Any] = {}
db_chains: Dict[str, Any] = {}
langchain_dbs: Dict[str, Any] = {}


@router.post("/connect", response_model=DBConnectionResponse)
async def connect_to_database(request: DBConnectionRequest):
    """
    Establish a connection to a database.

    Args:
        request: The database connection request

    Returns:
        DBConnectionResponse: Response with connection status and database information
    """
    try:
        # Create database connection
        success, engine, error = create_db_connection(request.db_type, **request.connection_params)

        if not success:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": error}
            )

        # Generate a unique ID for this connection
        # Use a timestamp-based ID that matches the frontend's format
        import time
        connection_id = f"{request.db_type}_{int(time.time() * 1000)}"

        # Store the connection
        db_connections[connection_id] = engine

        # Get schema from connection parameters if provided
        schema = request.connection_params.get('schema', None)
        if schema:
            logger.info(f"Using schema from connection parameters: {schema}")

        # Get table names with schema if provided
        tables = get_table_names(engine, schema=schema)

        # Create LangChain SQLDatabase with schema if provided
        langchain_db = create_langchain_sql_database(engine, schema=schema)
        if langchain_db:
            langchain_dbs[connection_id] = langchain_db

            # Initialize LLM
            llm = initialize_llm()
            if llm:
                # Initialize SQL agent
                agent = initialize_sql_agent(llm, langchain_db)
                if agent:
                    db_agents[connection_id] = agent

                # Initialize SQL chain
                chain = initialize_sql_chain(llm, langchain_db)
                if chain:
                    db_chains[connection_id] = chain

        # Return the connection_id to the frontend
        return {
            "success": True,
            "message": f"Successfully connected to {request.db_type} database",
            "tables": tables,
            "connection_id": connection_id  # Include the connection ID in the response
        }

    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Error connecting to database: {str(e)}"}
        )


@router.post("/query", response_model=QueryResponse)
async def query_database(request: QueryRequest, connection_id: str):
    """
    Execute a natural language query on a database.

    Args:
        request: The query request
        connection_id: ID of the database connection to query

    Returns:
        QueryResponse: Response with query results
    """
    # Log the received connection_id for debugging
    logger.info(f"Received query request with connection_id: {connection_id}")
    logger.info(f"Available connection IDs: {list(db_connections.keys())}")
    if connection_id not in db_connections:
        return JSONResponse(
            status_code=404,
            content={"success": False, "error": "Database connection not found. Please connect to a database first."}
        )

    if connection_id not in db_agents:
        # Initialize LLM and agent if not already done
        llm = initialize_llm()
        if not llm:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to initialize LLM"}
            )

        langchain_db = langchain_dbs.get(connection_id)
        if not langchain_db:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to initialize LangChain database"}
            )

        agent = initialize_sql_agent(llm, langchain_db)
        if not agent:
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": "Failed to initialize SQL agent"}
            )

        db_agents[connection_id] = agent

        chain = initialize_sql_chain(llm, langchain_db)
        if chain:
            db_chains[connection_id] = chain

    try:
        # Get the agent, chain, and engine
        agent = db_agents[connection_id]
        chain = db_chains.get(connection_id)
        engine = db_connections[connection_id]

        # Log agent configuration before processing
        logger.info(f"Using SQL agent with configuration from settings: max_iterations={settings.AGENT_MAX_ITERATIONS}, max_execution_time={settings.AGENT_MAX_EXECUTION_TIME}")

        # Process the query using the agent
        response = process_sql_query(agent, request.query)

        if not response["success"]:
            logger.error(f"SQL query processing failed: {response.get('error', 'Unknown error')}")
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": response["error"]}
            )

        # Extract the result
        result = response["result"]

        # Try to extract the SQL query if available
        sql_query = None
        if chain:
            try:
                sql_query = generate_sql_query(chain, request.query)
            except Exception as sql_error:
                logger.error(f"Error generating SQL query: {str(sql_error)}")

        # Check if there's any tabular data in the result
        data = None
        df = None

        # Try to extract a DataFrame from the agent's output
        if sql_query:
            try:
                success, query_result = execute_sql_query(engine, sql_query)
                if success and isinstance(query_result, pd.DataFrame):
                    df = query_result
                    data = df.to_dict(orient='records')
            except Exception as exec_error:
                logger.error(f"Error executing SQL query: {str(exec_error)}")

        # Create a visualization if appropriate
        visualization = None
        try:
            # Determine if visualization is needed based on the query
            visualization_keywords = ["plot", "chart", "graph", "visualize", "visualization", "bar chart", "line chart",
                                     "histogram", "pie chart", "scatter plot", "heatmap", "box plot"]

            needs_visualization = df is not None and any(keyword in request.query.lower() for keyword in visualization_keywords)

            if needs_visualization:
                logger.info(f"Visualization requested in query: {request.query}")
                logger.info(f"DataFrame shape: {df.shape if df is not None else 'No DataFrame'}")
                logger.info(f"DataFrame columns: {df.columns.tolist() if df is not None else 'No columns'}")

                # Use the fallback visualization which is more general and works with any data
                if df is not None:
                    viz_data = create_fallback_visualization(df, request.query)

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
                else:
                    logger.error("Cannot create visualization: DataFrame is None")
        except Exception as viz_error:
            logger.error(f"Error creating visualization: {str(viz_error)}")
            import traceback
            logger.error(f"Visualization error traceback: {traceback.format_exc()}")

        # Create the analysis result
        analysis_result = AnalysisResult(
            text=result.get("output", "No output generated"),
            data=data,
            visualization=visualization if visualization else None,
            code=sql_query  # Include the generated SQL query
        )

        return {"success": True, "result": analysis_result}

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

        # Log the connection ID and query for debugging
        logger.error(f"Connection ID: {connection_id}")
        logger.error(f"Query: {request.query}")

        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Error processing query: {str(e)}"}
        )
