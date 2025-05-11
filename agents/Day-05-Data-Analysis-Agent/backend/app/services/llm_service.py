"""
Data Analysis Agent - LLM Service

This module provides functionality for initializing and configuring the LLM.
"""

import os
import logging
from typing import Optional, Dict, Any

from langchain_core.utils.utils import secret_from_env
from langchain_openai import ChatOpenAI
from pydantic import Field, SecretStr

from app.config import settings

# Set up logging
logger = logging.getLogger(__name__)


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
        logger.error("OpenRouter API key not found. Please add it to your .env file.")
        return None

    try:
        llm = ChatOpenRouter(
            openai_api_key=openrouter_api_key,
            model_name=settings.DEFAULT_LLM_MODEL,
            temperature=settings.DEFAULT_TEMPERATURE,
            max_tokens=settings.DEFAULT_MAX_TOKENS,
            request_timeout=settings.DEFAULT_REQUEST_TIMEOUT,
            max_retries=settings.DEFAULT_MAX_RETRIES
        )
        logger.info("LLM initialized successfully!")
        return llm
    except Exception as e:
        logger.error(f"Error initializing LLM: {str(e)}")
        return None


def test_llm_connection() -> Dict[str, Any]:
    """
    Test the LLM connection by sending a simple query.
    
    Returns:
        Dict[str, Any]: Dictionary with success status and message
    """
    llm = initialize_llm()
    if not llm:
        return {"success": False, "message": "Failed to initialize LLM"}
    
    try:
        response = llm.invoke("Say hello!")
        return {
            "success": True, 
            "message": "LLM connection successful", 
            "response": response.content
        }
    except Exception as e:
        logger.error(f"Error testing LLM connection: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}
