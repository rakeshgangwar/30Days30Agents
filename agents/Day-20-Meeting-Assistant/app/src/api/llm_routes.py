"""
API routes for LLM operations.

This module provides REST API endpoints for LLM functionality including
meeting summarization and action item extraction.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from loguru import logger

from src.ai.llm_service import (
    LLMService,
    MeetingSummaryRequest,
    ActionItemsRequest,
    LLMProvider
)


# Pydantic models for API requests and responses
class SummarizationRequest(BaseModel):
    """Request model for meeting summarization"""
    transcript: str = Field(..., description="Meeting transcript text", min_length=10)
    meeting_title: Optional[str] = Field(None, description="Optional meeting title")
    participants: Optional[List[str]] = Field(None, description="List of participant names")
    duration_minutes: Optional[int] = Field(None, description="Meeting duration in minutes", gt=0)
    summary_type: str = Field("detailed", description="Summary type: brief, detailed, or executive")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transcript": "John: Good morning everyone. Let's start with the quarterly review...",
                "meeting_title": "Q4 Planning Meeting",
                "participants": ["John", "Sarah", "Mike"],
                "duration_minutes": 60,
                "summary_type": "detailed"
            }
        }


class ActionItemsExtractionRequest(BaseModel):
    """Request model for action items extraction"""
    transcript: str = Field(..., description="Meeting transcript text", min_length=10)
    participants: Optional[List[str]] = Field(None, description="List of participant names")
    context: Optional[str] = Field(None, description="Additional context about the meeting")
    
    class Config:
        json_schema_extra = {
            "example": {
                "transcript": "John: I'll take care of the budget analysis by Friday. Sarah, can you handle the client presentation?",
                "participants": ["John", "Sarah", "Mike"],
                "context": "Project planning meeting for Q4 launch"
            }
        }


class LLMResponse(BaseModel):
    """Response model for LLM operations"""
    content: str = Field(..., description="Generated content")
    provider: str = Field(..., description="LLM provider used")
    model: str = Field(..., description="Model name used")
    tokens_used: Optional[int] = Field(None, description="Number of tokens used")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")


class ActionItem(BaseModel):
    """Action item model"""
    action: str = Field(..., description="Description of the action item")
    assignee: Optional[str] = Field(None, description="Person responsible for the action")
    deadline: Optional[str] = Field(None, description="Deadline for the action")
    priority: str = Field("medium", description="Priority level: high, medium, or low")


class ActionItemsResponse(BaseModel):
    """Response model for action items extraction"""
    action_items: List[ActionItem] = Field(..., description="Extracted action items")
    llm_response: LLMResponse = Field(..., description="Raw LLM response details")


class HealthCheckResponse(BaseModel):
    """Health check response model"""
    openrouter: Dict[str, Any] = Field(..., description="OpenRouter status")
    ollama: Dict[str, Any] = Field(..., description="Ollama status")


class ServiceStatusResponse(BaseModel):
    """Service status response model"""
    use_local_llm: bool = Field(..., description="Whether local LLM is preferred")
    openrouter_available: bool = Field(..., description="Whether OpenRouter is available")
    ollama_available: bool = Field(..., description="Whether Ollama is available")
    default_model: str = Field(..., description="Default model being used")
    openrouter_rate_limits: Optional[Dict[str, Any]] = Field(None, description="OpenRouter rate limit status")


# Create router
router = APIRouter(prefix="/api/llm", tags=["LLM Operations"])


# Dependency to get LLM service
async def get_llm_service() -> LLMService:
    """Get LLM service instance"""
    service = LLMService()
    try:
        yield service
    finally:
        await service.close()


@router.post("/summarize", response_model=LLMResponse)
async def summarize_meeting(
    request: SummarizationRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Generate a meeting summary from transcript text.
    
    This endpoint takes a meeting transcript and generates a summary
    using the configured LLM provider (OpenRouter or Ollama).
    """
    try:
        # Create MeetingSummaryRequest
        summary_request = MeetingSummaryRequest(
            transcript=request.transcript,
            meeting_title=request.meeting_title,
            participants=request.participants,
            duration_minutes=request.duration_minutes,
            summary_type=request.summary_type
        )
        
        # Validate summary type
        if request.summary_type not in ["brief", "detailed", "executive"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Summary type must be 'brief', 'detailed', or 'executive'"
            )
        
        logger.info(f"Processing summarization request - Type: {request.summary_type}")
        
        # Generate summary
        llm_response = await llm_service.summarize_meeting(summary_request)
        
        return LLMResponse(
            content=llm_response.content,
            provider=llm_response.provider.value,
            model=llm_response.model,
            tokens_used=llm_response.tokens_used,
            processing_time=llm_response.processing_time
        )
    
    except ValueError as e:
        logger.error(f"Validation error in summarization: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in meeting summarization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate meeting summary"
        )


