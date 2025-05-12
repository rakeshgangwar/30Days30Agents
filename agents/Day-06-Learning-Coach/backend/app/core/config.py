"""
Configuration settings for the Learning Coach Agent.
"""

import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, field_validator
from pydantic_core.core_schema import FieldValidationInfo


class Settings(BaseModel):
    """Application settings."""
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Learning Coach Agent"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./learning_coach.db"
    
    # LangChain settings
    LANGCHAIN_API_KEY: Optional[str] = None
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any, info: FieldValidationInfo) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)


# Load environment variables
settings = Settings()

# Override settings with environment variables
for field in settings.model_fields:
    env_value = os.getenv(field)
    if env_value:
        setattr(settings, field, env_value)
