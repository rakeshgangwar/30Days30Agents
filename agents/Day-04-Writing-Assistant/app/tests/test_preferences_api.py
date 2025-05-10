"""
Integration tests for the preferences API endpoints.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.models.preferences import UserPreference


def test_get_preferences_unauthorized(client, test_user_id, api_key):
    """Test getting preferences without authentication."""
    # Make a request without an API key
    response = client.get(f"/api/v1/preferences/{test_user_id}")
    
    # Check that we got a 401 Unauthorized response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_get_preferences_not_found(client, api_key):
    """Test getting preferences for a user that doesn't exist."""
    # Make a request with a valid API key
    response = client.get(
        "/api/v1/preferences/non-existent-user",
        headers={"X-API-Key": api_key}
    )
    
    # Check that we got a 200 OK response with default preferences
    assert response.status_code == 200
    
    # Check that the response contains default preferences
    data = response.json()
    assert data["user_id"] == "non-existent-user"
    assert data["preferred_model"] is None
    assert data["temperature"] == 0.7
    assert data["formality_level"] == "neutral"


def test_get_preferences(client, test_user_id, user_preference, api_key):
    """Test getting preferences for an existing user."""
    # Make a request with a valid API key
    response = client.get(
        f"/api/v1/preferences/{test_user_id}",
        headers={"X-API-Key": api_key}
    )
    
    # Check that we got a 200 OK response
    assert response.status_code == 200
    
    # Check that the response contains the correct preferences
    data = response.json()
    assert data["user_id"] == test_user_id
    assert data["preferred_model"] == user_preference.preferred_model
    assert data["temperature"] == user_preference.temperature
    assert data["default_tone"] == user_preference.default_tone
    assert data["formality_level"] == user_preference.formality_level
    assert data["check_grammar"] == user_preference.check_grammar
    assert data["check_style"] == user_preference.check_style
    assert data["check_spelling"] == user_preference.check_spelling


def test_update_preferences_unauthorized(client, test_user_id, test_preferences, api_key):
    """Test updating preferences without authentication."""
    # Make a request without an API key
    response = client.put(
        f"/api/v1/preferences/{test_user_id}",
        json=test_preferences
    )
    
    # Check that we got a 401 Unauthorized response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_create_preferences(client, test_user_id, test_preferences, api_key, db):
    """Test creating preferences for a new user."""
    # Make a request with a valid API key
    response = client.put(
        f"/api/v1/preferences/{test_user_id}",
        json=test_preferences,
        headers={"X-API-Key": api_key}
    )
    
    # Check that we got a 200 OK response
    assert response.status_code == 200
    
    # Check that the response contains the correct preferences
    data = response.json()
    assert data["user_id"] == test_user_id
    assert data["preferred_model"] == test_preferences["preferred_model"]
    assert data["temperature"] == test_preferences["temperature"]
    assert data["default_tone"] == test_preferences["default_tone"]
    assert data["formality_level"] == test_preferences["formality_level"]
    assert data["check_grammar"] == test_preferences["check_grammar"]
    assert data["check_style"] == test_preferences["check_style"]
    assert data["check_spelling"] == test_preferences["check_spelling"]
    
    # Check that the preferences were saved to the database
    db_preferences = db.query(UserPreference).filter(
        UserPreference.user_id == test_user_id
    ).first()
    assert db_preferences is not None
    assert db_preferences.user_id == test_user_id


def test_update_preferences(client, test_user_id, user_preference, api_key, db):
    """Test updating preferences for an existing user."""
    # Create updated preferences data
    updated_data = {
        "preferred_model": "updated-model",
        "temperature": 0.8,
        "default_tone": "casual"
    }
    
    # Make a request with a valid API key
    response = client.put(
        f"/api/v1/preferences/{test_user_id}",
        json=updated_data,
        headers={"X-API-Key": api_key}
    )
    
    # Check that we got a 200 OK response
    assert response.status_code == 200
    
    # Check that the response contains the updated preferences
    data = response.json()
    assert data["user_id"] == test_user_id
    assert data["preferred_model"] == "updated-model"
    assert data["temperature"] == 0.8
    assert data["default_tone"] == "casual"
    
    # Check that other fields were not changed
    assert data["formality_level"] == user_preference.formality_level
    assert data["check_grammar"] == user_preference.check_grammar
    assert data["check_style"] == user_preference.check_style
    assert data["check_spelling"] == user_preference.check_spelling
    
    # Check that the preferences were updated in the database
    db_preferences = db.query(UserPreference).filter(
        UserPreference.user_id == test_user_id
    ).first()
    assert db_preferences is not None
    assert db_preferences.preferred_model == "updated-model"
    assert db_preferences.temperature == 0.8
    assert db_preferences.default_tone == "casual"


def test_delete_preferences_unauthorized(client, test_user_id, api_key):
    """Test deleting preferences without authentication."""
    # Make a request without an API key
    response = client.delete(f"/api/v1/preferences/{test_user_id}")
    
    # Check that we got a 401 Unauthorized response
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_delete_preferences(client, test_user_id, user_preference, api_key, db):
    """Test deleting preferences for an existing user."""
    # Make a request with a valid API key
    response = client.delete(
        f"/api/v1/preferences/{test_user_id}",
        headers={"X-API-Key": api_key}
    )
    
    # Check that we got a 204 No Content response
    assert response.status_code == 204
    
    # Check that the preferences were deleted from the database
    db_preferences = db.query(UserPreference).filter(
        UserPreference.user_id == test_user_id
    ).first()
    assert db_preferences is None


def test_delete_preferences_not_found(client, api_key):
    """Test deleting preferences for a user that doesn't exist."""
    # Make a request with a valid API key
    response = client.delete(
        "/api/v1/preferences/non-existent-user",
        headers={"X-API-Key": api_key}
    )
    
    # Check that we got a 404 Not Found response
    assert response.status_code == 404
    assert response.json()["detail"] == "Preferences for user non-existent-user not found"
