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
        if viz_type == 'bar':
            x = kwargs.get('x')
            y = kwargs.get('y')
            if x and y and x in df.columns and y in df.columns:
                fig = px.bar(df, x=x, y=y, title=f"{y} by {x}")
            else:
                logger.error(f"Invalid columns for bar chart: {x}, {y}")
                return None

        elif viz_type == 'line':
            x = kwargs.get('x')
            y = kwargs.get('y')
            if x and y and x in df.columns and y in df.columns:
                fig = px.line(df, x=x, y=y, title=f"{y} over {x}")
            else:
                logger.error(f"Invalid columns for line chart: {x}, {y}")
                return None

        elif viz_type == 'scatter':
            x = kwargs.get('x')
            y = kwargs.get('y')
            if x and y and x in df.columns and y in df.columns:
                fig = px.scatter(df, x=x, y=y, title=f"Relationship between {x} and {y}")
            else:
                logger.error(f"Invalid columns for scatter plot: {x}, {y}")
                return None

        elif viz_type == 'histogram':
            column = kwargs.get('column')
            if column and column in df.columns:
                fig = px.histogram(df, x=column, title=f"Distribution of {column}")
            else:
                logger.error(f"Invalid column for histogram: {column}")
                return None

        elif viz_type == 'heatmap':
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
            if column and column in df.columns:
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

        else:
            logger.error(f"Unsupported visualization type: {viz_type}")
            return None

        # Update layout for better appearance
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40)
        )

        # Convert to JSON
        return json.loads(fig.to_json())
    except Exception as e:
        logger.error(f"Error creating visualization: {str(e)}")
        return None


def create_fallback_visualization(df: pd.DataFrame, query: str) -> Optional[Dict[str, Any]]:
    """
    Create a fallback visualization when the LLM-generated code fails.
    This function creates a simple visualization based on the DataFrame structure.

    Args:
        df: The DataFrame to visualize
        query: The user's query (used to determine visualization type)

    Returns:
        Optional[Dict[str, Any]]: Plotly figure as JSON or None if visualization fails
    """
    try:
        # Determine the best visualization type based on the data structure
        if len(df.columns) == 2:
            x_col = df.columns[0]
            y_col = df.columns[1]

            # Check if the second column is numeric (for bar charts/histograms)
            if df.dtypes.iloc[1].kind in 'iuf':
                # Create a bar chart
                fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")

            # If both columns are numeric, create a scatter plot
            elif df.dtypes.iloc[0].kind in 'iuf' and df.dtypes.iloc[1].kind in 'iuf':
                fig = px.scatter(df, x=x_col, y=y_col, title=f"Relationship between {x_col} and {y_col}")

            # Otherwise, create a simple line chart
            else:
                fig = px.line(df, x=x_col, y=y_col, title=f"Trend of {y_col} by {x_col}")

        # For DataFrames with more columns, create a summary visualization
        else:
            # Get numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns

            if len(numeric_cols) > 0:
                # Create a bar chart of the mean of each numeric column
                means = df[numeric_cols].mean().sort_values(ascending=False)
                fig = px.bar(
                    x=means.index,
                    y=means.values,
                    title="Average Values by Column"
                )
            else:
                # Create a count plot of the first categorical column
                first_col = df.columns[0]
                value_counts = df[first_col].value_counts().sort_values(ascending=False).head(10)
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"Count of {first_col} Values"
                )

        # Update layout for better appearance
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=50, b=40)
        )

        # Convert to JSON
        return json.loads(fig.to_json())

    except Exception as e:
        logger.error(f"Failed to create fallback visualization: {str(e)}")
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
