"""
Data Analysis Agent - UI Components

This module contains UI components for the Streamlit application.
"""

import streamlit as st
import pandas as pd
from typing import Any, Callable, Dict, List, Optional, Tuple

import sys
import os

# Add the parent directory to the Python path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config import settings


def setup_page_config():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title=settings.APP_TITLE,
        page_icon=settings.APP_ICON,
        layout=settings.APP_LAYOUT,
        initial_sidebar_state=settings.APP_INITIAL_SIDEBAR_STATE
    )


def render_header():
    """Render the application header."""
    st.title(f"{settings.APP_ICON} {settings.APP_TITLE}")
    st.markdown("""
    Upload your data and ask questions in natural language to analyze and visualize it.
    """)


def render_sidebar():
    """Render the sidebar with data source selection."""
    st.sidebar.title("Data Source")
    data_source = st.sidebar.radio(
        "Select Data Source",
        options=["CSV File", "SQL Database"],
        index=0
    )
    return data_source


def render_csv_upload_section():
    """
    Render the CSV file upload section.

    Returns:
        The uploaded file object or None
    """
    st.markdown("### Upload CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")

    return uploaded_file


def render_sql_connection_section():
    """
    Render the SQL database connection section.

    Returns:
        Tuple containing connection parameters
    """
    st.markdown("### Connect to SQL Database")

    # Database type selection
    db_type = st.selectbox(
        "Select Database Type",
        options=["SQLite", "PostgreSQL"],
        index=0
    )

    # Connection parameters based on database type
    if db_type == "SQLite":
        db_path = st.text_input("Database File Path", settings.DEFAULT_SQLITE_PATH)
        return db_type.lower(), {"db_path": db_path}
    else:
        # PostgreSQL connection parameters
        col1, col2 = st.columns(2)
        with col1:
            host = st.text_input("Host", "localhost")
            port = st.text_input("Port", "5432")
            database = st.text_input("Database Name")
        with col2:
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")

        return db_type.lower(), {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password
        }


def render_query_input_section():
    """
    Render the query input section.

    Returns:
        The query string and whether the analyze button was clicked
    """
    st.markdown("### Ask a question about your data")
    query = st.text_area(
        "Enter your query in natural language",
        height=100,
        placeholder="e.g., 'What is the average of column X?' or 'Show me a histogram of column Y'"
    )

    analyze_clicked = st.button("Analyze")

    return query, analyze_clicked


def render_results_section():
    """
    Create a container for query results.

    Returns:
        The results container
    """
    return st.container()


def render_error(error_message: str, show_details: bool = False, details: str = ""):
    """
    Render an error message.

    Args:
        error_message: The error message to display
        show_details: Whether to show detailed error information
        details: Detailed error information
    """
    st.error(error_message)

    if show_details and details:
        with st.expander("Error Details"):
            st.code(details)


def render_success(message: str):
    """
    Render a success message.

    Args:
        message: The success message to display
    """
    st.success(message)


def render_info(message: str):
    """
    Render an info message.

    Args:
        message: The info message to display
    """
    st.info(message)


def render_warning(message: str):
    """
    Render a warning message.

    Args:
        message: The warning message to display
    """
    st.warning(message)
