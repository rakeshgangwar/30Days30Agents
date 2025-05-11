"""
Data Analysis Agent - Visualization Module

This module provides functionality for creating data visualizations.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import re
import ast
import inspect
from typing import Optional, Tuple, Dict, Any, List


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

        elif viz_type == 'heatmap':
            if df.select_dtypes(include=['number']).shape[1] >= 2:
                corr = df.select_dtypes(include=['number']).corr()
                sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
            else:
                st.error("Not enough numeric columns for a correlation heatmap")
                return None

        elif viz_type == 'boxplot':
            column = kwargs.get('column')
            if column and column in df.columns:
                sns.boxplot(data=df, y=column, ax=ax)
            else:
                st.error(f"Invalid column for boxplot: {column}")
                return None

        elif viz_type == 'pairplot':
            # For pairplots, we need to create a new figure
            plt.close(fig)
            numeric_df = df.select_dtypes(include=['number'])
            if numeric_df.shape[1] >= 2:
                columns = kwargs.get('columns', numeric_df.columns.tolist()[:4])  # Limit to 4 columns by default
                fig = sns.pairplot(df[columns])
                return fig
            else:
                st.error("Not enough numeric columns for a pairplot")
                return None

        else:
            st.error(f"Unsupported visualization type: {viz_type}")
            return None

        plt.tight_layout()
        return fig
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")
        return None


def display_visualization(fig: plt.Figure) -> None:
    """
    Display a matplotlib figure in the Streamlit UI.

    Args:
        fig: The matplotlib figure to display
    """
    if fig is not None:
        st.pyplot(fig)
    else:
        st.error("No visualization to display")


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
        'plt', 'pd', 'sns', 'np'
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


def execute_visualization_code(code: str, df: pd.DataFrame) -> Tuple[Optional[plt.Figure], str]:
    """
    Execute visualization code and return the resulting figure.

    Args:
        code: The Python code to execute
        df: The DataFrame to use in the code

    Returns:
        Tuple[Optional[plt.Figure], str]: The resulting figure and any output/error message
    """
    if not code:
        return None, "No code to execute"

    if not is_safe_code(code):
        return None, "The generated code contains potentially unsafe operations and cannot be executed"

    # Create a local namespace with the DataFrame and necessary imports
    local_namespace = {
        'df': df,
        'pd': pd,
        'plt': plt,
        'sns': sns,
        'np': __import__('numpy')
    }

    try:
        # Capture the current figure before execution
        old_figs = plt.get_fignums()

        # Execute the code
        exec(code, {}, local_namespace)

        # Get the new figure(s) created by the code
        new_figs = plt.get_fignums()
        new_fig_nums = [fig for fig in new_figs if fig not in old_figs]

        if new_fig_nums:
            # Return the last created figure
            return plt.figure(new_fig_nums[-1]), "Visualization created successfully"
        else:
            # Check if the code returned a figure directly
            for var_name, var_value in local_namespace.items():
                if isinstance(var_value, plt.Figure):
                    return var_value, "Visualization created successfully"

            return None, "No figure was created by the code"
    except Exception as e:
        return None, f"Error executing visualization code: {str(e)}"


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
    sample_data = df.head(3).to_dict(orient='records')

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

INSTRUCTIONS:
1. Generate Python code using matplotlib and/or seaborn to create the visualization.
2. Use the variable 'df' which already contains the DataFrame.
3. Include necessary imports (matplotlib.pyplot as plt, seaborn as sns).
4. Set an appropriate figure size and title.
5. Include code to create the figure (e.g., fig, ax = plt.subplots()).
6. Do NOT include plt.show() as the figure will be displayed by Streamlit.
7. Return ONLY the Python code within a code block (```python ... ```).
8. Make sure the code is complete and can run independently.
9. Use appropriate colors, labels, and styling for a professional visualization.

Example response format:
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Create figure and axes
fig, ax = plt.subplots(figsize=(10, 6))

# Create the visualization
sns.barplot(data=df, x='column_name', y='another_column', ax=ax)

# Add title and labels
plt.title('Descriptive Title')
plt.xlabel('X Axis Label')
plt.ylabel('Y Axis Label')

# Improve readability
plt.xticks(rotation=45)
plt.tight_layout()
```
"""
    return prompt
