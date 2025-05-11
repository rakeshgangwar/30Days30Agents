"""
OpenRouter Client for Data Analysis Agent

This module provides a custom ChatOpenAI class configured for OpenRouter.
"""

import os
from typing import Optional

from langchain_core.utils.utils import secret_from_env
from langchain_openai import ChatOpenAI
from pydantic import Field, SecretStr


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
