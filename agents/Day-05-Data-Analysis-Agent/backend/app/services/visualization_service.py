"""
Data Analysis Agent - Visualization Service

This module provides functionality for creating data visualizations.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import re
import ast
import inspect
import logging
import json
import base64
from io import BytesIO
from typing import Optional, Tuple, Dict, Any, List

# Set up logging
logger = logging.getLogger(__name__)


def create_plotly_visualization(df: pd.DataFrame, viz_type: str, **kwargs) -> Optional[Dict[str, Any]]:
    """
    Create a visualization using Plotly.

    Args:
        df: The pandas DataFrame
        viz_type: Type of visualization (e.g., 'bar', 'line', 'scatter', 'histogram')
        **kwargs: Visualization parameters

    Returns:
        Optional[Dict[str, Any]]: Plotly figure as JSON or None if visualization fails
    """
    try:
        logger.info(f"Creating {viz_type} visualization with parameters: {kwargs}")

        if viz_type == 'bar':
            x = kwargs.get('x')
            y = kwargs.get('y')
            if x and y and x in df.columns and y in df.columns:
                # Group by x column and aggregate y column if x is categorical and y is numeric
                if pd.api.types.is_object_dtype(df[x]) and pd.api.types.is_numeric_dtype(df[y]):
                    logger.info(f"Grouping data for bar chart with categorical x={x} and numeric y={y}")
                    grouped_df = df.groupby(x)[y].sum().reset_index().sort_values(y, ascending=False)
                    fig = px.bar(grouped_df, x=x, y=y, title=f"{y} by {x}")
                else:
                    fig = px.bar(df, x=x, y=y, title=f"{y} by {x}")
            else:
                logger.error(f"Invalid columns for bar chart: {x}, {y}")
                return None

        elif viz_type == 'line':
            x = kwargs.get('x')
            y = kwargs.get('y')
            if x and y and x in df.columns and y in df.columns:
                # Group by x column and aggregate y column for better line charts
                if pd.api.types.is_object_dtype(df[x]) and pd.api.types.is_numeric_dtype(df[y]):
                    logger.info(f"Grouping data for line chart with categorical x={x} and numeric y={y}")
                    grouped_df = df.groupby(x)[y].sum().reset_index().sort_values(y, ascending=False)
                    fig = px.line(grouped_df, x=x, y=y, title=f"{y} by {x}", markers=True)
                else:
                    # Use the data as is
                    fig = px.line(df, x=x, y=y, title=f"{y} over {x}", markers=True)

                # Add markers to make the line chart more readable
                fig.update_traces(mode='lines+markers')
            else:
                logger.error(f"Invalid columns for line chart: {x}, {y}")
                return None

        elif viz_type == 'scatter':
            x = kwargs.get('x')
            y = kwargs.get('y')
            color = kwargs.get('color')
            size = kwargs.get('size')

            if x and y and x in df.columns and y in df.columns:
                # Create scatter plot with optional color and size parameters
                scatter_args = {
                    'x': x,
                    'y': y,
                    'title': f"Relationship between {x} and {y}"
                }

                # Add color dimension if provided
                if color and color in df.columns:
                    scatter_args['color'] = color
                    scatter_args['title'] = f"Relationship between {x} and {y} (colored by {color})"

                # Add size dimension if provided
                if size and size in df.columns and pd.api.types.is_numeric_dtype(df[size]):
                    scatter_args['size'] = size
                    scatter_args['title'] = f"Relationship between {x} and {y} (sized by {size})"

                fig = px.scatter(df, **scatter_args)
            else:
                logger.error(f"Invalid columns for scatter plot: {x}, {y}")
                return None

        elif viz_type == 'histogram':
            column = kwargs.get('column')
            bins = kwargs.get('bins', 30)  # Default to 30 bins

            if column and column in df.columns:
                if pd.api.types.is_numeric_dtype(df[column]):
                    fig = px.histogram(df, x=column, nbins=bins, title=f"Distribution of {column}")
                else:
                    # For categorical columns, create a count plot
                    value_counts = df[column].value_counts().sort_values(ascending=False)
                    fig = px.bar(
                        x=value_counts.index,
                        y=value_counts.values,
                        title=f"Distribution of {column}"
                    )
            else:
                logger.error(f"Invalid column for histogram: {column}")
                return None

        elif viz_type == 'heatmap':
            # For correlation heatmap
            if df.select_dtypes(include=['number']).shape[1] >= 2:
                corr = df.select_dtypes(include=['number']).corr()
                fig = go.Figure(data=go.Heatmap(
                    z=corr.values,
                    x=corr.columns,
                    y=corr.columns,
                    colorscale='RdBu_r',
                    zmin=-1, zmax=1
                ))
                fig.update_layout(title="Correlation Heatmap")
            else:
                logger.error("Not enough numeric columns for a correlation heatmap")
                return None

        elif viz_type == 'boxplot':
            column = kwargs.get('column')
            group = kwargs.get('group')

            if column and column in df.columns:
                if group and group in df.columns:
                    # Create grouped boxplot
                    fig = px.box(df, y=column, x=group, title=f"Box Plot of {column} by {group}")
                else:
                    # Create simple boxplot
                    fig = px.box(df, y=column, title=f"Box Plot of {column}")
            else:
                logger.error(f"Invalid column for boxplot: {column}")
                return None

        elif viz_type == 'pie':
            column = kwargs.get('column')

            if column and column in df.columns:
                value_counts = df[column].value_counts()
                fig = px.pie(
                    values=value_counts.values,
                    names=value_counts.index,
                    title=f"Distribution of {column}"
                )
            else:
                logger.error(f"Invalid column for pie chart: {column}")
                return None

        elif viz_type == 'area':
            x = kwargs.get('x')
            y = kwargs.get('y')

            if x and y and x in df.columns and y in df.columns:
                # Group by x column and aggregate y column if needed
                if pd.api.types.is_object_dtype(df[x]) and pd.api.types.is_numeric_dtype(df[y]):
                    grouped_df = df.groupby(x)[y].sum().reset_index().sort_values(x)
                    fig = px.area(grouped_df, x=x, y=y, title=f"{y} by {x}")
                else:
                    # Sort by x for better area charts
                    sorted_df = df.sort_values(x)
                    fig = px.area(sorted_df, x=x, y=y, title=f"{y} by {x}")
            else:
                logger.error(f"Invalid columns for area chart: {x}, {y}")
                return None

        elif viz_type == 'violin':
            column = kwargs.get('column')
            group = kwargs.get('group')

            if column and column in df.columns and pd.api.types.is_numeric_dtype(df[column]):
                if group and group in df.columns:
                    # Create grouped violin plot
                    fig = px.violin(df, y=column, x=group, box=True, title=f"Violin Plot of {column} by {group}")
                else:
                    # Create simple violin plot
                    fig = px.violin(df, y=column, box=True, title=f"Violin Plot of {column}")
            else:
                logger.error(f"Invalid column for violin plot: {column}")
                return None

        elif viz_type == 'bubble':
            x = kwargs.get('x')
            y = kwargs.get('y')
            size = kwargs.get('size')
            color = kwargs.get('color')

            if x and y and size and x in df.columns and y in df.columns and size in df.columns:
                bubble_args = {
                    'x': x,
                    'y': y,
                    'size': size,
                    'title': f"Bubble Chart of {y} vs {x} (sized by {size})"
                }

                # Add color dimension if provided
                if color and color in df.columns:
                    bubble_args['color'] = color
                    bubble_args['title'] = f"Bubble Chart of {y} vs {x} (sized by {size}, colored by {color})"

                fig = px.scatter(df, **bubble_args)
            else:
                logger.error(f"Invalid columns for bubble chart: x={x}, y={y}, size={size}")
                return None

        elif viz_type == 'sunburst':
            path = kwargs.get('path')
            values = kwargs.get('values')

            if path and isinstance(path, list) and all(col in df.columns for col in path):
                sunburst_args = {
                    'path': path,
                    'title': f"Sunburst Chart of {', '.join(path)}"
                }

                if values and values in df.columns and pd.api.types.is_numeric_dtype(df[values]):
                    sunburst_args['values'] = values
                    sunburst_args['title'] = f"Sunburst Chart of {', '.join(path)} (values: {values})"

                fig = px.sunburst(df, **sunburst_args)
            else:
                logger.error(f"Invalid path for sunburst chart: {path}")
                return None

        else:
            logger.error(f"Unsupported visualization type: {viz_type}")
            return None

        # Update layout for better appearance
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40),
            height=500,  # Set a fixed height
            width=800    # Set a fixed width that will be responsive
        )

        # Convert to JSON
        return json.loads(fig.to_json())
    except Exception as e:
        logger.error(f"Error creating visualization: {str(e)}")
        import traceback
        logger.error(f"Visualization error traceback: {traceback.format_exc()}")
        return None


def create_fallback_visualization(df: pd.DataFrame, query: str) -> Optional[Dict[str, Any]]:
    """
    Create a fallback visualization when the LLM-generated code fails.
    This function creates a simple visualization based on the DataFrame structure and query.

    Args:
        df: The DataFrame to visualize
        query: The user's query (used to determine visualization type)

    Returns:
        Optional[Dict[str, Any]]: Plotly figure as JSON or None if visualization fails
    """
    try:
        logger.info(f"Creating fallback visualization for query: {query}")
        logger.info(f"DataFrame shape: {df.shape}, columns: {df.columns.tolist()}")

        # Check for specific visualization requests in the query
        bar_chart_keywords = ["bar chart", "bar graph", "column chart", "bar plot"]
        line_chart_keywords = ["line chart", "line graph", "trend", "line plot", "time series"]
        scatter_plot_keywords = ["scatter", "relationship", "correlation", "scatter plot", "scatter chart"]
        histogram_keywords = ["histogram", "distribution", "frequency distribution"]
        pie_chart_keywords = ["pie chart", "pie graph", "proportion", "percentage breakdown"]
        box_plot_keywords = ["box plot", "boxplot", "box chart", "box and whisker"]
        heatmap_keywords = ["heatmap", "heat map", "correlation matrix", "correlation heatmap"]
        area_chart_keywords = ["area chart", "area graph", "area plot", "stacked area"]
        violin_plot_keywords = ["violin plot", "violin chart", "distribution comparison"]
        bubble_chart_keywords = ["bubble chart", "bubble plot", "bubble graph"]
        sunburst_keywords = ["sunburst", "sunburst chart", "hierarchical", "hierarchy"]

        # Extract potential column names from the query
        query_words = set(query.lower().split())
        column_matches = []

        # First, check for common column names that might be mentioned in the query
        common_x_columns = ["state", "country", "region", "city", "date", "month", "year", "category", "product"]
        common_y_columns = ["total", "count", "sum", "amount", "value", "sales", "revenue", "profit", "number"]

        # Check if any common column patterns are in the query
        x_axis_indicators = ["x axis", "x-axis", "horizontal axis"]
        y_axis_indicators = ["y axis", "y-axis", "vertical axis"]

        # Look for explicit axis mentions in the query
        x_column_candidates = []
        y_column_candidates = []

        # Check for explicit mentions of columns for x and y axes
        for indicator in x_axis_indicators:
            if indicator in query.lower():
                # Find what comes after the indicator
                parts = query.lower().split(indicator)
                if len(parts) > 1:
                    # Extract words after the indicator
                    after_indicator = parts[1].strip()
                    words = after_indicator.split()
                    # Look for column names in the next few words
                    for col in df.columns:
                        col_lower = col.lower()
                        if any(col_lower in word for word in words[:5]):
                            x_column_candidates.append(col)
                            break

        for indicator in y_axis_indicators:
            if indicator in query.lower():
                # Find what comes after the indicator
                parts = query.lower().split(indicator)
                if len(parts) > 1:
                    # Extract words after the indicator
                    after_indicator = parts[1].strip()
                    words = after_indicator.split()
                    # Look for column names in the next few words
                    for col in df.columns:
                        col_lower = col.lower()
                        if any(col_lower in word for word in words[:5]):
                            y_column_candidates.append(col)
                            break

        # If we found explicit axis columns, use them
        if x_column_candidates and y_column_candidates:
            logger.info(f"Found explicit axis columns - x: {x_column_candidates[0]}, y: {y_column_candidates[0]}")
            return create_plotly_visualization(df, "bar", x=x_column_candidates[0], y=y_column_candidates[0])

        # Check for common column patterns
        for col in df.columns:
            # Check if column name appears in the query (case-insensitive)
            col_lower = col.lower()
            if col_lower in query.lower():
                column_matches.append(col)
            # Also check individual words in column name
            elif any(word in query_words for word in col_lower.split()):
                column_matches.append(col)

        # Look for common column names in the DataFrame
        x_col = None
        y_col = None

        # First, try to find a categorical column for x-axis and numeric column for y-axis
        categorical_cols = df.select_dtypes(include=['object']).columns
        numeric_cols = df.select_dtypes(include=['number']).columns

        # If "total" is in numeric columns, it's likely to be the y-axis for many queries
        if "total" in numeric_cols and any(word in query.lower() for word in ["total", "sum", "count"]):
            y_col = "total"
            logger.info(f"Selected 'total' as y-axis column based on query")

        # If "state_name" is in categorical columns, it's likely to be the x-axis for state-based queries
        if "state_name" in categorical_cols and any(word in query.lower() for word in ["state", "states"]):
            x_col = "state_name"
            logger.info(f"Selected 'state_name' as x-axis column based on query")

        # If we've identified both columns, create the visualization
        if x_col and y_col:
            # Determine the visualization type based on the query
            viz_type = "bar"  # Default to bar chart

            # Check for line chart request
            if any(keyword in query.lower() for keyword in ["line chart", "line graph", "trend", "line plot"]):
                viz_type = "line"
                logger.info(f"Line chart requested in query")

            logger.info(f"Creating {viz_type} visualization with x={x_col}, y={y_col}")
            return create_plotly_visualization(df, viz_type, x=x_col, y=y_col)

        logger.info(f"Potential columns from query: {column_matches}")

        # Try to identify what kind of visualization is needed
        if any(keyword in query.lower() for keyword in bar_chart_keywords):
            # Bar chart requested
            if len(column_matches) >= 2:
                # If we have at least two columns mentioned, use them for x and y
                x_col = column_matches[0]
                y_col = column_matches[1]

                # Check if the columns exist and y is numeric
                if x_col in df.columns and y_col in df.columns and pd.api.types.is_numeric_dtype(df[y_col]):
                    # Group by the x column and aggregate the y column
                    grouped_df = df.groupby(x_col)[y_col].sum().reset_index()
                    fig = px.bar(grouped_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                    logger.info(f"Created bar chart with x={x_col}, y={y_col}")
                else:
                    # If columns don't exist or y is not numeric, fall back to default
                    logger.info("Columns not suitable for bar chart, using fallback")
                    return _create_default_visualization(df)
            else:
                # If no specific columns mentioned, try to create a meaningful bar chart
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns
                numeric_cols = df.select_dtypes(include=['number']).columns

                # For state-based queries, look for state columns
                if "state" in query.lower():
                    state_cols = [col for col in categorical_cols if "state" in col.lower()]
                    if state_cols and "total" in numeric_cols:
                        x_col = state_cols[0]
                        y_col = "total"
                        logger.info(f"State query detected. Using x={x_col}, y={y_col}")
                        grouped_df = df.groupby(x_col)[y_col].sum().reset_index()
                        fig = px.bar(grouped_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                        return json.loads(fig.to_json())

                if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                    # Use first categorical column for x and first numeric for y
                    x_col = categorical_cols[0]

                    # Prefer 'total' column if available for y-axis
                    if 'total' in numeric_cols:
                        y_col = 'total'
                    else:
                        y_col = numeric_cols[0]

                    # Group by the categorical column and sum the numeric column
                    grouped_df = df.groupby(x_col)[y_col].sum().reset_index()
                    fig = px.bar(grouped_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                    logger.info(f"Created default bar chart with x={x_col}, y={y_col}")
                else:
                    # If no suitable columns, fall back to default
                    logger.info("No suitable columns for bar chart, using fallback")
                    return _create_default_visualization(df)

        elif any(keyword in query.lower() for keyword in line_chart_keywords):
            # Line chart requested
            logger.info("Line chart requested in query")

            # For state-based queries, look for state columns
            if "state" in query.lower():
                state_cols = [col for col in df.select_dtypes(include=['object']).columns if "state" in col.lower()]
                if state_cols and "total" in df.select_dtypes(include=['number']).columns:
                    x_col = state_cols[0]
                    y_col = "total"
                    logger.info(f"State query detected. Using x={x_col}, y={y_col} for line chart")

                    # Group by state and sum totals
                    grouped_df = df.groupby(x_col)[y_col].sum().reset_index().sort_values(y_col, ascending=False)
                    fig = px.line(grouped_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}", markers=True)
                    return json.loads(fig.to_json())

            if len(column_matches) >= 2:
                x_col = column_matches[0]
                y_col = column_matches[1]

                if x_col in df.columns and y_col in df.columns and pd.api.types.is_numeric_dtype(df[y_col]):
                    # Group by x column and aggregate y column
                    grouped_df = df.groupby(x_col)[y_col].sum().reset_index()
                    fig = px.line(grouped_df, x=x_col, y=y_col, title=f"{y_col} over {x_col}", markers=True)
                    logger.info(f"Created line chart with x={x_col}, y={y_col}")
                else:
                    logger.info("Columns not suitable for line chart, using fallback")
                    return _create_default_visualization(df)
            else:
                # Try to find a date/time column for x-axis
                date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
                numeric_cols = df.select_dtypes(include=['number']).columns
                categorical_cols = df.select_dtypes(include=['object']).columns

                # For state-based queries, use state_name and total
                if "state" in query.lower() and "state_name" in categorical_cols and "total" in numeric_cols:
                    x_col = "state_name"
                    y_col = "total"
                    grouped_df = df.groupby(x_col)[y_col].sum().reset_index().sort_values(y_col, ascending=False)
                    fig = px.line(grouped_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}", markers=True)
                    logger.info(f"Created line chart with state_name and total")
                    return json.loads(fig.to_json())
                elif len(date_cols) > 0 and len(numeric_cols) > 0:
                    x_col = date_cols[0]
                    y_col = numeric_cols[0]
                    fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}", markers=True)
                    logger.info(f"Created default line chart with x={x_col}, y={y_col}")
                else:
                    logger.info("No suitable columns for line chart, using fallback")
                    return _create_default_visualization(df)

        elif any(keyword in query.lower() for keyword in scatter_plot_keywords):
            # Scatter plot requested
            if len(column_matches) >= 2:
                x_col = column_matches[0]
                y_col = column_matches[1]

                if (x_col in df.columns and y_col in df.columns and
                    pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col])):
                    fig = px.scatter(df, x=x_col, y=y_col, title=f"Relationship between {x_col} and {y_col}")
                    logger.info(f"Created scatter plot with x={x_col}, y={y_col}")
                else:
                    logger.info("Columns not suitable for scatter plot, using fallback")
                    return _create_default_visualization(df)
            else:
                # Find two numeric columns for scatter plot
                numeric_cols = df.select_dtypes(include=['number']).columns

                if len(numeric_cols) >= 2:
                    x_col = numeric_cols[0]
                    y_col = numeric_cols[1]
                    fig = px.scatter(df, x=x_col, y=y_col, title=f"Relationship between {x_col} and {y_col}")
                    logger.info(f"Created default scatter plot with x={x_col}, y={y_col}")
                else:
                    logger.info("No suitable columns for scatter plot, using fallback")
                    return _create_default_visualization(df)

        elif any(keyword in query.lower() for keyword in histogram_keywords):
            # Histogram requested
            if len(column_matches) >= 1:
                col = column_matches[0]

                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    fig = px.histogram(df, x=col, title=f"Distribution of {col}")
                    logger.info(f"Created histogram for column {col}")
                else:
                    logger.info("Column not suitable for histogram, using fallback")
                    return _create_default_visualization(df)
            else:
                # Find a numeric column for histogram
                numeric_cols = df.select_dtypes(include=['number']).columns

                if len(numeric_cols) >= 1:
                    col = numeric_cols[0]
                    fig = px.histogram(df, x=col, title=f"Distribution of {col}")
                    logger.info(f"Created default histogram for column {col}")
                else:
                    logger.info("No suitable columns for histogram, using fallback")
                    return _create_default_visualization(df)

        elif any(keyword in query.lower() for keyword in pie_chart_keywords):
            # Pie chart requested
            if len(column_matches) >= 1:
                col = column_matches[0]

                if col in df.columns:
                    value_counts = df[col].value_counts()
                    fig = px.pie(values=value_counts.values, names=value_counts.index, title=f"Distribution of {col}")
                    logger.info(f"Created pie chart for column {col}")
                else:
                    logger.info("Column not found for pie chart, using fallback")
                    return _create_default_visualization(df)
            else:
                # Find a categorical column for pie chart
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns

                if len(categorical_cols) >= 1:
                    col = categorical_cols[0]
                    value_counts = df[col].value_counts()
                    fig = px.pie(values=value_counts.values, names=value_counts.index, title=f"Distribution of {col}")
                    logger.info(f"Created default pie chart for column {col}")
                else:
                    logger.info("No suitable columns for pie chart, using fallback")
                    return _create_default_visualization(df)

        elif any(keyword in query.lower() for keyword in box_plot_keywords):
            # Box plot requested
            if len(column_matches) >= 1:
                col = column_matches[0]

                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    # Check if there's a potential grouping column
                    group_col = None
                    if len(column_matches) >= 2:
                        potential_group = column_matches[1]
                        if potential_group in df.columns and not pd.api.types.is_numeric_dtype(df[potential_group]):
                            group_col = potential_group

                    if group_col:
                        fig = px.box(df, y=col, x=group_col, title=f"Box Plot of {col} by {group_col}")
                    else:
                        fig = px.box(df, y=col, title=f"Box Plot of {col}")

                    logger.info(f"Created boxplot for column {col}")
                else:
                    logger.info("Column not suitable for boxplot, using fallback")
                    return _create_default_visualization(df)
            else:
                # Find a numeric column for boxplot
                numeric_cols = df.select_dtypes(include=['number']).columns

                if len(numeric_cols) >= 1:
                    col = numeric_cols[0]
                    fig = px.box(df, y=col, title=f"Box Plot of {col}")
                    logger.info(f"Created default boxplot for column {col}")
                else:
                    logger.info("No suitable columns for boxplot, using fallback")
                    return _create_default_visualization(df)

        elif any(keyword in query.lower() for keyword in heatmap_keywords):
            # Heatmap requested
            numeric_cols = df.select_dtypes(include=['number']).columns

            if len(numeric_cols) >= 2:
                # Create correlation heatmap
                corr = df[numeric_cols].corr()
                fig = go.Figure(data=go.Heatmap(
                    z=corr.values,
                    x=corr.columns,
                    y=corr.columns,
                    colorscale='RdBu_r',
                    zmin=-1, zmax=1
                ))
                fig.update_layout(title="Correlation Heatmap")
                logger.info(f"Created correlation heatmap with {len(numeric_cols)} numeric columns")
            else:
                logger.info("Not enough numeric columns for heatmap, using fallback")
                return _create_default_visualization(df)

        elif any(keyword in query.lower() for keyword in area_chart_keywords):
            # Area chart requested
            if len(column_matches) >= 2:
                x_col = column_matches[0]
                y_col = column_matches[1]

                if x_col in df.columns and y_col in df.columns and pd.api.types.is_numeric_dtype(df[y_col]):
                    # Group by x column and aggregate y column if needed
                    if pd.api.types.is_object_dtype(df[x_col]):
                        grouped_df = df.groupby(x_col)[y_col].sum().reset_index().sort_values(x_col)
                        fig = px.area(grouped_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                    else:
                        # Sort by x for better area charts
                        sorted_df = df.sort_values(x_col)
                        fig = px.area(sorted_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")

                    logger.info(f"Created area chart with x={x_col}, y={y_col}")
                else:
                    logger.info("Columns not suitable for area chart, using fallback")
                    return _create_default_visualization(df)
            else:
                # Try to find suitable columns
                date_cols = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
                numeric_cols = df.select_dtypes(include=['number']).columns

                if len(date_cols) > 0 and len(numeric_cols) > 0:
                    x_col = date_cols[0]
                    y_col = numeric_cols[0]
                    sorted_df = df.sort_values(x_col)
                    fig = px.area(sorted_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                    logger.info(f"Created default area chart with x={x_col}, y={y_col}")
                else:
                    logger.info("No suitable columns for area chart, using fallback")
                    return _create_default_visualization(df)

        elif any(keyword in query.lower() for keyword in violin_plot_keywords):
            # Violin plot requested
            if len(column_matches) >= 1:
                col = column_matches[0]

                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    # Check if there's a potential grouping column
                    group_col = None
                    if len(column_matches) >= 2:
                        potential_group = column_matches[1]
                        if potential_group in df.columns and not pd.api.types.is_numeric_dtype(df[potential_group]):
                            group_col = potential_group

                    if group_col:
                        fig = px.violin(df, y=col, x=group_col, box=True, title=f"Violin Plot of {col} by {group_col}")
                    else:
                        fig = px.violin(df, y=col, box=True, title=f"Violin Plot of {col}")

                    logger.info(f"Created violin plot for column {col}")
                else:
                    logger.info("Column not suitable for violin plot, using fallback")
                    return _create_default_visualization(df)
            else:
                # Find a numeric column for violin plot
                numeric_cols = df.select_dtypes(include=['number']).columns

                if len(numeric_cols) >= 1:
                    col = numeric_cols[0]
                    fig = px.violin(df, y=col, box=True, title=f"Violin Plot of {col}")
                    logger.info(f"Created default violin plot for column {col}")
                else:
                    logger.info("No suitable columns for violin plot, using fallback")
                    return _create_default_visualization(df)

        elif any(keyword in query.lower() for keyword in bubble_chart_keywords):
            # Bubble chart requested
            numeric_cols = df.select_dtypes(include=['number']).columns

            if len(numeric_cols) >= 3:
                x_col = numeric_cols[0]
                y_col = numeric_cols[1]
                size_col = numeric_cols[2]

                # Check if there's a potential color column
                color_col = None
                if len(column_matches) >= 1:
                    for col in column_matches:
                        if col in df.columns and col not in [x_col, y_col, size_col]:
                            color_col = col
                            break

                bubble_args = {
                    'x': x_col,
                    'y': y_col,
                    'size': size_col,
                    'title': f"Bubble Chart of {y_col} vs {x_col} (sized by {size_col})"
                }

                if color_col:
                    bubble_args['color'] = color_col
                    bubble_args['title'] = f"Bubble Chart of {y_col} vs {x_col} (sized by {size_col}, colored by {color_col})"

                fig = px.scatter(df, **bubble_args)
                logger.info(f"Created bubble chart with x={x_col}, y={y_col}, size={size_col}")
            else:
                logger.info("Not enough numeric columns for bubble chart, using fallback")
                return _create_default_visualization(df)

        elif any(keyword in query.lower() for keyword in sunburst_keywords):
            # Sunburst chart requested
            categorical_cols = df.select_dtypes(include=['object']).columns
            numeric_cols = df.select_dtypes(include=['number']).columns

            if len(categorical_cols) >= 2 and len(numeric_cols) >= 1:
                path = categorical_cols[:2].tolist()  # Use first two categorical columns
                values = numeric_cols[0]  # Use first numeric column

                fig = px.sunburst(
                    df,
                    path=path,
                    values=values,
                    title=f"Sunburst Chart of {', '.join(path)} (values: {values})"
                )
                logger.info(f"Created sunburst chart with path={path}, values={values}")
            else:
                logger.info("Not enough suitable columns for sunburst chart, using fallback")
                return _create_default_visualization(df)

        else:
            # No specific visualization type detected, use default
            logger.info("No specific visualization type detected, using default")
            return _create_default_visualization(df)

        # Update layout for better appearance
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40)
        )

        # Convert to JSON
        return json.loads(fig.to_json())

    except Exception as e:
        logger.error(f"Failed to create fallback visualization: {str(e)}")
        return _create_default_visualization(df)


def _create_default_visualization(df: pd.DataFrame) -> Optional[Dict[str, Any]]:
    """
    Create a default visualization based on the DataFrame structure.

    Args:
        df: The DataFrame to visualize

    Returns:
        Optional[Dict[str, Any]]: Plotly figure as JSON or None if visualization fails
    """
    try:
        logger.info(f"Creating default visualization for DataFrame with shape {df.shape}")
        logger.info(f"DataFrame columns: {df.columns.tolist()}")
        logger.info(f"DataFrame dtypes: {df.dtypes.to_dict()}")

        # Check for state-related columns and total column - common in many datasets
        state_cols = [col for col in df.columns if "state" in col.lower()]
        if state_cols and "total" in df.columns:
            x_col = state_cols[0]
            y_col = "total"
            logger.info(f"Found state column and total column. Using x={x_col}, y={y_col}")

            # Group by state and sum totals
            grouped_df = df.groupby(x_col)[y_col].sum().reset_index().sort_values(y_col, ascending=False)

            # Check if we're in a context where a line chart might be requested
            import inspect
            caller_frame = inspect.currentframe().f_back
            if caller_frame:
                caller_locals = caller_frame.f_locals
                if 'query' in caller_locals and isinstance(caller_locals['query'], str):
                    query = caller_locals['query'].lower()
                    if any(keyword in query for keyword in ["line chart", "line graph", "trend", "line plot"]):
                        logger.info(f"Line chart context detected in caller. Creating line chart.")
                        fig = px.line(grouped_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}", markers=True)
                        return json.loads(fig.to_json())

            # Default to bar chart
            fig = px.bar(grouped_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
            return json.loads(fig.to_json())

        # Determine the best visualization type based on the data structure
        if len(df.columns) == 2:
            x_col = df.columns[0]
            y_col = df.columns[1]

            logger.info(f"Two-column DataFrame detected. x_col={x_col}, y_col={y_col}")

            # Check if the second column is numeric (for bar charts/histograms)
            if pd.api.types.is_numeric_dtype(df[y_col]):
                # Create a bar chart
                logger.info(f"Creating bar chart with x={x_col}, y={y_col}")
                fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")

            # If both columns are numeric, create a scatter plot
            elif pd.api.types.is_numeric_dtype(df[x_col]) and pd.api.types.is_numeric_dtype(df[y_col]):
                logger.info(f"Creating scatter plot with x={x_col}, y={y_col}")
                fig = px.scatter(df, x=x_col, y=y_col, title=f"Relationship between {x_col} and {y_col}")

            # Otherwise, create a simple line chart
            else:
                logger.info(f"Creating line chart with x={x_col}, y={y_col}")
                fig = px.line(df, x=x_col, y=y_col, title=f"Trend of {y_col} by {x_col}")

        # For DataFrames with more columns, create a summary visualization
        else:
            # First, check for categorical and numeric columns
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns
            numeric_cols = df.select_dtypes(include=['number']).columns

            # If we have both categorical and numeric columns, create a grouped bar chart
            if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                # Use first categorical column for x and first numeric for y
                x_col = categorical_cols[0]

                # Prefer 'total' column if available for y-axis
                if 'total' in numeric_cols:
                    y_col = 'total'
                else:
                    y_col = numeric_cols[0]

                logger.info(f"Creating grouped bar chart with x={x_col}, y={y_col}")
                grouped_df = df.groupby(x_col)[y_col].sum().reset_index().sort_values(y_col, ascending=False)
                fig = px.bar(grouped_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                return json.loads(fig.to_json())

            # If we only have numeric columns, create a bar chart of means
            elif len(numeric_cols) > 0:
                # Create a bar chart of the mean of each numeric column
                means = df[numeric_cols].mean().sort_values(ascending=False)
                logger.info(f"Creating bar chart of means for numeric columns")
                fig = px.bar(
                    x=means.index,
                    y=means.values,
                    title="Average Values by Column"
                )
            else:
                # Create a count plot of the first categorical column
                first_col = df.columns[0]
                logger.info(f"No numeric columns found. Creating count plot for column {first_col}")
                value_counts = df[first_col].value_counts().sort_values(ascending=False).head(10)
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"Count of {first_col} Values"
                )

        # Update layout for better appearance
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40),
            height=500,  # Set a fixed height
            width=800    # Set a fixed width
        )

        # Log the figure data structure
        logger.info(f"Figure data structure: {list(fig.to_dict().keys())}")

        # Convert to JSON
        json_data = json.loads(fig.to_json())
        logger.info(f"JSON data structure: {list(json_data.keys())}")

        return json_data

    except Exception as e:
        logger.error(f"Failed to create default visualization: {str(e)}")
        import traceback
        logger.error(f"Default visualization error traceback: {traceback.format_exc()}")
        return None


def extract_code_from_response(response: str) -> str:
    """
    Extract Python code from an LLM response.

    Args:
        response: The LLM response text

    Returns:
        str: Extracted Python code or empty string if no code found
    """
    # Look for code blocks with Python syntax highlighting
    python_code_pattern = r"```(?:python)?\s*([\s\S]*?)```"
    matches = re.findall(python_code_pattern, response)

    if matches:
        return matches[0].strip()

    # If no code blocks found, try to find code without markers
    # This is a fallback and less reliable
    code_lines = []
    capture = False

    for line in response.split('\n'):
        if line.strip().startswith('import') or line.strip().startswith('from ') or line.strip().startswith('plt.') or line.strip().startswith('sns.'):
            capture = True

        if capture:
            code_lines.append(line)

    return '\n'.join(code_lines) if code_lines else ""


def is_safe_code(code: str) -> bool:
    """
    Check if the code is safe to execute.

    Args:
        code: The Python code to check

    Returns:
        bool: True if the code is safe, False otherwise
    """
    # List of allowed modules
    allowed_modules = {
        'pandas', 'matplotlib', 'seaborn', 'numpy', 'math',
        'plt', 'pd', 'sns', 'np', 'plotly', 'px', 'go'
    }

    # List of dangerous functions/statements
    dangerous_patterns = [
        'exec', 'eval', 'compile', 'open', 'file',
        '__import__', 'subprocess', 'os.', 'sys.',
        'shutil', 'requests', 'urllib', 'socket',
        'write', 'delete', 'remove', 'system'
    ]

    # Check for dangerous patterns
    for pattern in dangerous_patterns:
        if pattern in code:
            return False

    try:
        # Parse the code to check imports
        tree = ast.parse(code)

        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for name in node.names:
                    module_name = name.name.split('.')[0]
                    if module_name not in allowed_modules:
                        return False

            # Check function calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id not in allowed_modules and node.func.id not in ['print', 'len', 'range', 'enumerate', 'zip', 'min', 'max', 'sum', 'sorted', 'list', 'dict', 'set', 'tuple']:
                        # This is a simplistic check and might flag safe code
                        # For a production system, a more sophisticated check would be needed
                        pass

        return True
    except SyntaxError:
        # If the code has syntax errors, it's not safe to execute
        return False


def generate_visualization_prompt(query: str, df: pd.DataFrame) -> str:
    """
    Generate a prompt for the LLM to create visualization code.

    Args:
        query: The user's query
        df: The DataFrame to visualize

    Returns:
        str: The prompt for the LLM
    """
    # Get DataFrame info
    df_info = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "numeric_columns": list(df.select_dtypes(include=['number']).columns),
        "categorical_columns": list(df.select_dtypes(include=['object', 'category']).columns),
    }

    # Add sample data (first few rows)
    sample_data = df.head(3).to_string()

    # Determine the most appropriate visualization type based on the data structure
    viz_type = "auto"

    # Analyze the data structure to suggest an appropriate visualization type
    # This treats all visualization types equally without special cases

    # For count data with two columns, suggest a bar chart
    if len(df.columns) == 2 and df.dtypes.iloc[1].kind in 'iuf':
        viz_type = "bar"

    # For time series data, suggest a line chart
    date_cols = [col for col, dtype in df.dtypes.items() if 'date' in str(dtype).lower() or 'time' in str(dtype).lower()]
    if date_cols:
        viz_type = "line"

    # If the user explicitly requests a specific visualization type, use that
    chart_types = {
        "histogram": "histogram",
        "bar": "bar",
        "line": "line",
        "scatter": "scatter",
        "pie": "pie",
        "box": "box"
    }

    # Check if any chart type is mentioned in the query
    for chart_type, viz_value in chart_types.items():
        if chart_type in query.lower():
            viz_type = viz_value
            break

    prompt = f"""
