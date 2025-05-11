"""
Data Analysis Agent - Utility Functions

This module contains utility functions for the Data Analysis Agent.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text
import streamlit as st
from typing import Dict, Any, Optional, List, Tuple


def load_csv_file(file) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.
    
    Args:
        file: The uploaded file object from Streamlit
        
    Returns:
        pd.DataFrame: The loaded DataFrame
    """
    try:
        df = pd.read_csv(file)
        return df
    except Exception as e:
        st.error(f"Error loading CSV file: {str(e)}")
        return pd.DataFrame()


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


def create_visualization(df: pd.DataFrame, viz_type: str, **kwargs) -> Optional[plt.Figure]:
    """
    Create a visualization using matplotlib/seaborn.
    
    Args:
        df: The pandas DataFrame
        viz_type: Type of visualization (e.g., 'bar', 'line', 'scatter', 'histogram')
        **kwargs: Visualization parameters
        
    Returns:
        Optional[plt.Figure]: Matplotlib figure or None if visualization fails
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if viz_type == 'bar':
            x = kwargs.get('x')
            y = kwargs.get('y')
            if x and y and x in df.columns and y in df.columns:
                sns.barplot(data=df, x=x, y=y, ax=ax)
            else:
                st.error(f"Invalid columns for bar chart: {x}, {y}")
                return None
                
        elif viz_type == 'line':
            x = kwargs.get('x')
            y = kwargs.get('y')
            if x and y and x in df.columns and y in df.columns:
                sns.lineplot(data=df, x=x, y=y, ax=ax)
            else:
                st.error(f"Invalid columns for line chart: {x}, {y}")
                return None
                
        elif viz_type == 'scatter':
            x = kwargs.get('x')
            y = kwargs.get('y')
            if x and y and x in df.columns and y in df.columns:
                sns.scatterplot(data=df, x=x, y=y, ax=ax)
            else:
                st.error(f"Invalid columns for scatter plot: {x}, {y}")
                return None
                
        elif viz_type == 'histogram':
            column = kwargs.get('column')
            if column and column in df.columns:
                sns.histplot(data=df, x=column, ax=ax)
            else:
                st.error(f"Invalid column for histogram: {column}")
                return None
                
        else:
            st.error(f"Unsupported visualization type: {viz_type}")
            return None
        
        plt.tight_layout()
        return fig
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")
        return None
