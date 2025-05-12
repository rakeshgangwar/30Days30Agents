"""
User schemas for the Learning Coach Agent.
"""

from typing import Dict, List, Optional, Any

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""
    
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema."""
    
    password: str


class UserUpdate(BaseModel):
    """User update schema."""
    
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    learning_styles: Optional[List[str]] = None
    interests: Optional[List[str]] = None


class UserRead(UserBase):
    """User read schema."""
    
    id: int
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    learning_styles: Optional[List[str]] = Field(default_factory=list)
    interests: Optional[List[str]] = Field(default_factory=list)
    
    class Config:
        """Pydantic config."""
        
        from_attributes = True
