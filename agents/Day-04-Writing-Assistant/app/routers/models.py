"""
API router for model information.

This module provides API endpoints for retrieving available LLM models.
"""
import os
import sys
import logging
from typing import List

from fastapi import APIRouter, Query

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.services.models_service import models_service, ModelInfo

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/models", response_model=List[ModelInfo])
async def get_available_models(
    force_refresh: bool = Query(False, description="Force refresh the models cache")
):
    """
    Get available LLM models from OpenRouter.
    
    This endpoint returns a list of available models that can be used with the Writing Assistant.
    The results are cached to avoid repeated API calls to OpenRouter.
    
    Args:
        force_refresh: Whether to bypass the cache and fetch fresh data
        
    Returns:
        List of available models
    """
    logger.info(f"Getting available models (force_refresh={force_refresh})")
    
    models = await models_service.get_available_models(force_refresh=force_refresh)
    
    logger.info(f"Returning {len(models)} available models")
    return models


@router.get("/models/{model_id}", response_model=ModelInfo)
async def get_model_by_id(model_id: str):
    """
    Get information about a specific model.
    
    Args:
        model_id: The ID of the model to get information for
        
    Returns:
        Model information
    """
    logger.info(f"Getting information for model: {model_id}")
    
    # Ensure models are cached
    await models_service.get_available_models()
    
    # Get model from cache
    model = models_service.get_model_by_id(model_id)
    
    if not model:
        # If model not found in cache, try to fetch fresh data
        logger.warning(f"Model {model_id} not found in cache, fetching fresh data")
        await models_service.get_available_models(force_refresh=True)
        model = models_service.get_model_by_id(model_id)
        
        if not model:
            # If still not found, return 404
            logger.error(f"Model {model_id} not found")
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
    
    logger.info(f"Returning information for model: {model_id}")
    return model
