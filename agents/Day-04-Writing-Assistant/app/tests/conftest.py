"""
Test fixtures and utilities for the Writing Assistant API tests.
"""
import os
import sys
import pytest
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.main import app
from app.db.database import Base, get_db
from app.core.config import settings
from app.models.preferences import UserPreference
from app.core.security import generate_api_key

# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Create a fresh database for each test.
    
    Yields:
        SQLAlchemy Session: A database session for testing.
    """
    # Create the tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for testing
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after the test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with a database session dependency override.
    
    Args:
        db: SQLAlchemy Session fixture
        
    Yields:
        TestClient: A FastAPI test client.
    """
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create a test client
    with TestClient(app) as client:
        yield client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def api_key() -> str:
    """
    Generate a test API key and set it in the settings.
    
    Returns:
        str: A test API key.
    """
    test_api_key = generate_api_key()
    original_api_key = settings.API_KEY
    
    # Set the test API key
    settings.API_KEY = test_api_key
    
    yield test_api_key
    
    # Restore the original API key
    settings.API_KEY = original_api_key


@pytest.fixture(scope="function")
def test_user_id() -> str:
    """
    Generate a test user ID.
    
    Returns:
        str: A test user ID.
    """
    return "test-user-123"


@pytest.fixture(scope="function")
def test_preferences() -> Dict[str, Any]:
    """
    Generate test preferences data.
    
    Returns:
        Dict[str, Any]: Test preferences data.
    """
    return {
        "preferred_model": "test-model",
        "temperature": 0.5,
        "default_tone": "professional",
        "formality_level": "formal",
        "check_grammar": True,
        "check_style": True,
        "check_spelling": True,
        "extra_settings": {"custom_setting": "value"}
    }


@pytest.fixture(scope="function")
def user_preference(db: Session, test_user_id: str, test_preferences: Dict[str, Any]) -> UserPreference:
    """
    Create a test user preference in the database.
    
    Args:
        db: SQLAlchemy Session fixture
        test_user_id: Test user ID fixture
        test_preferences: Test preferences data fixture
        
    Returns:
        UserPreference: A test user preference.
    """
    # Create a user preference
    user_pref = UserPreference(
        user_id=test_user_id,
        **test_preferences
    )
    db.add(user_pref)
    db.commit()
    db.refresh(user_pref)
    
    return user_pref
