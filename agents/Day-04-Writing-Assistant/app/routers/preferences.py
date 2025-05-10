"""
API router for user preferences.

This module provides API endpoints for managing user preferences.
"""
import os
import sys
import logging
from typing import Dict, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.db.database import get_db
from app.services.preferences_service import preferences_service
from app.api.deps import get_api_key

logger = logging.getLogger(__name__)
router = APIRouter()


class PreferencesBase(BaseModel):
    """Base model for preferences API."""

    preferred_model: Optional[str] = None
    temperature: Optional[float] = 0.7
    default_tone: Optional[str] = None
    formality_level: Optional[str] = "neutral"
    check_grammar: Optional[bool] = True
    check_style: Optional[bool] = True
    check_spelling: Optional[bool] = True
    extra_settings: Optional[Dict[str, Any]] = None


class PreferencesResponse(PreferencesBase):
    """Response model for preferences API."""

    user_id: str

    class Config:
        """Pydantic configuration."""
        from_attributes = True


@router.get("/preferences/{user_id}", response_model=PreferencesResponse)
async def get_preferences(
    user_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """
    Get user preferences.

    Args:
        user_id: User ID to get preferences for
        db: Database session dependency
        api_key: API key for authentication

    Returns:
        User preferences
    """
    logger.info(f"Getting preferences for user: {user_id}")
    preferences = preferences_service.get_user_preferences(db, user_id)

    if not preferences:
        # Return default preferences if none exist
        default_prefs = preferences_service.get_default_preferences()
        default_prefs["user_id"] = user_id
        return default_prefs

    return preferences


@router.put("/preferences/{user_id}", response_model=PreferencesResponse)
async def update_preferences(
    user_id: str,
    preferences: PreferencesBase,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """
    Update user preferences.

    Args:
        user_id: User ID to update preferences for
        preferences: Preferences data to update
        db: Database session dependency
        api_key: API key for authentication

    Returns:
        Updated user preferences
    """
    logger.info(f"Updating preferences for user: {user_id}")

    try:
        updated_prefs = preferences_service.create_or_update_preferences(
            db, user_id, preferences.model_dump(exclude_unset=True)
        )
        return updated_prefs
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences",
        )


@router.delete("/preferences/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preferences(
    user_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """
    Delete user preferences.

    Args:
        user_id: User ID to delete preferences for
        db: Database session dependency
        api_key: API key for authentication

    Returns:
        204 No Content
    """
    logger.info(f"Deleting preferences for user: {user_id}")

    deleted = preferences_service.delete_user_preferences(db, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preferences for user {user_id} not found",
        )