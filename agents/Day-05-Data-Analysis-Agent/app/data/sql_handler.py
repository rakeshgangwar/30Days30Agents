"""
Data Analysis Agent - SQL Handler Module

This module provides functionality for handling SQL databases.
"""

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from typing import Any, Optional, Tuple


def create_db_connection(db_type: str, **kwargs) -> Optional[Any]:
    """
    Create a database connection using SQLAlchemy.
    
    Args:
        db_type: The type of database ('sqlite' or 'postgresql')
        **kwargs: Connection parameters
        
    Returns:
        Optional[Any]: SQLAlchemy engine or None if connection fails
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
            st.error(f"Unsupported database type: {db_type}")
            return None
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        return engine
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
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


def get_table_names(engine: Any) -> list:
    """
    Get a list of table names from the database.
    
    Args:
        engine: SQLAlchemy engine
        
    Returns:
        list: List of table names
    """
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        return inspector.get_table_names()
    except Exception as e:
        st.error(f"Error getting table names: {str(e)}")
        return []


def get_table_schema(engine: Any, table_name: str) -> dict:
    """
    Get the schema for a specific table.
    
    Args:
        engine: SQLAlchemy engine
        table_name: Name of the table
        
    Returns:
        dict: Dictionary containing table schema information
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
                "default": column.get("default", None),
                "primary_key": column.get("primary_key", False)
            })
            
        return schema
    except Exception as e:
        st.error(f"Error getting table schema: {str(e)}")
        return {"error": str(e)}
