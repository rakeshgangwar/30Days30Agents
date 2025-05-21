"""
User Database Model

This module provides the database model for users.
"""

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class User(Base):
    """
    Database model for users.
    
    A user represents a person who can own personas and interact with the system.
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Relationships
    personas = relationship("Persona", back_populates="owner")
    
    def __repr__(self):
        return f"<User {self.email}>"
