"""
Base Database Module

This module provides the base database models and utilities.
"""

# Import base first
from app.db.session import Base

# Import models in dependency order
from app.db.models.user import User
from app.db.models.persona import Persona
from app.db.models.content import Content
from app.db.models.platform import PlatformConnection
from app.db.models.interaction import Interaction

# Import all models here to ensure they are registered with SQLAlchemy
__all__ = [
    "Base",
    "User",
    "Persona",
    "Content",
    "PlatformConnection",
    "Interaction",
]
