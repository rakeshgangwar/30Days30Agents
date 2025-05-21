"""
Persona Schemas Module

This module provides Pydantic schemas for personas.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PersonaBase(BaseModel):
    """Base schema for persona data."""

    name: str = Field(..., description="Name of the persona", example="Tech Guru")
    background: Optional[str] = Field(None, description="Background story of the persona", example="A technology enthusiast with 15 years of experience in Silicon Valley.")
    interests: Optional[List[str]] = Field(None, description="List of interests", example=["AI", "Blockchain", "IoT"])
    values: Optional[List[str]] = Field(None, description="List of values", example=["Innovation", "Education", "Ethics"])
    tone: Optional[str] = Field(None, description="Tone of voice", example="Professional but approachable")
    expertise: Optional[List[str]] = Field(None, description="List of areas of expertise", example=["Machine Learning", "Cloud Computing", "Data Science"])
    purpose: Optional[str] = Field(None, description="Purpose of the persona", example="To share insights about emerging technologies and their impact on society.")
    avatar_url: Optional[str] = Field(None, description="URL to the persona's avatar image", example="https://example.com/avatar.jpg")
    is_active: Optional[bool] = Field(True, description="Whether the persona is active")


class PersonaCreate(PersonaBase):
    """Schema for creating a new persona."""
    pass


class PersonaUpdate(BaseModel):
    """Schema for updating an existing persona."""

    name: Optional[str] = Field(None, description="Name of the persona", example="Tech Guru")
    background: Optional[str] = Field(None, description="Background story of the persona", example="A technology enthusiast with 15 years of experience in Silicon Valley.")
    interests: Optional[List[str]] = Field(None, description="List of interests", example=["AI", "Blockchain", "IoT"])
    values: Optional[List[str]] = Field(None, description="List of values", example=["Innovation", "Education", "Ethics"])
    tone: Optional[str] = Field(None, description="Tone of voice", example="Professional but approachable")
    expertise: Optional[List[str]] = Field(None, description="List of areas of expertise", example=["Machine Learning", "Cloud Computing", "Data Science"])
    purpose: Optional[str] = Field(None, description="Purpose of the persona", example="To share insights about emerging technologies and their impact on society.")
    avatar_url: Optional[str] = Field(None, description="URL to the persona's avatar image", example="https://example.com/avatar.jpg")
    is_active: Optional[bool] = Field(None, description="Whether the persona is active")


class PersonaResponse(PersonaBase):
    """Schema for persona response data."""

    id: int = Field(..., description="Unique identifier for the persona")
    created_at: datetime = Field(..., description="When the persona was created")
    updated_at: datetime = Field(..., description="When the persona was last updated")

    model_config = {
        "from_attributes": True
    }


class PersonaList(BaseModel):
    """Schema for a list of personas."""

    items: List[PersonaResponse] = Field(..., description="List of personas")
    total: int = Field(..., description="Total number of personas")
    skip: int = Field(..., description="Number of personas skipped")
    limit: int = Field(..., description="Maximum number of personas returned")
