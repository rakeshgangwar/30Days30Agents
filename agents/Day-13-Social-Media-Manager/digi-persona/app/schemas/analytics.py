"""
Analytics Schemas Module

This module provides schemas for analytics data.
"""

from enum import Enum
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field


class AnalyticsTimeRange(str, Enum):
    """Time range for analytics data."""
    
    ONE_WEEK = "1w"
    TWO_WEEKS = "2w"
    ONE_MONTH = "1m"
    THREE_MONTHS = "3m"


class EngagementDataPoint(BaseModel):
    """Schema for a single engagement data point."""
    
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    twitter: Optional[int] = Field(0, description="Twitter engagement count")
    linkedin: Optional[int] = Field(0, description="LinkedIn engagement count")
    bluesky: Optional[int] = Field(0, description="Bluesky engagement count")


class EngagementData(BaseModel):
    """Schema for engagement data over time."""
    
    data: List[Dict[str, Any]] = Field(..., description="Engagement data points")


class ContentTypeItem(BaseModel):
    """Schema for a content type item."""
    
    name: str = Field(..., description="Content type name")
    value: int = Field(..., description="Content count")


class ContentTypeData(BaseModel):
    """Schema for content distribution by type."""
    
    data: List[ContentTypeItem] = Field(..., description="Content type distribution")


class InteractionTypeItem(BaseModel):
    """Schema for an interaction type item."""
    
    name: str = Field(..., description="Interaction type name")
    value: int = Field(..., description="Interaction count")


class InteractionTypeData(BaseModel):
    """Schema for interaction distribution by type."""
    
    data: List[InteractionTypeItem] = Field(..., description="Interaction type distribution")


class PlatformItem(BaseModel):
    """Schema for a platform performance item."""
    
    name: str = Field(..., description="Platform name")
    posts: int = Field(..., description="Number of posts")
    engagement: int = Field(..., description="Engagement count")
    followers: int = Field(..., description="Follower count")


class PlatformData(BaseModel):
    """Schema for platform performance data."""
    
    data: List[PlatformItem] = Field(..., description="Platform performance data")


class PersonaPerformanceItem(BaseModel):
    """Schema for a persona performance item."""
    
    id: int = Field(..., description="Persona ID")
    name: str = Field(..., description="Persona name")
    avatar: Optional[str] = Field(None, description="Persona avatar URL")
    posts: int = Field(..., description="Number of posts")
    engagement: int = Field(..., description="Engagement count")
    followers: int = Field(..., description="Follower count")


class PersonaPerformanceData(BaseModel):
    """Schema for persona performance data."""
    
    data: List[PersonaPerformanceItem] = Field(..., description="Persona performance data")


class AnalyticsResponse(BaseModel):
    """Schema for the complete analytics dashboard response."""
    
    engagement: List[Dict[str, Any]] = Field(..., description="Engagement data over time")
    content_types: List[ContentTypeItem] = Field(..., description="Content type distribution")
    interaction_types: List[InteractionTypeItem] = Field(..., description="Interaction type distribution")
    platforms: List[PlatformItem] = Field(..., description="Platform performance data")
    personas: List[PersonaPerformanceItem] = Field(..., description="Persona performance data")
