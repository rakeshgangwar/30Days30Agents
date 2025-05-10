"""
API router for text summarization functionality.
"""
import logging
from typing import Optional

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


class SummarizeRequest(BaseModel):
    """Request model for text summarization."""

    text: str
    max_length: Optional[int] = Field(default=None, description="Optional maximum length of the summary in characters (no limit if not specified)")
    format: Optional[str] = Field(default="paragraph", description="Format of the summary (paragraph, bullets)")
    focus: Optional[str] = Field(default=None, description="Optional focus area for the summary")
    model: Optional[str] = None
    temperature: Optional[float] = None
    user_id: Optional[str] = None


class SummarizeResponse(BaseModel):
    """Response model for text summarization."""

    summary: str
    model_used: str
    original_length: int
    summary_length: int


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest, db: Session = Depends(get_db)):
    """
    Summarize the provided text.

    This endpoint uses an LLM to generate a concise summary of the
    provided text.
    """
    try:
        logger.info(f"Received summarization request for {len(request.text)} characters")

        # Use the OpenRouter service to generate the summary
        summary = await openrouter_service.summarize(
            text=request.text,
            max_length=request.max_length,
            format=request.format,
            focus=request.focus,
            model=request.model,
            temperature=request.temperature,
            db=db,
            user_id=request.user_id
        )

        return SummarizeResponse(
            summary=summary,
            model_used=request.model or settings.DEFAULT_LLM_MODEL,
            original_length=len(request.text),
            summary_length=len(summary)
        )

    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while summarizing the text."
        )