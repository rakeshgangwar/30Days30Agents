"""
Data Analysis Agent - CSV Service

This module provides functionality for handling CSV files.
"""

import pandas as pd
import io
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

from app.config import settings
from app.services.llm_service import ChatOpenRouter

# Set up logging
logger = logging.getLogger(__name__)


def load_csv_file(file_content: bytes, filename: str) -> Tuple[bool, pd.DataFrame, Optional[str]]:
    """
    Load a CSV file into a pandas DataFrame.
    
    Args:
        file_content: The uploaded file content
        filename: The name of the uploaded file
        
    Returns:
        Tuple[bool, pd.DataFrame, Optional[str]]: Success status, DataFrame, and error message if any
    """
    try:
        # Create a BytesIO object from the file content
        file_obj = io.BytesIO(file_content)
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_obj)
        
        if df.empty:
            return False, pd.DataFrame(), "The uploaded CSV file is empty"
        
        return True, df, None
    except Exception as e:
        logger.error(f"Error loading CSV file {filename}: {str(e)}")
        return False, pd.DataFrame(), f"Error loading CSV file: {str(e)}"


def get_dataframe_info(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get basic information about a DataFrame.
    
    Args:
        df: The pandas DataFrame
        
    Returns:
        Dict[str, Any]: Dictionary containing DataFrame information
    """
    if df.empty:
        return {"error": "DataFrame is empty"}
    
    info = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_values": df.isnull().sum().to_dict(),
        "numeric_columns": list(df.select_dtypes(include=['number']).columns),
        "categorical_columns": list(df.select_dtypes(include=['object', 'category']).columns),
        "datetime_columns": list(df.select_dtypes(include=['datetime']).columns),
    }
    
    # Add basic statistics for numeric columns
    if info["numeric_columns"]:
        info["numeric_stats"] = df[info["numeric_columns"]].describe().to_dict()
    
    return info


def get_dataframe_preview(df: pd.DataFrame, rows: int = 5) -> List[Dict[str, Any]]:
    """
    Get a preview of the first few rows of a DataFrame.
    
    Args:
        df: The pandas DataFrame
        rows: Number of rows to include in the preview
        
    Returns:
        List[Dict[str, Any]]: List of dictionaries representing the preview rows
    """
    if df.empty:
        return []
    
    # Convert the first few rows to a list of dictionaries
    preview = df.head(rows).to_dict(orient='records')
    
    # Convert any non-serializable values to strings
    for row in preview:
        for key, value in row.items():
            if not isinstance(value, (str, int, float, bool, type(None))):
                row[key] = str(value)
    
    return preview


def initialize_dataframe_agent(llm: ChatOpenRouter, df: pd.DataFrame) -> Optional[Any]:
    """
    Initialize a Pandas DataFrame agent with the given LLM and DataFrame.

    Args:
        llm: The LLM to use for the agent
        df: The DataFrame to analyze

    Returns:
        Optional[Any]: Initialized agent or None if initialization fails
    """
    if df is None or df.empty:
        logger.error("Cannot initialize agent: DataFrame is empty or None")
        return None

    if llm is None:
        logger.error("Cannot initialize agent: LLM is not initialized")
        return None

    try:
        agent = create_pandas_dataframe_agent(
            llm=llm,
            df=df,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            allow_dangerous_code=settings.AGENT_ALLOW_DANGEROUS_CODE,
            max_iterations=settings.AGENT_MAX_ITERATIONS,
            max_execution_time=settings.AGENT_MAX_EXECUTION_TIME,
            early_stopping_method=settings.AGENT_EARLY_STOPPING_METHOD
        )
        logger.info("DataFrame agent initialized successfully!")
        return agent
    except Exception as e:
        logger.error(f"Error initializing DataFrame agent: {str(e)}")
        return None


def process_dataframe_query(agent: Any, query: str) -> Dict[str, Any]:
    """
    Process a query using the DataFrame agent.

    Args:
        agent: The agent to use for processing
        query: The query to process

    Returns:
        Dict[str, Any]: The agent's response
    """
    if agent is None:
        logger.error("Cannot process query: Agent is not initialized")
        return {"success": False, "error": "Agent is not initialized"}

    try:
        response = agent.invoke(query)
        return {"success": True, "result": response}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return {"success": False, "error": f"Error processing query: {str(e)}"}
