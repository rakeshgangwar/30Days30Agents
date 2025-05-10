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

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.openrouter_service import openrouter_service
from app.db.database import get_db

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
    temperature: Optional[float] = None
    user_id: Optional[str] = None


class GrammarAnalysisResponse(BaseModel):
    """Response model for grammar and style analysis."""

    issues: List[GrammarIssue] = Field(default_factory=list)
    model_used: str
    improved_text: Optional[str] = None
    raw_analysis: Optional[str] = None


@router.post("/analyze_grammar_style", response_model=GrammarAnalysisResponse)
async def analyze_grammar_style(request: GrammarAnalysisRequest, db: Session = Depends(get_db)):
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
            model=request.model,
            temperature=request.temperature,
            db=db,
            user_id=request.user_id
        )

        # Parse the raw analysis from the LLM
        raw_analysis = analysis_result.get("raw_analysis", "")
        issues = []
        improved_text = request.text  # Default to original text if parsing fails

        try:
            # Try to extract JSON from the response
            # The LLM might include markdown formatting or explanatory text
            import re

            # First, try to parse the entire response as JSON
            try:
                analysis_data = json.loads(raw_analysis)
                json_match = True  # Set a flag to indicate we found valid JSON
            except json.JSONDecodeError:
                # If that fails, try to extract JSON using regex patterns
                json_match = re.search(r'```json\s*([\s\S]*?)\s*```|(\{[\s\S]*\})', raw_analysis)

            if json_match:
                # If json_match is a boolean (True), we've already parsed the JSON
                if not isinstance(json_match, bool):
                    json_str = json_match.group(1) or json_match.group(2)
                    analysis_data = json.loads(json_str)

                # Extract issues
                if "issues" in analysis_data and isinstance(analysis_data["issues"], list):
                    for issue_data in analysis_data["issues"]:
                        issues.append(GrammarIssue(
                            type=issue_data.get("type", "unknown"),
                            description=issue_data.get("description", "No description provided"),
                            suggestion=issue_data.get("suggestion", "No suggestion provided"),
                            severity=issue_data.get("severity", "medium")
                        ))

                # Extract improved text
                if "improved_text" in analysis_data and isinstance(analysis_data["improved_text"], str):
                    improved_text = analysis_data["improved_text"]
            else:
                # If no JSON found, try to extract improved text directly
                improved_match = re.search(r'improved_text["\s:]+([^"]+)["\s]', raw_analysis, re.IGNORECASE)
                if improved_match:
                    improved_text = improved_match.group(1)

            logger.info(f"Parsed {len(issues)} issues from grammar analysis")

        except Exception as e:
            logger.error(f"Error parsing grammar analysis: {str(e)}")
            # Continue with empty issues and original text

        # If no issues were found but the improved text is different, create a generic issue
        if not issues and improved_text != request.text:
            issues.append(GrammarIssue(
                type="grammar",
                description="Grammar or style issues were found and corrected.",
                suggestion="See improved text for corrections.",
                severity="medium"
            ))

        return GrammarAnalysisResponse(
            issues=issues,
            model_used=analysis_result.get("model_used", settings.DEFAULT_LLM_MODEL),
            improved_text=improved_text,
            raw_analysis=raw_analysis
        )

    except Exception as e:
        logger.error(f"Error analyzing grammar: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while analyzing the text."
        )