"""
Platform database model.

This module provides the database model for platform connections.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class PlatformConnection(Base):
    """
    Database model for platform connections.
    
    This model stores connections to social media platforms for digital personas.
    """
    
    __tablename__ = "platform_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    persona_id = Column(Integer, ForeignKey("personas.id", ondelete="CASCADE"), nullable=False)
    platform_name = Column(String, nullable=False, index=True)
    platform_id = Column(String, nullable=False)
    username = Column(String, nullable=False)
    credentials = Column(JSON, nullable=False)  # Encrypted credentials for the platform
    is_active = Column(Boolean, default=True, nullable=False)
    platform_metadata = Column(JSON, nullable=True)  # Additional platform-specific data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    persona = relationship("Persona", back_populates="platform_connections")
    
    def __init__(self, 
                 persona_id: int, 
                 platform_name: str,
                 platform_id: str,
                 username: str,
                 credentials: Dict[str, Any],
                 is_active: bool = True,
                 platform_metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a platform connection.
        
        Args:
            persona_id: ID of the persona this connection is for.
            platform_name: Name of the platform (e.g., 'twitter', 'linkedin', 'bluesky').
            platform_id: ID of the account on the platform.
            username: Username on the platform.
            credentials: Credentials for the platform (API keys, tokens, etc.).
            is_active: Whether the connection is active.
            platform_metadata: Optional additional platform-specific data.
        """
        self.persona_id = persona_id
        self.platform_name = platform_name
        self.platform_id = platform_id
        self.username = username
        self.credentials = credentials
        self.is_active = is_active
        self.platform_metadata = platform_metadata or {}
