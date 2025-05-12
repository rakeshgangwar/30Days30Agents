"""
User model for the Learning Coach Agent.
"""

from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    preferences = Column(JSON, default={})
    learning_styles = Column(JSON, default=[])
    interests = Column(JSON, default=[])
