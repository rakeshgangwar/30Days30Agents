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
    # Comprehensive list of visualization-related terms
    visualization_terms = [
        # Basic visualization terms
        "plot", "chart", "graph", "histogram", "visualize", "visualization",
        "show me", "display", "draw", "create", "generate",

        # Chart types
        "bar chart", "line chart", "scatter plot", "heatmap", "boxplot", "pie chart",
        "bar", "line", "scatter", "box", "pie", "area", "bubble", "radar",

        # Data analysis terms often associated with visualizations
        "distribution", "frequency", "count by", "grouped by", "breakdown",
        "trend", "pattern", "comparison", "relationship", "correlation",

        # Visual elements
        "visual", "figure", "diagram", "illustration", "picture", "image",

        # Action verbs often used with visualization requests
        "show", "illustrate", "depict", "represent", "demonstrate", "view"
    ]

    # Check if any visualization term is in the query
    query_lower = query.lower()

    # First check for exact terms
    if any(term in query_lower for term in visualization_terms):
        return True

    # Then check for common visualization phrases
    viz_phrases = [
        "show me a", "create a", "generate a", "make a", "produce a",
        "can you show", "can you create", "can you generate", "can you make",
        "would like to see", "want to see", "need to see",
        "visually represent", "visually show", "visually display"
    ]

    if any(phrase in query_lower for phrase in viz_phrases):
        return True

    # Check for distribution-related terms that often imply visualization
    distribution_terms = [
        "distribution", "spread", "range", "frequency", "occurrence",
        "how many", "count of", "number of", "by year", "by month", "by category",
        "by department", "by group", "by type", "by region", "by country"
    ]

    if any(term in query_lower for term in distribution_terms):
        return True

    return False


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
