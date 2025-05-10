"""
API router for text tone adjustment functionality.
"""
import logging
from typing import Dict, List, Optional

import sys
import os

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.openrouter_service import openrouter_service
from app.db.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


class ToneAdjustRequest(BaseModel):
    """Request model for tone adjustment."""
    
    text: str
    target_tone: str = Field(
        description="Target tone for adjustment (e.g., professional, casual, friendly, formal)"
    )
    preserve_meaning: bool = Field(
        default=True,
        description="Whether to prioritize preserving the original meaning"
    )
    strength: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="How strongly to adjust the tone (0.0-1.0)"
    )
    model: Optional[str] = None
    temperature: Optional[float] = None
    user_id: Optional[str] = None


class ToneAdjustResponse(BaseModel):
    """Response model for tone adjustment."""
    
    original_text: str
    adjusted_text: str
    model_used: str
    tone_changes: List[str] = Field(
        default_factory=list,
        description="List of specific tone changes made"
    )


@router.post("/adjust_tone", response_model=ToneAdjustResponse)
async def adjust_tone(request: ToneAdjustRequest, db: Session = Depends(get_db)):
    """
    Adjust the tone of the provided text.
    
    This endpoint uses an LLM to rewrite the input text with the
    specified tone while preserving its meaning.
    """
    try:
        logger.info(
            f"Received tone adjustment request to {request.target_tone} tone "
            f"for {len(request.text)} characters"
        )
        
        # Use the OpenRouter service to adjust the tone
        result = await openrouter_service.adjust_tone(
            text=request.text,
            target_tone=request.target_tone,
            preserve_meaning=request.preserve_meaning,
            strength=request.strength,
            model=request.model,
            temperature=request.temperature,
            db=db,
            user_id=request.user_id
        )
        
        return ToneAdjustResponse(
            original_text=request.text,
            adjusted_text=result.get("adjusted_text", ""),
            model_used=result.get("model_used", settings.DEFAULT_LLM_MODEL),
            tone_changes=[f"Adjusted to {request.target_tone} tone"]
        )
    
    except Exception as e:
        logger.error(f"Error adjusting tone: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while adjusting the tone."
        )