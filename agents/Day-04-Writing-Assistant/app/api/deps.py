"""
API Dependencies

This module provides dependency functions for FastAPI endpoints.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.core.security import verify_api_key

# Define API key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Validate API key from header.
    
    Args:
        api_key: API key from header
        
    Returns:
        str: Validated API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    # If API_KEY is not set in settings, authentication is disabled
    if not settings.API_KEY:
        return ""
    
    if not api_key or not verify_api_key(api_key, settings.API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "APIKey"},
        )
    
    return api_key


async def get_optional_api_key(api_key: str = Security(api_key_header)) -> Optional[str]:
    """
    Optionally validate API key from header.
    
    This dependency doesn't raise an exception if the API key is missing or invalid.
    It's useful for endpoints that can work with or without authentication.
    
    Args:
        api_key: API key from header
        
    Returns:
        Optional[str]: Validated API key or None if invalid
    """
    # If API_KEY is not set in settings, authentication is disabled
    if not settings.API_KEY:
        return ""
    
    if not api_key or not verify_api_key(api_key, settings.API_KEY):
        return None
    
    return api_key
