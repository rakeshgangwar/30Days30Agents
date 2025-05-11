"""
Data Analysis Agent - CSV Handler Module

This module provides functionality for handling CSV files.
"""

import pandas as pd
import streamlit as st
from typing import Dict, Any


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


def display_dataframe_info(df: pd.DataFrame) -> None:
    """
    Display information about a DataFrame in the Streamlit UI.
    
    Args:
        df: The pandas DataFrame to display information about
    """
    if df.empty:
        st.error("DataFrame is empty")
        return
        
    # Get dataframe information
    info = get_dataframe_info(df)
    
    # Display data preview
    st.markdown("### Data Preview")
    st.dataframe(df.head(), use_container_width=True)
    
    # Display basic information
    st.markdown("### Data Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Rows:** {info['shape'][0]}")
        st.write(f"**Columns:** {info['shape'][1]}")
        
        if info['numeric_columns']:
            st.write(f"**Numeric columns:** {', '.join(info['numeric_columns'])}")
            
        if info['categorical_columns']:
            st.write(f"**Categorical columns:** {', '.join(info['categorical_columns'])}")
            
    with col2:
        # Display missing values if any
        missing_values = {k: v for k, v in info['missing_values'].items() if v > 0}
        if missing_values:
            st.write("**Missing values:**")
            for col, count in missing_values.items():
                st.write(f"- {col}: {count}")
        else:
            st.write("**No missing values found**")
