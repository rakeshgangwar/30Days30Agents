"""
Database configuration and session management for Meeting Assistant
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from pydantic_settings import BaseSettings
from typing import Optional


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    
    database_url: str = "sqlite:///./meeting_assistant.db"
    echo_sql: bool = False
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env file


# Initialize settings
db_settings = DatabaseSettings()

# Create engine with SQLite-specific configuration
if db_settings.database_url.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        db_settings.database_url,
        echo=db_settings.echo_sql,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        db_settings.database_url,
        echo=db_settings.echo_sql,
        pool_pre_ping=True,
        pool_recycle=300,
    )

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Naming convention for constraints (helpful for Alembic migrations)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

Base.metadata = MetaData(naming_convention=convention)


def get_database_session():
    """
    Dependency function to get database session
    Use this in FastAPI route dependencies
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_database():
    """Initialize database tables"""
    # Import all models to register them with Base.metadata
    import src.models  # noqa: F401
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")


async def close_database():
    """Close database connections"""
    engine.dispose()
    print("Database connections closed")