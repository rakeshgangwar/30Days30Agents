from typing import List, Optional

from pydantic import AnyHttpUrl, field_validator, BaseModel

# Use BaseModel instead of BaseSettings if pydantic_settings is not available
try:
    from pydantic_settings import BaseSettings
except ImportError:
    BaseSettings = BaseModel

class Settings(BaseSettings):
    """Application settings."""

    # Application settings
    APP_NAME: str = "Digi-Persona"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "dev-secret-key-for-testing-only"
    API_V1_STR: str = "/api/v1"
    API_PREFIX: str = "/api/v1"

    # CORS settings
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database settings
    DATABASE_URL: str
    DATABASE_TEST_URL: Optional[str] = None

    @field_validator('DATABASE_URL', 'DATABASE_TEST_URL')
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Allow both PostgreSQL and SQLite URLs
        if v.startswith('postgresql://') or v.startswith('postgres://') or v.startswith('sqlite:///'):
            return v
        raise ValueError(f'Invalid database URL: {v}')

    # Redis settings
    REDIS_URL: Optional[str] = None

    # Celery settings
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @field_validator('CELERY_BROKER_URL', 'CELERY_RESULT_BACKEND')
    def validate_celery_url(cls, v: Optional[str], info) -> Optional[str]:
        if v is None:
            # Default to Redis URL if not specified
            # Access the values from the data dictionary
            data = info.data
            return data.get('REDIS_URL')
        return v

    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = None

    # JWT settings
    JWT_SECRET_KEY: Optional[str] = "dev-secret-key-for-testing-only"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Monitoring settings
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
    }

settings = Settings()
