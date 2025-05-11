"""
Data Analysis Agent - Agent Module

This module provides functionality for creating and managing agents.
"""

import streamlit as st
import pandas as pd
from typing import Optional, Any

from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

import sys
import os

# Add the parent directory to the Python path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config import settings
from core.llm import ChatOpenRouter


def initialize_agent(llm: ChatOpenRouter, df: pd.DataFrame) -> Optional[Any]:
    """
    Initialize a Pandas DataFrame agent with the given LLM and DataFrame.

    Args:
        llm: The LLM to use for the agent
        df: The DataFrame to analyze

    Returns:
        Optional[Any]: Initialized agent or None if initialization fails
    """
    if df is None or df.empty:
        st.error("Cannot initialize agent: DataFrame is empty or None")
        return None

    if llm is None:
        st.error("Cannot initialize agent: LLM is not initialized")
        return None

    # Create a spinner in the main area
    with st.spinner("Initializing agent..."):
        try:
            agent = create_pandas_dataframe_agent(
                llm=llm,
                df=df,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                verbose=True,
                allow_dangerous_code=settings.AGENT_ALLOW_DANGEROUS_CODE,
                max_iterations=settings.AGENT_MAX_ITERATIONS,
                max_execution_time=settings.AGENT_MAX_EXECUTION_TIME,
                early_stopping_method=settings.AGENT_EARLY_STOPPING_METHOD
            )
            st.sidebar.success("Agent initialized successfully!")
            return agent
        except Exception as e:
            st.sidebar.error(f"Error initializing agent: {str(e)}")
            return None


def process_query(agent: Any, query: str) -> Any:
    """
    Process a query using the agent.

    Args:
        agent: The agent to use for processing
        query: The query to process

    Returns:
        Any: The agent's response
    """
    if agent is None:
        st.error("Cannot process query: Agent is not initialized")
        return None

    try:
        response = agent.invoke(query)
        return response
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        return None
