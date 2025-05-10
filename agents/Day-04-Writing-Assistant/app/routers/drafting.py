"""
API router for text drafting functionality.
"""
import logging
from typing import Optional

import sys
import os

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.openrouter_service import openrouter_service
from app.db.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


class DraftRequest(BaseModel):
    """Request model for draft generation."""
    
    prompt: str
    max_length: Optional[int] = 500
    format: Optional[str] = None
    context: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    user_id: Optional[str] = None


class DraftResponse(BaseModel):
    """Response model for draft generation."""
    
    text: str
    model_used: str


@router.post("/draft", response_model=DraftResponse)
async def create_draft(request: DraftRequest, db: Session = Depends(get_db)):
    """
    Generate a draft based on the provided prompt.
    
    This endpoint uses an LLM to generate text based on the user's prompt
    and any provided context.
    """
    try:
        logger.info(f"Received draft request with prompt: {request.prompt[:50]}...")
        
        # Combine context with prompt if provided
        prompt = request.prompt
        if request.context:
            prompt = f"Context: {request.context}\n\nPrompt: {request.prompt}"
        
        # Generate the draft using the OpenRouter service
        generated_text = await openrouter_service.generate_draft(
            prompt=prompt,
            max_length=request.max_length,
            model=request.model,
            temperature=request.temperature,
            db=db,
            user_id=request.user_id
        )
        
        # Return the generated text
        return DraftResponse(
            text=generated_text,
            model_used=request.model or settings.DEFAULT_LLM_MODEL
        )
    
    except Exception as e:
        logger.error(f"Error generating draft: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while generating the draft."
        )