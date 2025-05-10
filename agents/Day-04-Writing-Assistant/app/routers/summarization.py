"""
API router for text summarization functionality.
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from core.config import settings
from services.openrouter_service import openrouter_service

logger = logging.getLogger(__name__)
router = APIRouter()


class SummarizeRequest(BaseModel):
    """Request model for text summarization."""
    
    text: str
    max_length: Optional[int] = Field(default=200, description="Maximum length of the summary in characters")
    format: Optional[str] = Field(default="paragraph", description="Format of the summary (paragraph, bullets)")
    focus: Optional[str] = Field(default=None, description="Optional focus area for the summary")
    model: Optional[str] = None


class SummarizeResponse(BaseModel):
    """Response model for text summarization."""
    
    summary: str
    model_used: str
    original_length: int
    summary_length: int


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
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
            model=request.model
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