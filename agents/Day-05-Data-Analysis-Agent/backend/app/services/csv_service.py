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
        # Log DataFrame information
        logger.info(f"DataFrame shape: {df.shape}")
        logger.info(f"DataFrame columns: {df.columns.tolist()}")
        logger.info(f"DataFrame dtypes: {df.dtypes}")
        logger.info(f"DataFrame has NaN values: {df.isna().any().any()}")

        # Log LLM information
        logger.info(f"LLM type: {type(llm).__name__}")
        logger.info(f"LLM model name: {getattr(llm, 'model_name', 'Unknown')}")

        # Log agent configuration
        logger.info("Creating pandas dataframe agent with the following configuration:")
        logger.info(f"  Agent type: {AgentType.OPENAI_FUNCTIONS}")
        logger.info(f"  Allow dangerous code: {settings.AGENT_ALLOW_DANGEROUS_CODE}")
        logger.info(f"  Max iterations: {settings.AGENT_MAX_ITERATIONS}")
        logger.info(f"  Max execution time: {settings.AGENT_MAX_EXECUTION_TIME}")
        logger.info(f"  Early stopping method: {settings.AGENT_EARLY_STOPPING_METHOD}")

        # Create a custom prefix that explicitly instructs the agent to use the full dataset
        custom_prefix = """You are working with a pandas DataFrame that contains {total_rows} rows and {total_cols} columns.
When analyzing this data, you MUST ALWAYS use the FULL dataset by executing Python code on the entire DataFrame.
DO NOT limit your analysis to just the preview rows shown in the prompt.

For example:
- When counting rows, use df.shape[0] to get the total count
- When calculating statistics, use df.mean(), df.sum(), etc. on the entire DataFrame
- When filtering data, apply the filter to the full DataFrame: df[df['column'] > value]

IMPORTANT: You MUST EXECUTE the Python code you generate using the python_repl_ast tool.
DO NOT just suggest code - actually run it to get real results from the data.
Always execute your code and provide the actual results in your response.

Always execute Python code that operates on the ENTIRE DataFrame, not just what you can see in the preview.
"""

        # Format the custom prefix with actual dataframe info
        formatted_prefix = custom_prefix.format(
            total_rows=df.shape[0],
            total_cols=df.shape[1]
        )

        logger.info(f"Using custom prefix: {formatted_prefix[:100]}...")

        # Create the agent with a more explicit configuration
        agent = create_pandas_dataframe_agent(
            llm=llm,
            df=df,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            allow_dangerous_code=True,  # Explicitly set to True to ensure code execution
            max_iterations=settings.AGENT_MAX_ITERATIONS,
            max_execution_time=60,  # Increase execution time to allow for code execution
            early_stopping_method=settings.AGENT_EARLY_STOPPING_METHOD,
            # Use a reasonable number of rows for the preview
            number_of_head_rows=10,
            # Add our custom prefix
            prefix=formatted_prefix,
            # Explicitly include Python execution in the prompt
            include_df_in_prompt=True,
            # Ensure the agent has all the tools it needs
            extra_tools=[]  # This ensures default tools are used
        )

        # Log that we've explicitly enabled code execution
        logger.info("Agent created with code execution explicitly enabled")

        logger.info("DataFrame agent initialized successfully!")

        # Try to log agent details if possible
        try:
            agent_dict = vars(agent)
            logger.info(f"Agent attributes: {list(agent_dict.keys())}")

            # Log tool names if available
            if 'tools' in agent_dict:
                tool_names = [getattr(tool, 'name', str(tool)) for tool in agent_dict['tools']]
                logger.info(f"Agent tools: {tool_names}")
        except:
            logger.info("Could not extract detailed agent information")

        return agent
    except Exception as e:
        logger.error(f"Error initializing DataFrame agent: {str(e)}")
        logger.exception("Detailed exception information:")
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
        # Add detailed logging
        logger.info(f"Processing query: {query}")

        # Modify the query to explicitly instruct the agent to use the full dataset and execute code
        enhanced_query = f"""Remember to analyze the FULL dataset, not just the preview rows.

{query}

Important instructions:
1. Make sure your analysis includes ALL rows in the dataframe, not just the sample rows
2. You MUST EXECUTE your Python code using the python_repl_ast tool to get actual results
3. Do not just write code without executing it
4. Always include the actual numerical results from running your code

First write the code, then execute it with python_repl_ast, then provide the answer based on the execution results."""

        logger.info(f"Enhanced query: {enhanced_query[:100]}...")

        # Log agent type and configuration
        logger.info(f"Agent type: {type(agent).__name__}")

        # Invoke the agent
        logger.info("Invoking agent...")
        response = agent.invoke(enhanced_query)

        # Log the response structure
        logger.info(f"Response type: {type(response).__name__}")
        logger.info(f"Response keys: {response.keys() if hasattr(response, 'keys') else 'No keys'}")

        # Log intermediate steps if available
        if hasattr(response, 'get') and response.get('intermediate_steps'):
            logger.info("Intermediate steps found in response")
            for i, step in enumerate(response.get('intermediate_steps', [])):
                if isinstance(step, tuple) and len(step) > 1:
                    action, action_result = step
                    logger.info(f"Step {i+1}:")
                    logger.info(f"  Action: {action}")
                    logger.info(f"  Action type: {type(action).__name__}")
                    logger.info(f"  Result type: {type(action_result).__name__}")

                    # If the result is a DataFrame, log its shape
                    if isinstance(action_result, pd.DataFrame):
                        logger.info(f"  DataFrame shape: {action_result.shape}")

        # Log the final output
        if hasattr(response, 'get'):
            logger.info(f"Output: {response.get('output', 'No output')[:100]}...")
        else:
            logger.info(f"Output: {str(response)[:100]}...")

        return {"success": True, "result": response}
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        logger.exception("Detailed exception information:")
        return {"success": False, "error": f"Error processing query: {str(e)}"}
