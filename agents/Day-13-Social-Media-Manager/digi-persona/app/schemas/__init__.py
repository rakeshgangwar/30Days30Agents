"""
Schemas Package

This package provides Pydantic schemas for the application.
"""

from app.schemas.persona import PersonaCreate, PersonaUpdate, PersonaResponse, PersonaList
from app.schemas.content import (
    ContentCreate,
    ContentUpdate,
    ContentResponse,
    ContentList,
    ContentGenerateRequest,
    ContentGenerateResponse,
    ContentScheduleRequest,
    ContentScheduleResponse,
    ContentBatchScheduleRequest,
    ContentGenerateScheduleRequest,
    ContentBatchGenerateScheduleRequest,
    TaskResponse,
)
from app.schemas.auth import (
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenPayload,
)

__all__ = [
    "PersonaCreate",
    "PersonaUpdate",
    "PersonaResponse",
    "PersonaList",
    "ContentCreate",
    "ContentUpdate",
    "ContentResponse",
    "ContentList",
    "ContentGenerateRequest",
    "ContentGenerateResponse",
    "ContentScheduleRequest",
    "ContentScheduleResponse",
    "ContentBatchScheduleRequest",
    "ContentGenerateScheduleRequest",
    "ContentBatchGenerateScheduleRequest",
    "TaskResponse",
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenPayload",
]
