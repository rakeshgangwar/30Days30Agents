"""
Models service module for fetching and caching available LLM models.

This module provides a service for fetching available models from OpenRouter
and caching them to avoid repeated API calls.
"""
import logging
import time
from typing import Dict, List, Optional, Any
import httpx
from pydantic import BaseModel

import sys
import os

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelInfo(BaseModel):
    """Model information from OpenRouter."""
    id: str
    name: str
    description: Optional[str] = None
    context_length: Optional[int] = None
    pricing: Optional[Dict[str, Any]] = None
    provider: Optional[str] = None


class ModelsService:
    """Service for fetching and caching available LLM models."""

    def __init__(self):
        """Initialize the models service."""
        self.cache = {}
        self.cache_expiry = {}
        self.cache_ttl = 3600  # Cache TTL in seconds (1 hour)
        self.openrouter_models_url = "https://openrouter.ai/api/v1/models"

    async def get_available_models(self, force_refresh: bool = False) -> List[ModelInfo]:
        """
        Get available models from OpenRouter with caching.

        Args:
            force_refresh: Whether to bypass the cache and fetch fresh data

        Returns:
            List of available models
        """
        cache_key = "openrouter_models"

        # Return cached models if available and not expired
        if not force_refresh and cache_key in self.cache:
            # Check if cache is still valid
            if time.time() < self.cache_expiry.get(cache_key, 0):
                logger.debug("Returning cached models")
                return self.cache[cache_key]
            else:
                logger.debug("Cache expired, fetching fresh models")

        # Fetch models from OpenRouter
        try:
            logger.info("Fetching available models from OpenRouter")
            
            # Check if API key is available
            if not settings.OPENROUTER_API_KEY:
                logger.warning("OpenRouter API key not configured, returning empty list")
                return []
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://writing-assistant.app",  # Update with actual site URL
                    "X-Title": "Writing Assistant",  # Update with actual site name
                }
                
                response = await client.get(
                    self.openrouter_models_url,
                    headers=headers,
                    timeout=10.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Process and filter models
                models = []
                for model_data in data.get("data", []):
                    # Create ModelInfo object
                    model = ModelInfo(
                        id=model_data.get("id", ""),
                        name=model_data.get("name", ""),
                        description=model_data.get("description", ""),
                        context_length=model_data.get("context_length", 0),
                        pricing=model_data.get("pricing", {}),
                        provider=model_data.get("id", "").split("/")[0] if "/" in model_data.get("id", "") else None
                    )
                    models.append(model)
                
                # Update cache
                self.cache[cache_key] = models
                self.cache_expiry[cache_key] = time.time() + self.cache_ttl
                
                logger.info(f"Fetched {len(models)} models from OpenRouter")
                return models
                
        except Exception as e:
            logger.error(f"Error fetching models from OpenRouter: {str(e)}")
            
            # Return cached models if available (even if expired)
            if cache_key in self.cache:
                logger.warning("Returning expired cached models due to fetch error")
                return self.cache[cache_key]
            
            # Return empty list if no cache available
            return []

    def get_model_by_id(self, model_id: str) -> Optional[ModelInfo]:
        """
        Get a specific model by ID.

        Args:
            model_id: The ID of the model to get

        Returns:
            Model information if found, None otherwise
        """
        cache_key = "openrouter_models"
        
        # Check if models are cached
        if cache_key not in self.cache:
            logger.warning(f"Models not cached, cannot get model {model_id}")
            return None
            
        # Find model in cached models
        for model in self.cache[cache_key]:
            if model.id == model_id:
                return model
                
        logger.warning(f"Model {model_id} not found in cached models")
        return None


# Singleton instance for use throughout the application
models_service = ModelsService()
