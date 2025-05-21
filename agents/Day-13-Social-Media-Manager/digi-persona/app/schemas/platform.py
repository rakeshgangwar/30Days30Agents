"""
Platform schemas.

This module provides pydantic schemas for platform-related objects.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field, validator

class PlatformMetrics(BaseModel):
    """Platform metrics model."""
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0

class PlatformConnectionBase(BaseModel):
    """Base platform connection model."""
    platform_name: str
    username: str

class PlatformConnectionCreate(PlatformConnectionBase):
    """Platform connection creation model."""
    credentials: Dict[str, Any] = Field(..., description="Platform-specific credentials")
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform_name": "twitter",
                "username": "@techexpert",
                "credentials": {
                    "api_key": "your_api_key",
                    "api_secret": "your_api_secret",
                    "access_token": "your_access_token",
                    "access_token_secret": "your_access_token_secret"
                }
            }
        }

class PlatformConnectionResponse(PlatformConnectionBase):
    """Platform connection response model."""
    id: int
    persona_id: int
    platform_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    metrics: PlatformMetrics
    
    class Config:
        orm_mode = True

class PlatformConnectionList(BaseModel):
    """Platform connection list model."""
    items: List[PlatformConnectionResponse]
    total: int

class PlatformAccountInfo(BaseModel):
    """Platform account information model."""
    platform_connection_id: int
    platform_name: str
    platform_id: str
    username: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0
    profile_image_url: Optional[str] = None
    
    # Platform-specific fields
    handle: Optional[str] = None  # Twitter, Bluesky
    screen_name: Optional[str] = None  # Twitter
    did: Optional[str] = None  # Bluesky
    vanity_name: Optional[str] = None  # LinkedIn
    
    # Additional platform-specific data
    additional_data: Optional[Dict[str, Any]] = None

class PlatformPostCreate(BaseModel):
    """Platform post creation model."""
    content: str = Field(..., description="Post content")
    media_urls: Optional[List[str]] = Field(None, description="Media URLs to include in the post")
    additional_params: Dict[str, Any] = Field(default_factory=dict, description="Additional platform-specific parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "Hello world from my digital persona!",
                "media_urls": ["https://example.com/image.jpg"],
                "additional_params": {
                    "reply_to": "12345"
                }
            }
        }
        
    @validator('content')
    def content_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('content cannot be empty')
        return v

class PlatformPostResponse(BaseModel):
    """Platform post response model."""
    platform_connection_id: int
    platform_name: str
    created_at: str
    external_id: str
    external_url: Optional[str] = None
    content: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    media: Optional[List[Dict[str, Any]]] = None
    
    # Additional platform-specific data
    additional_data: Optional[Dict[str, Any]] = None