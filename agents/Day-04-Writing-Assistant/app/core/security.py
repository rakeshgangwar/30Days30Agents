"""
Security utilities for authentication.

This module provides security utilities for the Writing Assistant API,
including API key validation and JWT token handling.
"""
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.core.config import settings


def generate_api_key() -> str:
    """
    Generate a secure API key.
    
    Returns:
        str: A secure random API key.
    """
    return secrets.token_urlsafe(32)


def verify_api_key(api_key: str, valid_api_key: str) -> bool:
    """
    Verify an API key against a valid API key.
    
    Args:
        api_key: The API key to verify
        valid_api_key: The valid API key to compare against
        
    Returns:
        bool: True if the API key is valid, False otherwise
    """
    if not api_key or not valid_api_key:
        return False
    return secrets.compare_digest(api_key, valid_api_key)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time
        
    Returns:
        str: JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a JWT access token.
    
    Args:
        token: JWT token
        
    Returns:
        Optional[Dict[str, Any]]: Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
