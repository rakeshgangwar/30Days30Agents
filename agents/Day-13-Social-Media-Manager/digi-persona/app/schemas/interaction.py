"""
Interaction schemas.

This module provides pydantic schemas for interaction-related objects.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

class InteractionBase(BaseModel):
    """Base interaction model."""
    platform: str
    external_id: str
    type: str
    content: str
    author_data: Dict[str, Any] = Field(..., alias="author")
    platform_data: Dict[str, Any] = {}

class InteractionCreate(InteractionBase):
    """Interaction creation model."""
    persona_id: int
    
    class Config:
        allow_population_by_field_name = True
        json_schema_extra = {
            "example": {
                "persona_id": 1,
                "platform": "twitter",
                "external_id": "12345",
                "type": "mention",
                "content": "@techexpert What do you think about the new AI regulations?",
                "author": {
                    "id": "67890",
                    "name": "John Smith",
                    "screen_name": "@johnsmith",
                    "profile_image_url": "https://example.com/profile.jpg"
                }
            }
        }

class InteractionResponse(InteractionBase):
    """Interaction response model."""
    id: int
    persona_id: int
    status: str
    response: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    responded_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class InteractionList(BaseModel):
    """Interaction list model."""
    items: List[InteractionResponse]
    total: int
    skip: int
    limit: int

class InteractionResponseCreate(BaseModel):
    """Interaction response creation model."""
    content: str = Field(..., description="Response content")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Thank you for mentioning me! The new AI regulations are indeed a significant development."
            }
        }

class InteractionResponseResponse(BaseModel):
    """Interaction response response model."""
    interaction_id: int
    platform: str
    content: str
    external_id: str
    created_at: Optional[str] = None
    platform_data: Dict[str, Any] = {}

class InteractionFilter(BaseModel):
    """Interaction filter model."""
    persona_id: Optional[int] = Field(None, description="Filter by persona ID")
    platform: Optional[str] = Field(None, description="Filter by platform")
    status: Optional[str] = Field(None, description="Filter by status (pending, responded)")
    type: Optional[str] = Field(None, description="Filter by type (mention, reply, comment, etc.)")
    author_name: Optional[str] = Field(None, description="Filter by author name")
    content_contains: Optional[str] = Field(None, description="Filter by content containing text")
    created_after: Optional[datetime] = Field(None, description="Filter by created after date")
    created_before: Optional[datetime] = Field(None, description="Filter by created before date")
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field("desc", description="Sort order (asc, desc)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "persona_id": 1,
                "platform": "twitter",
                "status": "pending",
                "type": "mention",
                "author_name": "John",
                "content_contains": "AI",
                "created_after": "2023-01-01T00:00:00Z",
                "created_before": "2023-12-31T23:59:59Z",
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }