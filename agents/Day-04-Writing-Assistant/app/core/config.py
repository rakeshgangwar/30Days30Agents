"""
Configuration settings for the Writing Assistant API.
"""
import os
import json
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # App information
    APP_NAME: str = "Writing Assistant API"
    APP_DESCRIPTION: str = "AI-powered writing assistant with integration for multiple text editors"
    APP_VERSION: str = "0.1.0"
    DOCS_URL: str = "/docs"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]

    @field_validator("CORS_ORIGINS")
    def validate_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins string to list if needed."""
        if isinstance(v, str):
            if v == "*":
                return ["*"]

            # Try to parse as JSON first
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                # Fallback to comma separation if not JSON
                return [i.strip() for i in v.split(",")]

        return v

    # Database settings
    DATABASE_URL: str = "sqlite:///./writing_assistant.db"

    # OpenRouter settings
    OPENROUTER_API_KEY: Optional[str] = None
    DEFAULT_LLM_MODEL: str = "anthropic/claude-3-haiku"

    # Security settings
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    API_KEY: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"

    # Model config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create settings instance
settings = Settings()