"""
Resource model for the Learning Coach Agent.
"""

from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Float
from sqlalchemy.orm import relationship

from app.db.base import Base


class Resource(Base):
    """Resource model."""
    
    __tablename__ = "resources"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    url = Column(String)
    type = Column(String)  # article, video, course, etc.
    description = Column(String)
    difficulty = Column(String)  # beginner, intermediate, advanced
    estimated_time = Column(String)
    topics = Column(JSON, default=[])
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="resources")