You are a data visualization expert. Create Python code to visualize the following data based on the user's query.

USER QUERY: {query}

DATAFRAME INFORMATION:
- Shape: {df_info['shape']}
- Columns: {', '.join(df_info['columns'])}
- Numeric columns: {', '.join(df_info['numeric_columns'])}
- Categorical columns: {', '.join(df_info['categorical_columns'])}

SAMPLE DATA (first 3 rows):
{sample_data}

SUGGESTED VISUALIZATION TYPE: {viz_type}

INSTRUCTIONS:
1. Generate Python code using Plotly Express (px) to create a clear, professional visualization.
2. Use the variable 'df' which already contains the DataFrame.
3. Include necessary imports (import plotly.express as px, import plotly.graph_objects as go).
4. Add a descriptive title, axis labels, and legend if applicable.
5. Use appropriate colors and styling for a professional look.
6. Return ONLY the Python code within a code block (```python ... ```).
7. Make sure the code is complete and can run independently.
8. The code should return a Plotly figure object (fig) at the end.

IMPORTANT NOTES:
- Choose the most appropriate visualization type based on the data structure and the user's query.
- For categorical data with counts/frequencies, use bar charts (px.bar()).
- For numerical distributions, use histograms (px.histogram()) with appropriate bins.
- For time series data, use line charts (px.line()) with proper date formatting.
- For relationships between variables, use scatter plots (px.scatter()).
- For part-to-whole relationships, use pie charts (px.pie()).
- For comparing distributions, use box plots (px.box()).
- Use appropriate colors, legends, and grid lines to enhance readability.

Example response format:
```python
import plotly.express as px

# Create the visualization
fig = px.bar(df, x='column_name', y='another_column', title='Descriptive Title')

# Update layout for better appearance
fig.update_layout(
    xaxis_title='X Axis Label',
    yaxis_title='Y Axis Label',
    template='plotly_white'
)

# Return the figure
fig
```
"""
    return prompt
