"""
Data Analysis Agent - Configuration Settings

This module contains configuration settings and environment variables for the Data Analysis Agent.
"""

import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, Any, List


class Settings(BaseSettings):
    """Application settings."""
    
    # API Keys
    OPENROUTER_API_KEY: Optional[str] = None
    
    # LLM Settings
    DEFAULT_LLM_MODEL: str = "anthropic/claude-3.7-sonnet"
    DEFAULT_TEMPERATURE: float = 0.2
    DEFAULT_MAX_TOKENS: int = 1024
    DEFAULT_REQUEST_TIMEOUT: int = 60
    DEFAULT_MAX_RETRIES: int = 3
    
    # Agent Settings
    AGENT_MAX_ITERATIONS: int = 25
    AGENT_MAX_EXECUTION_TIME: int = 30
    AGENT_EARLY_STOPPING_METHOD: str = "force"
    AGENT_ALLOW_DANGEROUS_CODE: bool = True
    
    # Database Settings
    DEFAULT_SQLITE_PATH: str = "test_data.db"
    DEFAULT_DB_TYPE: str = "sqlite"
    
    # Application Settings
    APP_TITLE: str = "Data Analysis Agent"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # Model config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Create settings instance
settings = Settings()
