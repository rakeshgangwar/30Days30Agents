"""
Models for user preferences.

This module defines the database models for storing user preferences.
"""
import os
import sys
from sqlalchemy import Column, Integer, String, Boolean, JSON, Float

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.db.database import Base


class UserPreference(Base):
    """User preferences database model."""
    
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, unique=True)
    
    # LLM preferences
    preferred_model = Column(String, nullable=True)
    temperature = Column(Float, default=0.7)
    
    # Writing style preferences
    default_tone = Column(String, nullable=True)
    formality_level = Column(String, default="neutral")  # casual, neutral, formal
    
    # Grammar preferences
    check_grammar = Column(Boolean, default=True)
    check_style = Column(Boolean, default=True)
    check_spelling = Column(Boolean, default=True)
    
    # Additional preferences (extensible)
    extra_settings = Column(JSON, nullable=True)
    
    def to_dict(self):
        """Convert model to dictionary for API responses."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "preferred_model": self.preferred_model,
            "temperature": self.temperature,
            "default_tone": self.default_tone,
            "formality_level": self.formality_level,
            "check_grammar": self.check_grammar,
            "check_style": self.check_style,
            "check_spelling": self.check_spelling,
            "extra_settings": self.extra_settings,
        }