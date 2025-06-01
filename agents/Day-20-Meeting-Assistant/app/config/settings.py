"""
Configuration settings for the Meeting Assistant application.
Loads environment variables and provides default values.
"""

import os
from pathlib import Path
from typing import List, Optional, Union, Annotated, Any

# For Pydantic v2, BaseSettings is in pydantic-settings package
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///meeting_assistant.db"
    
    # Redis Configuration (Optional)
    REDIS_URL: Optional[str] = None
    
    # API Keys
    OPENROUTER_API_KEY: Optional[str] = None
    HF_TOKEN: Optional[str] = None
    
    # LLM Configuration
    USE_LOCAL_LLM: bool = False
    OPENROUTER_MODEL: str = "anthropic/claude-3.5-sonnet"
    OLLAMA_MODEL: str = "llama3.1:8b"
    
    # Audio Processing
    CHUNK_SIZE_MINUTES: int = 15
    MAX_FILE_SIZE_MB: int = 500
    
    # Audio Chunking System
    CHUNK_DURATION: int = 15 * 60  # Default chunk duration in seconds (15 minutes)
    MAX_WORKERS: int = 3  # Default number of parallel workers for processing chunks
    ENABLE_CHUNKING: bool = True  # Whether to enable chunking by default
    
    # Security
    SECRET_KEY: str = "default-secret-key-for-development-only"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application Settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "production"
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    CHUNK_DIR: str = "chunks"
    MODEL_DIR: str = "models"
    
    # Celery Configuration
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # Audio Processing Settings
    WHISPER_MODEL: str = "medium"
    ENABLE_GPU: bool = False
    
    # CORS Settings - Store as string and parse in validator
    ALLOWED_ORIGINS_STR: Optional[str] = None
    ALLOWED_ORIGINS: List[str] = Field(default=["http://localhost:3000", "http://localhost:8080"])
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Any, info: Any = None) -> List[str]:
        """Parse comma-separated string of allowed origins"""
        # If ALLOWED_ORIGINS is set directly and is a string, parse it
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
            
        # If it's already a list, return as-is
        if isinstance(v, list):
            return v
            
        # Otherwise return the default
        return ["http://localhost:3000", "http://localhost:8080"]
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values"""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the allowed values"""
        allowed_environments = ["development", "testing", "production"]
        if v.lower() not in allowed_environments:
            raise ValueError(f"Environment must be one of {allowed_environments}")
        return v.lower()
    
    @field_validator("CHUNK_DURATION")
    @classmethod
    def validate_chunk_duration(cls, v: int) -> int:
        """Validate chunk duration is within reasonable limits"""
        if v < 60:  # Minimum 1 minute
            raise ValueError("Chunk duration must be at least 60 seconds (1 minute)")
        if v > 3600:  # Maximum 1 hour
            raise ValueError("Chunk duration must be at most 3600 seconds (1 hour)")
        return v
    
    @field_validator("MAX_WORKERS")
    @classmethod
    def validate_max_workers(cls, v: int) -> int:
        """Validate max workers is within reasonable limits"""
        if v < 1:
            raise ValueError("Max workers must be at least 1")
        if v > 10:  # Reasonable limit to prevent resource exhaustion
            raise ValueError("Max workers must be at most 10")
        return v

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


# Create settings instance with error handling
try:
    settings = Settings()
except Exception as e:
    import sys
    print(f"Error loading settings: {e}")
    sys.exit(1)
