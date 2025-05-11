"""
Data Analysis Agent - Visualization Module

This module provides functionality for creating data visualizations.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from typing import Optional


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
