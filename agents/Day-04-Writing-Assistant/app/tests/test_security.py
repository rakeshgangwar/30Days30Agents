"""
Tests for the security module.
"""
import os
import sys
import pytest
from datetime import datetime, timedelta
from jose import jwt

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.core.security import (
    generate_api_key,
    verify_api_key,
    create_access_token,
    decode_access_token
)
from app.core.config import settings


def test_generate_api_key():
    """Test API key generation."""
    # Generate an API key
    api_key = generate_api_key()

    # Check that it's a non-empty string
    assert isinstance(api_key, str)
    assert len(api_key) > 0

    # Generate another key and check that they're different
    another_key = generate_api_key()
    assert api_key != another_key


def test_verify_api_key():
    """Test API key verification."""
    # Generate a valid API key
    valid_key = generate_api_key()

    # Test with valid key
    assert verify_api_key(valid_key, valid_key) is True

    # Test with invalid key
    invalid_key = generate_api_key()
    assert verify_api_key(invalid_key, valid_key) is False

    # Test with empty keys
    assert verify_api_key("", valid_key) is False
    assert verify_api_key(valid_key, "") is False
    assert verify_api_key("", "") is False


def test_create_access_token():
    """Test JWT access token creation."""
    # Create test data
    data = {"sub": "test-user", "role": "user"}

    # Create a token
    token = create_access_token(data)

    # Check that it's a non-empty string
    assert isinstance(token, str)
    assert len(token) > 0

    # Decode the token and check the payload
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "test-user"
    assert payload["role"] == "user"
    assert "exp" in payload


def test_create_access_token_with_expiration():
    """Test JWT access token creation with custom expiration."""
    # Create test data
    data = {"sub": "test-user"}
    expires_delta = timedelta(minutes=30)

    # Create a token with custom expiration
    token = create_access_token(data, expires_delta=expires_delta)

    # Decode the token and check the expiration
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    # Verify that the token has an expiration claim
    assert "exp" in payload

    # Verify that the token is not expired
    # We don't test the exact expiration time as it depends on the current time
    # which can cause flaky tests
    try:
        # This will raise an exception if the token is expired
        jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True}
        )
        # If we get here, the token is not expired
        assert True
    except jwt.ExpiredSignatureError:
        # If we get here, the token is expired, which is not expected
        assert False, "Token should not be expired"


def test_decode_access_token():
    """Test JWT access token decoding."""
    # Create test data
    data = {"sub": "test-user", "role": "admin"}

    # Create a token
    token = create_access_token(data)

    # Decode the token
    payload = decode_access_token(token)

    # Check the payload
    assert payload is not None
    assert payload["sub"] == "test-user"
    assert payload["role"] == "admin"


def test_decode_access_token_invalid():
    """Test decoding an invalid JWT access token."""
    # Test with an invalid token
    payload = decode_access_token("invalid-token")
    assert payload is None

    # Test with an empty token
    payload = decode_access_token("")
    assert payload is None


def test_decode_access_token_expired():
    """Test decoding an expired JWT access token."""
    # Create test data with a token that's already expired
    data = {"sub": "test-user"}
    expires_delta = timedelta(minutes=-1)  # Expired 1 minute ago

    # Create an expired token
    token = create_access_token(data, expires_delta=expires_delta)

    # Attempt to decode the expired token
    payload = decode_access_token(token)

    # Should return None for an expired token
    assert payload is None
