"""
Data Analysis Agent - Helper Utilities

This module contains utility functions for the Data Analysis Agent.
"""

import re
import pandas as pd
import streamlit as st
from typing import Any, Dict, List, Optional, Tuple


def extract_number_from_query(query: str) -> Optional[int]:
    """
    Extract a number from a query string.
    
    Args:
        query: The query string to extract a number from
        
    Returns:
        Optional[int]: The extracted number or None if no number is found
    """
    numbers = re.findall(r'\d+', query)
    if numbers:
        return int(numbers[0])
    return None


def detect_visualization_request(query: str) -> bool:
    """
    Detect if a query is requesting a visualization.
    
    Args:
        query: The query string to check
        
    Returns:
        bool: True if the query is requesting a visualization, False otherwise
    """
    visualization_terms = [
        "plot", "chart", "graph", "histogram", "visualize", "visualization",
        "show me", "display", "draw", "create", "generate", "bar chart",
        "line chart", "scatter plot", "heatmap", "boxplot", "pie chart"
    ]
    
    return any(term in query.lower() for term in visualization_terms)


def detect_query_type(query: str) -> str:
    """
    Detect the type of query being asked.
    
    Args:
        query: The query string to analyze
        
    Returns:
        str: The detected query type ('visualization', 'filter', 'statistics', 'general')
    """
    if detect_visualization_request(query):
        return 'visualization'
        
    filter_terms = [
        "filter", "where", "find", "show me", "display", "list", "get",
        "more than", "less than", "equal to", "greater than", "smaller than",
        "between", "contains", "starts with", "ends with"
    ]
    
    if any(term in query.lower() for term in filter_terms):
        return 'filter'
        
    statistics_terms = [
        "average", "mean", "median", "mode", "sum", "count", "maximum", "minimum",
        "max", "min", "standard deviation", "variance", "correlation", "stats",
        "statistics", "summarize", "summary", "describe"
    ]
    
    if any(term in query.lower() for term in statistics_terms):
        return 'statistics'
        
    return 'general'


def format_error_message(error: Exception) -> str:
    """
    Format an error message for display.
    
    Args:
        error: The exception to format
        
    Returns:
        str: Formatted error message with suggestions
    """
    error_str = str(error)
    
    # Check for common error types and provide helpful messages
    if "Connection" in error_str:
        return f"""
        Connection error: {error_str}
        
        This might be due to:
        1. Network connectivity issues
        2. OpenRouter API service unavailability
        3. API rate limits
        
        Try again in a few moments or check your API key configuration.
        """
    elif "Timeout" in error_str:
        return f"""
        Timeout error: {error_str}
        
        This might be due to:
        1. Complex query requiring more processing time
        2. Network latency
        3. Service overload
        
        Try simplifying your query or try again later.
        """
    elif "KeyError" in error_str or "NameError" in error_str:
        return f"""
        Reference error: {error_str}
        
        This might be due to:
        1. Referring to a column that doesn't exist
        2. Typo in column name
        3. Case sensitivity issues
        
        Check the column names in your data and try again.
        """
    else:
        return f"Error: {error_str}"
