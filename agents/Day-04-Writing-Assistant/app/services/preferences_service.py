"""
User preferences service module.

This module provides functionality for managing user preferences.
"""
import os
import sys
import logging
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.models.preferences import UserPreference

logger = logging.getLogger(__name__)


class PreferencesService:
    """Service for managing user preferences."""

    def get_user_preferences(self, db: Session, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user's preferences.
        
        Args:
            db: Database session
            user_id: Unique identifier for the user
            
        Returns:
            User preferences dictionary or None if not found
        """
        try:
            preferences = db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            if preferences:
                return preferences.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error retrieving preferences for user {user_id}: {str(e)}")
            raise
    
    def create_or_update_preferences(
        self, db: Session, user_id: str, preferences_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create or update user preferences.
        
        Args:
            db: Database session
            user_id: Unique identifier for the user
            preferences_data: Dictionary of preference settings to update
            
        Returns:
            Updated user preferences dictionary
        """
        try:
            # Check if user preferences exist
            preferences = db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            if preferences:
                # Update existing preferences
                for key, value in preferences_data.items():
                    if hasattr(preferences, key):
                        setattr(preferences, key, value)
                
                db.commit()
                db.refresh(preferences)
                return preferences.to_dict()
            else:
                # Create new preferences
                new_preferences = UserPreference(
                    user_id=user_id,
                    **{k: v for k, v in preferences_data.items() if hasattr(UserPreference, k)}
                )
                db.add(new_preferences)
                db.commit()
                db.refresh(new_preferences)
                return new_preferences.to_dict()
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating preferences for user {user_id}: {str(e)}")
            raise
    
    def delete_user_preferences(self, db: Session, user_id: str) -> bool:
        """
        Delete a user's preferences.
        
        Args:
            db: Database session
            user_id: Unique identifier for the user
            
        Returns:
            True if preferences were deleted, False otherwise
        """
        try:
            preferences = db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            if preferences:
                db.delete(preferences)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting preferences for user {user_id}: {str(e)}")
            raise
    
    def get_default_preferences(self) -> Dict[str, Any]:
        """
        Get default preferences.
        
        Returns:
            Dictionary of default preference settings
        """
        return {
            "preferred_model": None,
            "temperature": 0.7,
            "default_tone": None,
            "formality_level": "neutral",
            "check_grammar": True,
            "check_style": True,
            "check_spelling": True,
            "extra_settings": None,
        }


# Singleton instance for use throughout the application
preferences_service = PreferencesService()