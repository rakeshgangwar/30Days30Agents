"""
Interaction database model.

This module provides the database model for tracking interactions
from social media platforms.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Interaction(Base):
    """
    Database model for interactions.
    
    This model stores interactions like mentions, replies, comments, etc.
    from social media platforms for digital personas.
    """
    
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id", ondelete="CASCADE"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), nullable=True)
    platform = Column(String, nullable=False, index=True)
    external_id = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False, index=True)  # mention, reply, comment, direct_message, etc.
    content_text = Column(Text, nullable=False)  # Renamed from 'content' to avoid conflict with relationship
    author_data = Column(JSON, nullable=False)  # User who created the interaction
    status = Column(String, nullable=False, default="pending", index=True)  # pending, responded, ignored
    response = Column(Text, nullable=True)  # Our response to the interaction
    platform_data = Column(JSON, nullable=True)  # Additional platform-specific data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    responded_at = Column(DateTime, nullable=True)
    # Relationships
    persona = relationship("Persona", back_populates="interactions")
    content = relationship("Content", back_populates="interactions")
    persona = relationship("Persona", back_populates="interactions")
    
    def __init__(self,
                 persona_id: int,
                 platform: str,
                 external_id: str,
                 type: str,
                 content_text: str,
                 author_data: Dict[str, Any],
                 content_id: Optional[int] = None,
                 status: str = "pending",
                 response: Optional[str] = None,
                 platform_data: Optional[Dict[str, Any]] = None):
        """
        Initialize an interaction.
        
        Args:
            persona_id: ID of the persona this interaction is for.
            platform: Platform name (e.g., 'twitter', 'linkedin', 'bluesky').
            external_id: External ID of the interaction on the platform.
            type: Type of interaction (e.g., 'mention', 'reply', 'comment').
            content_text: Content of the interaction.
            author_data: Data about the author of the interaction.
            content_id: ID of the content this interaction is related to (optional).
            status: Status of the interaction (default: 'pending').
            response: Optional response to the interaction.
            platform_data: Optional additional platform-specific data.
        """
        self.persona_id = persona_id
        self.platform = platform
        self.external_id = external_id
        self.type = type
        self.content_text = content_text
        self.author_data = author_data
        self.content_id = content_id
        self.status = status
        self.response = response
        self.platform_data = platform_data or {}
