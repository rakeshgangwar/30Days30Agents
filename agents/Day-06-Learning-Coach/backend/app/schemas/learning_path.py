"""
Learning Path schemas for the Learning Coach Agent.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class LearningPathBase(BaseModel):
    """Base learning path schema."""
    
    title: str
    description: Optional[str] = None


class LearningPathCreate(LearningPathBase):
    """Learning path creation schema."""
    
    user_id: int
    topics: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    resources: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class LearningPathUpdate(BaseModel):
    """Learning path update schema."""
    
    title: Optional[str] = None
    description: Optional[str] = None
    topics: Optional[List[Dict[str, Any]]] = None
    resources: Optional[List[Dict[str, Any]]] = None
    progress: Optional[Dict[str, Any]] = None


class LearningPathRead(LearningPathBase):
    """Learning path read schema."""
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    topics: List[Dict[str, Any]] = Field(default_factory=list)
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    progress: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic config."""
        
        from_attributes = True
