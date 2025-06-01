"""
OpenRouter API client for cloud LLM access.

This module provides a client for interacting with the OpenRouter API,
which offers access to various cloud-based language models.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import httpx
from loguru import logger
from config.settings import settings


class OpenRouterModel(Enum):
    """Available OpenRouter models with their identifiers"""
    CLAUDE_3_5_SONNET = "anthropic/claude-3.5-sonnet"
    CLAUDE_3_HAIKU = "anthropic/claude-3-haiku"
    GPT_4_TURBO = "openai/gpt-4-turbo"
    GPT_4O = "openai/gpt-4o"
    GPT_4O_MINI = "openai/gpt-4o-mini"
    LLAMA_3_1_8B = "meta-llama/llama-3.1-8b-instruct"
    LLAMA_3_1_70B = "meta-llama/llama-3.1-70b-instruct"
    GEMINI_PRO = "google/gemini-pro"
    DEEPSEEK_CHAT_V3_FREE = "deepseek/deepseek-chat-v3-0324:free"
    
    @classmethod
    def get_default(cls) -> "OpenRouterModel":
        """Get the default model from settings"""
        model_name = settings.OPENROUTER_MODEL
        for model in cls:
            if model.value == model_name:
                return model
        logger.warning(f"Unknown model '{model_name}' in settings, using Claude 3.5 Sonnet")
        return cls.CLAUDE_3_5_SONNET


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    tokens_per_minute: int = 100000
    max_retries: int = 3
    retry_delay: float = 1.0
    backoff_multiplier: float = 2.0


@dataclass
class RequestHistory:
    """Track request history for rate limiting"""
    timestamps: List[float] = field(default_factory=list)
    token_usage: List[int] = field(default_factory=list)
    
    def add_request(self, tokens_used: int = 0):
        """Add a request to the history"""
        current_time = time.time()
        self.timestamps.append(current_time)
        self.token_usage.append(tokens_used)
        
        # Clean old entries (older than 1 hour)
        cutoff_time = current_time - 3600
        self.timestamps = [t for t in self.timestamps if t > cutoff_time]
        self.token_usage = self.token_usage[-len(self.timestamps):]


class OpenRouterError(Exception):
    """Base exception for OpenRouter API errors"""
    pass


class RateLimitError(OpenRouterError):
    """Raised when rate limits are exceeded"""
    pass


class AuthenticationError(OpenRouterError):
    """Raised when authentication fails"""
    pass


class ModelNotFoundError(OpenRouterError):
    """Raised when requested model is not found"""
    pass


class OpenRouterClient:
    """Client for interacting with the OpenRouter API"""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[Union[str, OpenRouterModel]] = None,
        rate_limit_config: Optional[RateLimitConfig] = None,
        timeout: float = 30.0
    ):
        """
        Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key. If None, will use OPENROUTER_API_KEY from settings
            model: Default model to use. If None, will use model from settings
            rate_limit_config: Rate limiting configuration
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        if not self.api_key:
            raise AuthenticationError("OpenRouter API key is required")
        
        # Set default model
        if isinstance(model, str):
            self.default_model = model
        elif isinstance(model, OpenRouterModel):
            self.default_model = model.value
        else:
            self.default_model = OpenRouterModel.get_default().value
        
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.timeout = timeout
        self.request_history = RequestHistory()
        
        # HTTP client configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/meeting-assistant",
                "X-Title": "Meeting Assistant"
            }
        )
        
        logger.info(f"OpenRouter client initialized with model: {self.default_model}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    def _check_rate_limits(self) -> bool:
        """Check if we're within rate limits"""
        current_time = time.time()
        
        # Check requests per minute
        minute_ago = current_time - 60
        recent_requests = [t for t in self.request_history.timestamps if t > minute_ago]
        if len(recent_requests) >= self.rate_limit_config.requests_per_minute:
            return False
        
        # Check requests per hour
        hour_ago = current_time - 3600
        hourly_requests = [t for t in self.request_history.timestamps if t > hour_ago]
        if len(hourly_requests) >= self.rate_limit_config.requests_per_hour:
            return False
        
        # Check tokens per minute
        minute_tokens = sum(
            tokens for t, tokens in zip(self.request_history.timestamps, self.request_history.token_usage)
            if t > minute_ago
        )
        if minute_tokens >= self.rate_limit_config.tokens_per_minute:
            return False
        
        return True
    
    async def _wait_for_rate_limit(self):
        """Wait until rate limits allow a new request"""
        while not self._check_rate_limits():
            logger.warning("Rate limit reached, waiting...")
            await asyncio.sleep(1)
    
    async def _make_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """Make a request to the OpenRouter API with retry logic"""
        
        # Check rate limits
        await self._wait_for_rate_limit()
        
        try:
            url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
            response = await self.client.post(url, json=data)
            
            # Track the request
            tokens_used = data.get("max_tokens", 0)  # Estimate, actual usage in response
            self.request_history.add_request(tokens_used)
            
            if response.status_code == 200:
                result = response.json()
                
                # Update token usage with actual usage if available
                if "usage" in result:
                    actual_tokens = result["usage"].get("total_tokens", tokens_used)
                    if self.request_history.token_usage:
                        self.request_history.token_usage[-1] = actual_tokens
                
                return result
            
            elif response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            
            elif response.status_code == 404:
                raise ModelNotFoundError(f"Model not found: {data.get('model', 'unknown')}")
            
            elif response.status_code == 429:
                if retry_count < self.rate_limit_config.max_retries:
                    delay = self.rate_limit_config.retry_delay * (
                        self.rate_limit_config.backoff_multiplier ** retry_count
                    )
                    logger.warning(f"Rate limited, retrying in {delay}s (attempt {retry_count + 1})")
                    await asyncio.sleep(delay)
                    return await self._make_request(endpoint, data, retry_count + 1)
                else:
                    raise RateLimitError("Rate limit exceeded and max retries reached")
            
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"OpenRouter API error: {error_msg}")
                raise OpenRouterError(error_msg)
        
        except httpx.TimeoutException:
            if retry_count < self.rate_limit_config.max_retries:
                delay = self.rate_limit_config.retry_delay * (
                    self.rate_limit_config.backoff_multiplier ** retry_count
                )
                logger.warning(f"Request timeout, retrying in {delay}s (attempt {retry_count + 1})")
                await asyncio.sleep(delay)
                return await self._make_request(endpoint, data, retry_count + 1)
            else:
                raise OpenRouterError("Request timeout and max retries reached")
        
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise OpenRouterError(f"Request failed: {e}")
    
    async def generate_completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 1.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion using the OpenRouter API.
        
        Args:
            prompt: The input prompt
            model: Model to use (defaults to instance default)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            top_p: Nucleus sampling parameter
            **kwargs: Additional parameters for the API
            
        Returns:
            API response dictionary
        """
        model = model or self.default_model
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            **kwargs
        }
        
        logger.debug(f"Generating completion with model: {model}")
        return await self._make_request("chat/completions", data)
    
    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a chat completion using the OpenRouter API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to instance default)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters for the API
            
        Returns:
            API response dictionary
        """
        model = model or self.default_model
        
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        logger.debug(f"Generating chat completion with model: {model}, {len(messages)} messages")
        return await self._make_request("chat/completions", data)
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from OpenRouter"""
        try:
            response = await self.client.get(f"{self.BASE_URL}/models")
            if response.status_code == 200:
                result = response.json()
                return result.get("data", [])
            else:
                logger.error(f"Failed to get models: HTTP {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error fetching models: {e}")
            return []
    
    async def health_check(self) -> bool:
        """Check if the OpenRouter API is accessible"""
        try:
            # Try a simple completion with minimal tokens
            result = await self.generate_completion(
                prompt="Say 'OK'",
                max_tokens=5,
                temperature=0.0
            )
            return "choices" in result and len(result["choices"]) > 0
        except Exception as e:
            logger.error(f"OpenRouter health check failed: {e}")
            return False
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        current_time = time.time()
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        recent_requests = [t for t in self.request_history.timestamps if t > minute_ago]
        hourly_requests = [t for t in self.request_history.timestamps if t > hour_ago]
        
        minute_tokens = sum(
            tokens for t, tokens in zip(self.request_history.timestamps, self.request_history.token_usage)
            if t > minute_ago
        )
        
        return {
            "requests_per_minute": {
                "used": len(recent_requests),
                "limit": self.rate_limit_config.requests_per_minute,
                "remaining": self.rate_limit_config.requests_per_minute - len(recent_requests)
            },
            "requests_per_hour": {
                "used": len(hourly_requests),
                "limit": self.rate_limit_config.requests_per_hour,
                "remaining": self.rate_limit_config.requests_per_hour - len(hourly_requests)
            },
            "tokens_per_minute": {
                "used": minute_tokens,
                "limit": self.rate_limit_config.tokens_per_minute,
                "remaining": self.rate_limit_config.tokens_per_minute - minute_tokens
            }
        }