@router.post("/extract-action-items", response_model=ActionItemsResponse)
async def extract_action_items(
    request: ActionItemsExtractionRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Extract action items from meeting transcript.
    
    This endpoint analyzes a meeting transcript and extracts actionable items
    including assignees, deadlines, and priorities where mentioned.
    """
    try:
        # Create ActionItemsRequest
        action_items_request = ActionItemsRequest(
            transcript=request.transcript,
            participants=request.participants,
            context=request.context
        )
        
        logger.info("Processing action items extraction request")
        
        # Extract action items
        llm_response = await llm_service.extract_action_items(action_items_request)
        
        # Parse action items
        parsed_items = llm_service.parse_action_items(llm_response)
        
        # Convert to ActionItem models
        action_items = [
            ActionItem(
                action=item["action"],
                assignee=item.get("assignee"),
                deadline=item.get("deadline"),
                priority=item.get("priority", "medium")
            )
            for item in parsed_items
        ]
        
        return ActionItemsResponse(
            action_items=action_items,
            llm_response=LLMResponse(
                content=llm_response.content,
                provider=llm_response.provider.value,
                model=llm_response.model,
                tokens_used=llm_response.tokens_used,
                processing_time=llm_response.processing_time
            )
        )
    
    except ValueError as e:
        logger.error(f"Validation error in action items extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in action items extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract action items"
        )


@router.get("/health", response_model=HealthCheckResponse)
async def llm_health_check(llm_service: LLMService = Depends(get_llm_service)):
    """
    Check the health of all LLM providers.
    
    This endpoint tests connectivity and basic functionality of
    both OpenRouter and Ollama (when available).
    """
    try:
        logger.info("Performing LLM health check")
        health_status = await llm_service.health_check()
        
        return HealthCheckResponse(
            openrouter=health_status["openrouter"],
            ollama=health_status["ollama"]
        )
    
    except Exception as e:
        logger.error(f"Error in LLM health check: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform health check"
        )


@router.get("/status", response_model=ServiceStatusResponse)
async def get_llm_status(llm_service: LLMService = Depends(get_llm_service)):
    """
    Get the current status of the LLM service.
    
    This endpoint provides information about available providers,
    configuration, and rate limiting status.
    """
    try:
        logger.debug("Getting LLM service status")
        status = llm_service.get_status()
        
        return ServiceStatusResponse(
            use_local_llm=status["use_local_llm"],
            openrouter_available=status["openrouter_available"],
            ollama_available=status["ollama_available"],
            default_model=status["default_model"],
            openrouter_rate_limits=status.get("openrouter_rate_limits")
        )
    
    except Exception as e:
        logger.error(f"Error getting LLM status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get service status"
        )


@router.post("/test")
async def test_llm_connection(llm_service: LLMService = Depends(get_llm_service)):
    """
    Test LLM connection with a simple prompt.
    
    This endpoint sends a simple test prompt to verify that the LLM
    service is working correctly.
    """
    try:
        logger.info("Testing LLM connection")
        
        # Create a simple test request
        test_request = MeetingSummaryRequest(
            transcript="This is a test meeting transcript. John said hello to everyone.",
            summary_type="brief"
        )
        
        # Generate test summary
        response = await llm_service.summarize_meeting(test_request)
        
        return {
            "status": "success",
            "provider": response.provider.value,
            "model": response.model,
            "response_length": len(response.content),
            "processing_time": response.processing_time,
            "tokens_used": response.tokens_used
        }
    
    except Exception as e:
        logger.error(f"LLM connection test failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM connection test failed: {str(e)}"
        )