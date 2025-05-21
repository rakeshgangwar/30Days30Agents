"""Content Database Model

This module provides the database model for content items.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Content(Base):
    """
    Database model for content items.

    A content item represents a piece of content (tweet, post, article, etc.)
    created for a specific persona and platform.
    """

    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False, index=True)
    content_type = Column(String, nullable=False, index=True)  # tweet, post, article, etc.
    text = Column(Text, nullable=False)
    platform = Column(String, nullable=False, index=True)  # twitter, linkedin, bluesky
    status = Column(String, nullable=False, default="draft", index=True)  # draft, pending_review, approved, published
    scheduled_time = Column(DateTime, nullable=True, index=True)
    published_time = Column(DateTime, nullable=True)
    external_id = Column(String, nullable=True, index=True)  # ID from the platform
    media_urls = Column(JSON, nullable=True)  # URLs of attached media
    content_metadata = Column(JSON, nullable=True)  # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    persona = relationship("Persona", back_populates="content")
    interactions = relationship("Interaction", back_populates="content", cascade="all, delete-orphan", foreign_keys="[Interaction.content_id]")

    def __repr__(self) -> str:
        """String representation of the content item."""
        return f"<Content {self.id}: {self.content_type} for {self.platform}>"
