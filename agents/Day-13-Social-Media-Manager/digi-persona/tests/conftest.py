"""
Test configuration and fixtures for pytest.
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture(scope="session")
def test_db_url():
    """Get the test database URL."""
    return os.environ.get("DATABASE_TEST_URL", "sqlite:///:memory:")


@pytest.fixture(scope="session")
def test_engine(test_db_url):
    """Create a test database engine."""
    engine = create_engine(
        test_db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture(scope="session")
def test_db(test_engine):
    """Create all tables in the test database."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def db_session(test_engine, test_db):
    """Create a new database session for a test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client for the FastAPI application."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_persona(db_session):
    """Create a test persona."""
    from app.db.models.persona import Persona
    
    persona = Persona(
        name="Test Persona",
        background="A test persona for unit tests",
        interests=["Testing", "Python", "FastAPI"],
        values=["Quality", "Reliability"],
        tone="Professional",
        expertise=["Software Testing", "API Development"],
        purpose="To test the application"
    )
    db_session.add(persona)
    db_session.commit()
    db_session.refresh(persona)
    
    yield persona
    
    db_session.delete(persona)
    db_session.commit()
