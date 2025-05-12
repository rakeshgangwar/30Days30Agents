"""
Quiz model for the Learning Coach Agent.
"""

from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean, Float
from sqlalchemy.orm import relationship

from app.db.base import Base


class Quiz(Base):
    """Quiz model."""
    
    __tablename__ = "quizzes"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    topic = Column(String, index=True)
    difficulty = Column(String)  # beginner, intermediate, advanced
    questions = Column(JSON, default=[])
    estimated_time_minutes = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    learning_objectives = Column(JSON, default=[])
    tags = Column(JSON, default=[])
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="quizzes")


class QuizAttempt(Base):
    """Quiz attempt model."""
    
    __tablename__ = "quiz_attempts"
    
    id = Column(String, primary_key=True, index=True)
    quiz_id = Column(String, ForeignKey("quizzes.id"), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    answers = Column(JSON, default=[])
    score = Column(Float)
    correct_answers = Column(Integer)
    total_questions = Column(Integer)
    feedback = Column(JSON, default={})
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    quiz = relationship("Quiz")
    user = relationship("User")
