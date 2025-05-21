"""
Auth Schemas Module

This module provides Pydantic schemas for authentication.
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base schema for user data."""
    email: EmailStr = Field(..., description="User's email address")
    full_name: Optional[str] = Field(None, description="User's full name")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., description="User's password", min_length=8)


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserResponse(UserBase):
    """Schema for user response data."""
    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Whether the user is active")
    is_superuser: bool = Field(..., description="Whether the user is a superuser")

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for access token."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Token type")


class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: Optional[int] = Field(None, description="Subject (user ID)")
