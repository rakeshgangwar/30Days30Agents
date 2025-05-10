"""
Tests for the preferences service.
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import SQLAlchemyError

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.services.preferences_service import PreferencesService
from app.models.preferences import UserPreference


def test_get_user_preferences(db, test_user_id, user_preference, test_preferences):
    """Test getting user preferences."""
    # Create a preferences service
    service = PreferencesService()
    
    # Get the preferences
    preferences = service.get_user_preferences(db, test_user_id)
    
    # Check that we got the correct preferences
    assert preferences is not None
    assert preferences["user_id"] == test_user_id
    assert preferences["preferred_model"] == test_preferences["preferred_model"]
    assert preferences["temperature"] == test_preferences["temperature"]
    assert preferences["default_tone"] == test_preferences["default_tone"]
    assert preferences["formality_level"] == test_preferences["formality_level"]
    assert preferences["check_grammar"] == test_preferences["check_grammar"]
    assert preferences["check_style"] == test_preferences["check_style"]
    assert preferences["check_spelling"] == test_preferences["check_spelling"]
    assert preferences["extra_settings"] == test_preferences["extra_settings"]


def test_get_user_preferences_not_found(db):
    """Test getting preferences for a user that doesn't exist."""
    # Create a preferences service
    service = PreferencesService()
    
    # Get preferences for a non-existent user
    preferences = service.get_user_preferences(db, "non-existent-user")
    
    # Check that we got None
    assert preferences is None


def test_get_user_preferences_error(db):
    """Test error handling when getting user preferences."""
    # Create a preferences service
    service = PreferencesService()
    
    # Mock the database query to raise an exception
    with patch.object(db, "query", side_effect=SQLAlchemyError("Test error")):
        # Attempt to get preferences
        with pytest.raises(SQLAlchemyError):
            service.get_user_preferences(db, "test-user")


def test_create_preferences(db, test_user_id, test_preferences):
    """Test creating new user preferences."""
    # Create a preferences service
    service = PreferencesService()
    
    # Create new preferences
    preferences = service.create_or_update_preferences(db, test_user_id, test_preferences)
    
    # Check that the preferences were created correctly
    assert preferences is not None
    assert preferences["user_id"] == test_user_id
    assert preferences["preferred_model"] == test_preferences["preferred_model"]
    assert preferences["temperature"] == test_preferences["temperature"]
    assert preferences["default_tone"] == test_preferences["default_tone"]
    assert preferences["formality_level"] == test_preferences["formality_level"]
    assert preferences["check_grammar"] == test_preferences["check_grammar"]
    assert preferences["check_style"] == test_preferences["check_style"]
    assert preferences["check_spelling"] == test_preferences["check_spelling"]
    assert preferences["extra_settings"] == test_preferences["extra_settings"]
    
    # Check that the preferences were saved to the database
    db_preferences = db.query(UserPreference).filter(
        UserPreference.user_id == test_user_id
    ).first()
    assert db_preferences is not None
    assert db_preferences.user_id == test_user_id


def test_update_preferences(db, test_user_id, user_preference):
    """Test updating existing user preferences."""
    # Create a preferences service
    service = PreferencesService()
    
    # Update preferences
    updated_data = {
        "preferred_model": "updated-model",
        "temperature": 0.8,
        "default_tone": "casual"
    }
    preferences = service.create_or_update_preferences(db, test_user_id, updated_data)
    
    # Check that the preferences were updated correctly
    assert preferences is not None
    assert preferences["user_id"] == test_user_id
    assert preferences["preferred_model"] == "updated-model"
    assert preferences["temperature"] == 0.8
    assert preferences["default_tone"] == "casual"
    
    # Check that other fields were not changed
    assert preferences["formality_level"] == user_preference.formality_level
    assert preferences["check_grammar"] == user_preference.check_grammar
    assert preferences["check_style"] == user_preference.check_style
    assert preferences["check_spelling"] == user_preference.check_spelling
    assert preferences["extra_settings"] == user_preference.extra_settings


def test_create_or_update_preferences_error(db, test_user_id, test_preferences):
    """Test error handling when creating or updating preferences."""
    # Create a preferences service
    service = PreferencesService()
    
    # Mock the database query to raise an exception
    with patch.object(db, "query", side_effect=SQLAlchemyError("Test error")):
        # Attempt to create or update preferences
        with pytest.raises(SQLAlchemyError):
            service.create_or_update_preferences(db, test_user_id, test_preferences)


def test_delete_user_preferences(db, test_user_id, user_preference):
    """Test deleting user preferences."""
    # Create a preferences service
    service = PreferencesService()
    
    # Delete the preferences
    result = service.delete_user_preferences(db, test_user_id)
    
    # Check that the preferences were deleted
    assert result is True
    
    # Check that the preferences were removed from the database
    db_preferences = db.query(UserPreference).filter(
        UserPreference.user_id == test_user_id
    ).first()
    assert db_preferences is None


def test_delete_user_preferences_not_found(db):
    """Test deleting preferences for a user that doesn't exist."""
    # Create a preferences service
    service = PreferencesService()
    
    # Delete preferences for a non-existent user
    result = service.delete_user_preferences(db, "non-existent-user")
    
    # Check that the result is False
    assert result is False


def test_delete_user_preferences_error(db, test_user_id, user_preference):
    """Test error handling when deleting user preferences."""
    # Create a preferences service
    service = PreferencesService()
    
    # Mock the database query to raise an exception
    with patch.object(db, "query", side_effect=SQLAlchemyError("Test error")):
        # Attempt to delete preferences
        with pytest.raises(SQLAlchemyError):
            service.delete_user_preferences(db, test_user_id)


def test_get_default_preferences():
    """Test getting default preferences."""
    # Create a preferences service
    service = PreferencesService()
    
    # Get default preferences
    preferences = service.get_default_preferences()
    
    # Check that we got the correct default preferences
    assert preferences is not None
    assert preferences["preferred_model"] is None
    assert preferences["temperature"] == 0.7
    assert preferences["default_tone"] is None
    assert preferences["formality_level"] == "neutral"
    assert preferences["check_grammar"] is True
    assert preferences["check_style"] is True
    assert preferences["check_spelling"] is True
    assert preferences["extra_settings"] is None
