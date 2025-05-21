"""Persona Database Model

This module provides the database model for personas.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Persona(Base):
    """
    Database model for personas.

    A persona represents a virtual human with a specific identity, personality,
    and social media presence.
    """

    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    background = Column(Text, nullable=True)
    interests = Column(JSON, nullable=True)
    values = Column(JSON, nullable=True)
    tone = Column(String, nullable=True)
    expertise = Column(JSON, nullable=True)
    purpose = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    owner = relationship("User", back_populates="personas")
    content = relationship("Content", back_populates="persona", cascade="all, delete-orphan")
    platform_connections = relationship("PlatformConnection", back_populates="persona", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="persona", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of the persona."""
        return f"<Persona {self.name} (ID: {self.id})>"
