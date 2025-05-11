"""
Data Analysis Agent - LLM Module

This module provides functionality for initializing and configuring the LLM.
"""

import os
import streamlit as st
from typing import Optional

from langchain_core.utils.utils import secret_from_env
from langchain_openai import ChatOpenAI
from pydantic import Field, SecretStr

import sys
import os

# Add the parent directory to the Python path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config import settings


class ChatOpenRouter(ChatOpenAI):
    """
    Custom ChatOpenAI class configured for OpenRouter.

    This class extends ChatOpenAI with OpenRouter-specific configurations,
    making it easier to use OpenRouter as a drop-in replacement for OpenAI.
    """

    openai_api_key: Optional[SecretStr] = Field(
        alias="api_key",
        default_factory=secret_from_env("OPENROUTER_API_KEY", default=None),
    )

    @property
    def lc_secrets(self) -> dict[str, str]:
        return {"openai_api_key": "OPENROUTER_API_KEY"}

    def __init__(self,
                 openai_api_key: Optional[str] = None,
                 **kwargs):
        """
        Initialize the ChatOpenRouter with OpenRouter-specific configurations.

        Args:
            openai_api_key: OpenRouter API key (falls back to OPENROUTER_API_KEY env var)
            **kwargs: Additional arguments to pass to ChatOpenAI
        """
        openai_api_key = (
            openai_api_key or os.environ.get("OPENROUTER_API_KEY")
        )
        super().__init__(
            base_url="https://openrouter.ai/api/v1",
            openai_api_key=openai_api_key,
            **kwargs
        )


def initialize_llm() -> Optional[ChatOpenRouter]:
    """
    Initialize the LLM with settings from the configuration.

    Returns:
        Optional[ChatOpenRouter]: Initialized LLM or None if initialization fails
    """
    # Check if we have an API key
    openrouter_api_key = settings.OPENROUTER_API_KEY
    if not openrouter_api_key:
        st.sidebar.error("OpenRouter API key not found. Please add it to your .env file.")
        return None

    # Create a spinner in the main area instead of sidebar
    with st.spinner("Initializing LLM..."):
        try:
            llm = ChatOpenRouter(
                openai_api_key=openrouter_api_key,
                model_name=settings.DEFAULT_LLM_MODEL,
                temperature=settings.DEFAULT_TEMPERATURE,
                max_tokens=settings.DEFAULT_MAX_TOKENS,
                request_timeout=settings.DEFAULT_REQUEST_TIMEOUT,
                max_retries=settings.DEFAULT_MAX_RETRIES
            )
            st.sidebar.success("LLM initialized successfully!")
            return llm
        except Exception as e:
            st.sidebar.error(f"Error initializing LLM: {str(e)}")
            return None
