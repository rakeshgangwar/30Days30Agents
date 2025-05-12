"""
Learning Path model for the Learning Coach Agent.
"""

from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class LearningPath(Base):
    """Learning Path model."""
    
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    topics = Column(JSON, default=[])
    resources = Column(JSON, default=[])
    progress = Column(JSON, default={})
