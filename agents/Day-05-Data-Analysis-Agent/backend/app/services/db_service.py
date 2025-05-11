"""
Data Analysis Agent - Database Service

This module provides functionality for handling SQL databases.
"""

import pandas as pd
import logging
from sqlalchemy import create_engine, text
from typing import Any, Dict, List, Optional, Tuple, Union

# Import LangChain components for SQL integration
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_core.language_models import BaseLanguageModel

from app.config import settings

# Set up logging
logger = logging.getLogger(__name__)


def create_db_connection(db_type: str, **kwargs) -> Tuple[bool, Optional[Any], Optional[str]]:
    """
    Create a database connection using SQLAlchemy.

    Args:
        db_type: The type of database ('sqlite' or 'postgresql')
        **kwargs: Connection parameters

    Returns:
        Tuple[bool, Optional[Any], Optional[str]]: Success status, SQLAlchemy engine, and error message if any
    """
    try:
        if db_type.lower() == 'sqlite':
            db_path = kwargs.get('db_path', ':memory:')
            engine = create_engine(f'sqlite:///{db_path}')
        elif db_type.lower() == 'postgresql':
            host = kwargs.get('host', 'localhost')
            port = kwargs.get('port', '5432')
            database = kwargs.get('database', '')
            user = kwargs.get('user', '')
            password = kwargs.get('password', '')

            engine = create_engine(
                f'postgresql://{user}:{password}@{host}:{port}/{database}'
            )
        else:
            error_msg = f"Unsupported database type: {db_type}"
            logger.error(error_msg)
            return False, None, error_msg

        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return True, engine, None
    except Exception as e:
        error_msg = f"Error connecting to database: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg


def create_langchain_sql_database(engine: Any, include_tables: Optional[List[str]] = None,
                                 sample_rows_in_table_info: int = 3) -> Optional[SQLDatabase]:
    """
    Create a LangChain SQLDatabase from a SQLAlchemy engine.

    Args:
        engine: SQLAlchemy engine
        include_tables: Optional list of tables to include (if None, all tables are included)
        sample_rows_in_table_info: Number of sample rows to include in table info

    Returns:
        Optional[SQLDatabase]: LangChain SQLDatabase or None if creation fails
    """
    try:
        db = SQLDatabase(
            engine=engine,
            include_tables=include_tables,
            sample_rows_in_table_info=sample_rows_in_table_info
        )
        return db
    except Exception as e:
        logger.error(f"Error creating LangChain SQLDatabase: {str(e)}")
        return None


def initialize_sql_agent(llm: BaseLanguageModel, db: SQLDatabase,
                        verbose: bool = True) -> Optional[Any]:
    """
    Initialize a SQL agent using LangChain.

    Args:
        llm: The language model to use
        db: The SQLDatabase to query
        verbose: Whether to enable verbose output

    Returns:
        Optional[Any]: SQL agent or None if initialization fails
    """
    try:
        # Create a toolkit with the database
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        # Create the SQL agent
        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=verbose,
            agent_type="openai-tools",
            max_iterations=settings.AGENT_MAX_ITERATIONS,
            early_stopping_method=settings.AGENT_EARLY_STOPPING_METHOD
        )

        return agent
    except Exception as e:
        logger.error(f"Error initializing SQL agent: {str(e)}")
        return None


def initialize_sql_chain(llm: BaseLanguageModel, db: SQLDatabase) -> Optional[Any]:
    """
    Initialize a SQL chain using LangChain.

    Args:
        llm: The language model to use
        db: The SQLDatabase to query

    Returns:
        Optional[Any]: SQL chain or None if initialization fails
    """
    try:
        # Create the SQL chain
        chain = create_sql_query_chain(llm, db)
        return chain
    except Exception as e:
        logger.error(f"Error initializing SQL chain: {str(e)}")
        return None


def execute_sql_query(engine: Any, query: str) -> Tuple[bool, Any]:
    """
    Execute a SQL query using SQLAlchemy.

    Args:
        engine: SQLAlchemy engine
        query: SQL query string

    Returns:
        Tuple[bool, Any]: (success, result) where result is a DataFrame or error message
    """
    try:
        result = pd.read_sql_query(query, engine)
        return True, result
    except Exception as e:
        return False, str(e)


def get_table_names(engine: Any) -> List[str]:
    """
    Get a list of table names from the database.

    Args:
        engine: SQLAlchemy engine

    Returns:
        List[str]: List of table names
    """
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        return inspector.get_table_names()
    except Exception as e:
        logger.error(f"Error getting table names: {str(e)}")
        return []


def get_table_schema(engine: Any, table_name: str) -> Dict[str, Any]:
    """
    Get the schema for a specific table.

    Args:
        engine: SQLAlchemy engine
        table_name: Name of the table

    Returns:
        Dict[str, Any]: Dictionary containing table schema information
    """
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)

        schema = {
            "table_name": table_name,
            "columns": []
        }

        for column in columns:
            schema["columns"].append({
                "name": column["name"],
                "type": str(column["type"]),
                "nullable": column.get("nullable", True),
                "default": str(column.get("default", None)),
                "primary_key": column.get("primary_key", False)
            })

        return schema
    except Exception as e:
        logger.error(f"Error getting table schema: {str(e)}")
        return {"error": str(e)}


def get_database_info(db: SQLDatabase) -> str:
    """
    Get information about the database schema.

    Args:
        db: LangChain SQLDatabase

    Returns:
        str: Formatted string with database schema information
    """
    try:
        return db.get_table_info()
    except Exception as e:
        logger.error(f"Error getting database info: {str(e)}")
        return f"Error retrieving database information: {str(e)}"


def process_sql_query(agent: Any, query: str) -> Dict[str, Any]:
    """
    Process a natural language query using the SQL agent.

    Args:
        agent: The SQL agent
        query: Natural language query

    Returns:
        Dict[str, Any]: Result from the agent
    """
    try:
        result = agent.invoke({"input": query})
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error processing SQL query with agent: {str(e)}")
        return {"success": False, "error": f"Error: {str(e)}"}


def generate_sql_query(chain: Any, question: str) -> str:
    """
    Generate a SQL query from a natural language question.

    Args:
        chain: The SQL chain
        question: Natural language question

    Returns:
        str: Generated SQL query
    """
    try:
        sql_query = chain.invoke({"question": question})
        return sql_query
    except Exception as e:
        logger.error(f"Error generating SQL query: {str(e)}")
        return f"Error generating SQL query: {str(e)}"
