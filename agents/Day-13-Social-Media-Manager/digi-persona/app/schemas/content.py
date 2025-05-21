"""
Content Schemas Module

This module provides Pydantic schemas for content.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, field_validator


class ContentBase(BaseModel):
    """Base schema for content data."""

    content_type: str = Field(..., description="Type of content", example="tweet")
    text: str = Field(..., description="Content text", example="Just launched our new AI product! #AI #Innovation")
    platform: str = Field(..., description="Platform for the content", example="twitter")
    status: Optional[str] = Field("draft", description="Status of the content", example="draft")
    scheduled_time: Optional[datetime] = Field(None, description="When the content is scheduled to be posted")
    media_urls: Optional[List[str]] = Field(None, description="URLs of media attached to the content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the content")


class ContentCreate(ContentBase):
    """Schema for creating new content."""

    persona_id: int = Field(..., description="ID of the persona the content is for")


class ContentUpdate(BaseModel):
    """Schema for updating existing content."""

    content_type: Optional[str] = Field(None, description="Type of content", example="tweet")
    text: Optional[str] = Field(None, description="Content text", example="Just launched our new AI product! #AI #Innovation")
    platform: Optional[str] = Field(None, description="Platform for the content", example="twitter")
    status: Optional[str] = Field(None, description="Status of the content", example="draft")
    scheduled_time: Optional[datetime] = Field(None, description="When the content is scheduled to be posted")
    media_urls: Optional[List[str]] = Field(None, description="URLs of media attached to the content")
    content_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata for the content")


class ContentResponse(ContentBase):
    """Schema for content response data."""

    id: int = Field(..., description="Unique identifier for the content")
    persona_id: int = Field(..., description="ID of the persona the content is for")
    external_id: Optional[str] = Field(None, description="ID of the content on the platform")
    published_time: Optional[datetime] = Field(None, description="When the content was published")
    created_at: datetime = Field(..., description="When the content was created")
    updated_at: datetime = Field(..., description="When the content was last updated")
    metadata: Optional[Dict[str, Any]] = None

    model_config = {
        "from_attributes": True
    }

    @field_validator('metadata', mode='after')
    def set_metadata(cls, v, info):
        if v is None and hasattr(info.data, 'content_metadata'):
            # Return the content_metadata directly
            return info.data.content_metadata if info.data.content_metadata is not None else {}
        return v if v is not None else {}


class ContentList(BaseModel):
    """Schema for a list of content items."""

    items: List[ContentResponse] = Field(..., description="List of content items")
    total: int = Field(..., description="Total number of content items")
    skip: int = Field(..., description="Number of content items skipped")
    limit: int = Field(..., description="Maximum number of content items returned")

    model_config = {
        "from_attributes": True
    }


class ContentGenerateRequest(BaseModel):
    """Schema for content generation request."""

    persona_id: int = Field(..., description="ID of the persona to generate content for")
    content_type: str = Field(..., description="Type of content to generate", example="tweet")
    topic: str = Field(..., description="Topic to generate content about", example="artificial intelligence")
    platform: str = Field(..., description="Platform to generate content for", example="twitter")
    additional_context: Optional[str] = Field(None, description="Additional context for generation")
    max_length: Optional[int] = Field(None, description="Maximum length of the generated content")
    save: Optional[bool] = Field(True, description="Whether to save the generated content to the database")


class ContentGenerateResponse(BaseModel):
    """Schema for content generation response."""

    id: Optional[int] = Field(None, description="ID of the generated content (if saved)")
    persona_id: int = Field(..., description="ID of the persona the content is for")
    content_type: str = Field(..., description="Type of content", example="tweet")
    text: str = Field(..., description="Generated content text")
    platform: str = Field(..., description="Platform for the content", example="twitter")
    status: str = Field(..., description="Status of the content", example="draft")
    content_metadata: Dict[str, Any] = Field(..., description="Metadata for the generated content")


class ContentScheduleRequest(BaseModel):
    """Schema for content scheduling request."""

    scheduled_time: datetime = Field(..., description="When to schedule the content for posting")


class ContentScheduleResponse(ContentResponse):
    """Schema for content scheduling response."""
    pass


class ContentBatchScheduleRequest(BaseModel):
    """Schema for batch content scheduling request."""

    content_ids: List[int] = Field(..., description="List of content IDs to schedule")
    start_time: datetime = Field(..., description="When to schedule the first content for posting")
    interval_minutes: int = Field(60, description="Minutes between each scheduled content")
    use_celery: bool = Field(False, description="Whether to use Celery for background processing")


class ContentGenerateScheduleRequest(BaseModel):
    """Schema for content generation and scheduling request."""

    persona_id: int = Field(..., description="ID of the persona to generate content for")
    content_type: str = Field(..., description="Type of content to generate", example="tweet")
    topic: str = Field(..., description="Topic to generate content about", example="artificial intelligence")
    platform: str = Field(..., description="Platform to generate content for", example="twitter")
    scheduled_time: datetime = Field(..., description="When to schedule the content for posting")
    additional_context: Optional[str] = Field(None, description="Additional context for generation")
    max_length: Optional[int] = Field(None, description="Maximum length of the generated content")
    use_celery: bool = Field(False, description="Whether to use Celery for background processing")


class ContentBatchGenerateScheduleRequest(BaseModel):
    """Schema for batch content generation and scheduling request."""

    persona_id: int = Field(..., description="ID of the persona to generate content for")
    content_type: str = Field(..., description="Type of content to generate", example="tweet")
    topics: List[str] = Field(..., description="List of topics to generate content about")
    platform: str = Field(..., description="Platform to generate content for", example="twitter")
    start_time: datetime = Field(..., description="When to schedule the first content for posting")
    interval_minutes: int = Field(60, description="Minutes between each scheduled content")
    additional_context: Optional[str] = Field(None, description="Additional context for generation")
    max_length: Optional[int] = Field(None, description="Maximum length of the generated content")
    use_celery: bool = Field(False, description="Whether to use Celery for background processing")


class TaskResponse(BaseModel):
    """Schema for task response."""

    task_id: str = Field(..., description="ID of the scheduled task")
    status: str = Field(..., description="Status of the task")


class Suggestion(BaseModel):
    """Schema for a content suggestion."""

    id: str = Field(..., description="Unique identifier for the suggestion")
    text: str = Field(..., description="The suggestion text")
    type: str = Field(..., description="Type of suggestion (improve, tone, hashtags, engagement)")
    description: Optional[str] = Field(None, description="Description of the suggestion")


class ContentSuggestionRequest(BaseModel):
    """Schema for content suggestion request."""

    content: str = Field(..., description="The content to get suggestions for")
    suggestion_type: str = Field(..., description="Type of suggestions to generate (improve, tone, hashtags, engagement)")
    persona_id: Optional[int] = Field(None, description="ID of the persona to generate suggestions for")
    content_type: Optional[str] = Field(None, description="Type of content")
    platform: Optional[str] = Field(None, description="Platform the content is for")


class ContentSuggestionResponse(BaseModel):
    """Schema for content suggestion response."""

    suggestions: List[Suggestion] = Field(default_factory=list, description="List of suggestions")


class ApplySuggestionRequest(BaseModel):
    """Schema for applying a suggestion to content."""

    content: str = Field(..., description="The original content")
    suggestion: str = Field(..., description="The suggestion to apply")
    persona_id: Optional[int] = Field(None, description="ID of the persona to generate content for")
    content_type: Optional[str] = Field(None, description="Type of content")
    platform: Optional[str] = Field(None, description="Platform the content is for")
    feedback: Optional[str] = Field(None, description="User feedback to guide the AI in modifying the content")


class ApplySuggestionResponse(BaseModel):
    """Schema for apply suggestion response."""

    improved_content: str = Field(..., description="The improved content with the suggestion applied")
