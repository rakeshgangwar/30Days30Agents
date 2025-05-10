"""
Tests for the API dependencies.
"""
import os
import sys
import pytest
from fastapi import HTTPException
from unittest.mock import patch

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.api.deps import get_api_key, get_optional_api_key
from app.core.config import settings


@pytest.mark.asyncio
async def test_get_api_key_valid(api_key):
    """Test get_api_key with a valid API key."""
    # Test with a valid API key
    result = await get_api_key(api_key)
    assert result == api_key


@pytest.mark.asyncio
async def test_get_api_key_invalid():
    """Test get_api_key with an invalid API key."""
    # Set a valid API key in settings
    settings.API_KEY = "valid-key"
    
    # Test with an invalid API key
    with pytest.raises(HTTPException) as excinfo:
        await get_api_key("invalid-key")
    
    # Check the exception details
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid or missing API key"
    assert excinfo.value.headers["WWW-Authenticate"] == "APIKey"


@pytest.mark.asyncio
async def test_get_api_key_missing():
    """Test get_api_key with a missing API key."""
    # Set a valid API key in settings
    settings.API_KEY = "valid-key"
    
    # Test with a missing API key
    with pytest.raises(HTTPException) as excinfo:
        await get_api_key(None)
    
    # Check the exception details
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Invalid or missing API key"


@pytest.mark.asyncio
async def test_get_api_key_disabled_auth():
    """Test get_api_key when authentication is disabled."""
    # Save the original API key
    original_api_key = settings.API_KEY
    
    try:
        # Disable authentication by setting API_KEY to None
        settings.API_KEY = None
        
        # Test with any API key (should pass)
        result = await get_api_key("any-key")
        assert result == ""
        
        # Test with no API key (should also pass)
        result = await get_api_key(None)
        assert result == ""
    finally:
        # Restore the original API key
        settings.API_KEY = original_api_key


@pytest.mark.asyncio
async def test_get_optional_api_key_valid(api_key):
    """Test get_optional_api_key with a valid API key."""
    # Test with a valid API key
    result = await get_optional_api_key(api_key)
    assert result == api_key


@pytest.mark.asyncio
async def test_get_optional_api_key_invalid():
    """Test get_optional_api_key with an invalid API key."""
    # Set a valid API key in settings
    settings.API_KEY = "valid-key"
    
    # Test with an invalid API key
    result = await get_optional_api_key("invalid-key")
    assert result is None


@pytest.mark.asyncio
async def test_get_optional_api_key_missing():
    """Test get_optional_api_key with a missing API key."""
    # Set a valid API key in settings
    settings.API_KEY = "valid-key"
    
    # Test with a missing API key
    result = await get_optional_api_key(None)
    assert result is None


@pytest.mark.asyncio
async def test_get_optional_api_key_disabled_auth():
    """Test get_optional_api_key when authentication is disabled."""
    # Save the original API key
    original_api_key = settings.API_KEY
    
    try:
        # Disable authentication by setting API_KEY to None
        settings.API_KEY = None
        
        # Test with any API key (should return empty string)
        result = await get_optional_api_key("any-key")
        assert result == ""
        
        # Test with no API key (should also return empty string)
        result = await get_optional_api_key(None)
        assert result == ""
    finally:
        # Restore the original API key
        settings.API_KEY = original_api_key
