"""
Ollama client for local LLM processing.

This module provides a client for interacting with locally running Ollama models,
serving as a fallback when OpenRouter is unavailable or rate limited.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import httpx
from loguru import logger

from config.settings import settings


class OllamaModel(Enum):
    """Available Ollama models with their identifiers"""
    LLAMA3_8B = "llama3:8b"
    LLAMA3_70B = "llama3:70b"
    MISTRAL_7B = "mistral:7b"
    PHI3_MINI = "phi3:mini"
    QWEN_3_30BB = "qwen3:30b-a3b"
    
    @classmethod
    def get_default(cls) -> "OllamaModel":
        """Get the default model from settings"""
        model_name = settings.OLLAMA_MODEL
        for model in cls:
            if model.value == model_name:
                return model
        logger.warning(f"Unknown model '{model_name}' in settings, using Llama3 8B")
        return cls.LLAMA3_8B

@dataclass
class OllamaConfig:
    """Configuration for Ollama client"""
    base_url: str = "http://localhost:11434"
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0

class OllamaError(Exception):
    """Base exception for Ollama errors"""
    pass

class OllamaClient:
    """Client for interacting with local Ollama models"""
    
    def __init__(
        self,
        config: Optional[OllamaConfig] = None,
        model: Optional[Union[str, OllamaModel]] = None
    ):
        """
        Initialize the Ollama client.
        
        Args:
            config: Ollama configuration
            model: Default model to use
        """
        self.config = config or OllamaConfig()
        
        # Set default model
        if isinstance(model, str):
            self.default_model = model
        elif isinstance(model, OllamaModel):
            self.default_model = model.value
        else:
            self.default_model = OllamaModel.get_default().value
            
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.config.timeout),
            headers={
                "Content-Type": "application/json"
            }
        )
        
        logger.info(f"Ollama client initialized with model: {self.default_model}")

    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
        
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _make_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Make a request to Ollama API with retry logic"""
        try:
            url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
            response = await self.client.post(url, json=data)
            
            if response.status_code == 200:
                return await response.json()
            elif response.status_code == 404:
                raise OllamaError(f"Model not found: {data.get('model', 'unknown')}")
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Ollama API error: {error_msg}")
                raise OllamaError(error_msg)
                
        except httpx.TimeoutException:
            if retry_count < self.config.max_retries:
                delay = self.config.retry_delay * (1 + retry_count)
                logger.warning(f"Request timeout, retrying in {delay}s (attempt {retry_count + 1})")
                await asyncio.sleep(delay)
                return await self._make_request(endpoint, data, retry_count + 1)
            else:
                raise OllamaError("Request timeout and max retries reached")
                
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise OllamaError(f"Request failed: {e}")

    async def generate_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion using Ollama.
        
        Args:
            prompt: The input prompt
            model: Model to use (defaults to instance default)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            API response dictionary
        """
        model = model or self.default_model
        
        data = {
            "model": model,
            "prompt": prompt,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                **kwargs
            }
        }
        
        logger.debug(f"Generating completion with model: {model}")
        return await self._make_request("api/generate", data)

    async def health_check(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = await self.client.get(f"{self.config.base_url}/")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False