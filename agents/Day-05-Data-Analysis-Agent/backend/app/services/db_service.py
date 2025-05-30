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
            schema = kwargs.get('schema', None)

            # Build connection string
            connection_string = f'postgresql://{user}:{password}@{host}:{port}/{database}'

            # Log connection details (without password)
            logger.info(f"Connecting to PostgreSQL database: host={host}, port={port}, database={database}, user={user}, schema={schema}")

            # Create engine with schema if provided
            if schema:
                engine = create_engine(
                    connection_string,
                    connect_args={'options': f'-c search_path={schema}'}
                )
                logger.info(f"Using schema: {schema}")
            else:
                engine = create_engine(connection_string)
                logger.info("No schema specified, using default schema")
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
                                 sample_rows_in_table_info: int = 3, schema: Optional[str] = None) -> Optional[SQLDatabase]:
    """
    Create a LangChain SQLDatabase from a SQLAlchemy engine.

    Args:
        engine: SQLAlchemy engine
        include_tables: Optional list of tables to include (if None, all tables are included)
        sample_rows_in_table_info: Number of sample rows to include in table info
        schema: Optional database schema to use

    Returns:
        Optional[SQLDatabase]: LangChain SQLDatabase or None if creation fails
    """
    try:
        # Log the tables in the database before creating SQLDatabase
        from sqlalchemy import inspect
        inspector = inspect(engine)

        # Get all schemas
        schemas = inspector.get_schema_names()
        logger.info(f"Available schemas: {schemas}")

        # Get tables in the specified schema or default schema
        if schema and schema in schemas:
            tables = inspector.get_table_names(schema=schema)
            logger.info(f"Tables in schema '{schema}': {tables}")
        else:
            tables = inspector.get_table_names()
            logger.info(f"Tables in default schema: {tables}")

        # Create SQLDatabase with schema if provided
        if schema:
            db = SQLDatabase(
                engine=engine,
                include_tables=include_tables,
                sample_rows_in_table_info=sample_rows_in_table_info,
                schema=schema
            )
            logger.info(f"Created LangChain SQLDatabase with schema: {schema}")
        else:
            db = SQLDatabase(
                engine=engine,
                include_tables=include_tables,
                sample_rows_in_table_info=sample_rows_in_table_info
            )
            logger.info("Created LangChain SQLDatabase with default schema")

        return db
    except Exception as e:
        logger.error(f"Error creating LangChain SQLDatabase: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
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
        logger.info(f"Initializing SQL agent with LLM type: {type(llm).__name__}")

        # Create a toolkit with the database
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        logger.info(f"Created SQL toolkit: {type(toolkit).__name__}")

        # Create the SQL agent with a more compatible agent type
        agent = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=verbose,
            agent_type="zero-shot-react-description",  # More compatible with various LLMs
            max_iterations=settings.AGENT_MAX_ITERATIONS,
            max_execution_time=settings.AGENT_MAX_EXECUTION_TIME,
            early_stopping_method=settings.AGENT_EARLY_STOPPING_METHOD
        )

        # Log the agent configuration for debugging
        logger.info(f"SQL agent configured with max_iterations={settings.AGENT_MAX_ITERATIONS}, " +
                   f"max_execution_time={settings.AGENT_MAX_EXECUTION_TIME}, " +
                   f"early_stopping_method={settings.AGENT_EARLY_STOPPING_METHOD}")

        logger.info(f"SQL agent initialized successfully: {type(agent).__name__}")
        return agent
    except Exception as e:
        logger.error(f"Error initializing SQL agent: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
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


def get_table_names(engine: Any, schema: Optional[str] = None) -> List[str]:
    """
    Get a list of table names from the database.

    Args:
        engine: SQLAlchemy engine
        schema: Optional schema name to get tables from

    Returns:
        List[str]: List of table names
    """
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)

        # Get all schemas
        schemas = inspector.get_schema_names()
        logger.info(f"Available schemas: {schemas}")

        # Get tables from specified schema or default
        if schema and schema in schemas:
            tables = inspector.get_table_names(schema=schema)
            logger.info(f"Tables in schema '{schema}': {tables}")
            return tables
        else:
            # If no schema specified or schema not found, try all schemas
            all_tables = []
            for schema_name in schemas:
                schema_tables = inspector.get_table_names(schema=schema_name)
                logger.info(f"Tables in schema '{schema_name}': {schema_tables}")
                all_tables.extend(schema_tables)

            # Also get tables without schema specification
            default_tables = inspector.get_table_names()
            logger.info(f"Tables in default schema: {default_tables}")

            # Combine and deduplicate
            all_tables.extend(default_tables)
            return list(set(all_tables))
    except Exception as e:
        logger.error(f"Error getting table names: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
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
        logger.info(f"Processing SQL query: {query}")
        logger.info(f"Agent type: {type(agent).__name__}")

        # Log agent configuration if available
        if hasattr(agent, 'max_iterations'):
            logger.info(f"Agent max_iterations: {agent.max_iterations}")
        if hasattr(agent, 'max_execution_time'):
            logger.info(f"Agent max_execution_time: {agent.max_execution_time}")

        # Start timing the query execution
        import time
        start_time = time.time()

        # Invoke the agent with the query
        result = agent.invoke({"input": query})

        # Calculate and log execution time
        execution_time = time.time() - start_time
        logger.info(f"Query processed successfully in {execution_time:.2f} seconds")

        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error processing SQL query with agent: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Exception details: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "error": f"Error processing query: {str(e)}"}


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
