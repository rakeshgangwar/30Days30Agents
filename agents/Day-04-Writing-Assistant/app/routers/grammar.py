"""
API router for grammar and style analysis functionality.
"""
import json
import logging
from typing import Dict, List, Optional, Union

import sys
import os

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.openrouter_service import openrouter_service

logger = logging.getLogger(__name__)
router = APIRouter()


class GrammarIssue(BaseModel):
    """Model for a single grammar or style issue."""
    
    type: str  # grammar, style, spelling, etc.
    position: Optional[tuple[int, int]] = None  # start and end position in text
    suggestion: Optional[str] = None
    description: str
    severity: str  # error, warning, suggestion


class GrammarAnalysisRequest(BaseModel):
    """Request model for grammar and style analysis."""
    
    text: str
    check_grammar: bool = True
    check_style: bool = True
    check_spelling: bool = True
    language: str = "en-US"
    model: Optional[str] = None


class GrammarAnalysisResponse(BaseModel):
    """Response model for grammar and style analysis."""
    
    issues: List[GrammarIssue] = Field(default_factory=list)
    model_used: str
    improved_text: Optional[str] = None
    raw_analysis: Optional[str] = None


@router.post("/analyze_grammar_style", response_model=GrammarAnalysisResponse)
async def analyze_grammar_style(request: GrammarAnalysisRequest):
    """
    Analyze the grammar and style of the provided text.
    
    This endpoint uses an LLM to check the text for grammar, style, and
    spelling issues.
    """
    try:
        logger.info(f"Received grammar analysis request for {len(request.text)} characters")
        
        # Use the OpenRouter service to analyze the text
        analysis_result = await openrouter_service.analyze_grammar_style(
            text=request.text,
            check_grammar=request.check_grammar,
            check_style=request.check_style,
            check_spelling=request.check_spelling,
            model=request.model
        )
        
        # For the MVP, we'll return the raw analysis from the LLM
        # In a production system, we would properly parse the JSON and create structured issues
        # This simplification avoids potential parsing errors in the MVP stage
        
        return GrammarAnalysisResponse(
            issues=[],  # Empty in MVP - in production we would parse these from the response
            model_used=analysis_result.get("model_used", settings.DEFAULT_LLM_MODEL),
            improved_text=None,  # In production, we would extract this from the response
            raw_analysis=analysis_result.get("raw_analysis", "")
        )
    
    except Exception as e:
        logger.error(f"Error analyzing grammar: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while analyzing the text."
        )