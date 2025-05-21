"""
AI Client Module

This module provides clients for AI services.
"""

from typing import Optional, Dict, Any

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class OpenAIClient:
    """
    Client for OpenAI API.
    
    This class provides methods for interacting with the OpenAI API,
    including error handling and retries.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client.
        
        Args:
            api_key: The OpenAI API key. If None, uses the key from settings.
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_text(
        self,
        prompt: str,
        model: str = "gpt-4o",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """
        Generate text using the OpenAI API.
        
        Args:
            prompt: The prompt to generate text from.
            model: The model to use.
            max_tokens: The maximum number of tokens to generate.
            temperature: The temperature to use for generation.
            **kwargs: Additional arguments to pass to the API.
            
        Returns:
            The generated text.
            
        Raises:
            Exception: If the API call fails.
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
        
        return response.choices[0].message.content
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_chat_completion(
        self,
        messages: list,
        model: str = "gpt-4o",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using the OpenAI API.
        
        Args:
            messages: The messages to generate a completion from.
            model: The model to use.
            max_tokens: The maximum number of tokens to generate.
            temperature: The temperature to use for generation.
            **kwargs: Additional arguments to pass to the API.
            
        Returns:
            The chat completion response.
            
        Raises:
            Exception: If the API call fails.
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )
        
        return {
            "content": response.choices[0].message.content,
            "role": response.choices[0].message.role,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
        }


# Global OpenAI client instance
_openai_client: Optional[OpenAIClient] = None


def get_openai_client() -> OpenAIClient:
    """
    Get the OpenAI client instance.
    
    Returns:
        The OpenAI client instance.
    """
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAIClient()
    return _openai_client
