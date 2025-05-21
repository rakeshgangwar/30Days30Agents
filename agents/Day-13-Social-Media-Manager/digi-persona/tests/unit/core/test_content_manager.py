"""
Tests for the content manager.
"""
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from app.core.content.manager import ContentManager
from app.db.models.content import Content
from app.db.models.persona import Persona


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock()
    return session


@pytest.fixture
def mock_persona():
    """Create a mock persona for testing."""
    return Persona(
        id=1,
        name="Test Persona",
        background="A test persona for unit tests",
        interests=["Testing", "Python", "FastAPI"],
        values=["Quality", "Reliability"],
        tone="Professional",
        expertise=["Software Testing", "API Development"],
        purpose="To test the application"
    )


@pytest.fixture
def mock_content(mock_persona):
    """Create a mock content item for testing."""
    return Content(
        id=1,
        persona_id=mock_persona.id,
        content_type="tweet",
        text="This is a test tweet for unit testing.",
        platform="twitter",
        status="draft",
        content_metadata={
            "topic": "testing",
            "additional_context": "Unit testing the API",
            "max_length": 280
        }
    )


@pytest.fixture
def content_manager(mock_db_session):
    """Create a content manager instance for testing."""
    return ContentManager(db=mock_db_session)


def test_create_content(content_manager, mock_db_session, mock_persona):
    """Test creating a content item."""
    content_data = {
        "persona_id": mock_persona.id,
        "content_type": "tweet",
        "text": "This is a test tweet for unit testing.",
        "platform": "twitter",
        "status": "draft",
        "content_metadata": {
            "topic": "testing",
            "additional_context": "Unit testing the API",
            "max_length": 280
        }
    }

    # Configure the mock session
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh = lambda x: None

    # Create the content
    content = content_manager.create_content(**content_data)

    # Verify the result
    assert content is not None
    assert content.persona_id == content_data["persona_id"]
    assert content.content_type == content_data["content_type"]
    assert content.text == content_data["text"]
    assert content.platform == content_data["platform"]
    assert content.status == content_data["status"]
    assert content.content_metadata == content_data["content_metadata"]

    # Verify the mock was called
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_get_content(content_manager, mock_db_session, mock_content):
    """Test getting a content item by ID."""
    # Configure the mock session
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_content

    # Get the content
    content = content_manager.get_content(content_id=mock_content.id)

    # Verify the result
    assert content is not None
    assert content.id == mock_content.id
    assert content.persona_id == mock_content.persona_id
    assert content.content_type == mock_content.content_type
    assert content.text == mock_content.text
    assert content.platform == mock_content.platform
    assert content.status == mock_content.status

    # Verify the mock was called
    mock_db_session.query.assert_called_once()


def test_update_content(content_manager, mock_db_session, mock_content):
    """Test updating a content item."""
    # Configure the mock session
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_content
    mock_db_session.commit.return_value = None

    # Update data
    update_data = {
        "text": "Updated test tweet for unit testing."
    }

    # Update the content
    content = content_manager.update_content(content_id=mock_content.id, **update_data)

    # Verify the result
    assert content is not None
    assert content.id == mock_content.id
    assert content.text == update_data["text"]

    # Verify the mock was called
    mock_db_session.query.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_delete_content(content_manager, mock_db_session, mock_content):
    """Test deleting a content item."""
    # Configure the mock session
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_content
    mock_db_session.delete.return_value = None
    mock_db_session.commit.return_value = None

    # Delete the content
    result = content_manager.delete_content(content_id=mock_content.id)

    # Verify the result
    assert result is True

    # Verify the mock was called
    mock_db_session.query.assert_called_once()
    mock_db_session.delete.assert_called_once_with(mock_content)
    mock_db_session.commit.assert_called_once()


def test_approve_content(content_manager, mock_db_session, mock_content):
    """Test approving a content item."""
    # Configure the mock session
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_content
    mock_db_session.commit.return_value = None

    # Approve the content
    content = content_manager.approve_content(content_id=mock_content.id)

    # Verify the result
    assert content is not None
    assert content.status == "approved"

    # Verify the mock was called
    mock_db_session.query.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_schedule_content(content_manager, mock_db_session, mock_content):
    """Test scheduling a content item."""
    # Configure the mock session
    mock_content.status = "approved"  # Content must be approved before scheduling
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_content
    mock_db_session.commit.return_value = None

    # Schedule time
    scheduled_time = datetime.now(timezone.utc) + timedelta(hours=1)

    # Schedule the content
    content = content_manager.schedule_content(content_id=mock_content.id, scheduled_time=scheduled_time)

    # Verify the result
    assert content is not None
    assert content.status == "scheduled"
    assert content.scheduled_time == scheduled_time

    # Verify the mock was called
    mock_db_session.query.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_publish_content(content_manager, mock_db_session, mock_content):
    """Test publishing a content item."""
    # Configure the mock session
    mock_content.status = "scheduled"  # Content must be scheduled before publishing
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_content
    mock_db_session.commit.return_value = None

    # Publish the content
    content = content_manager.publish_content(content_id=mock_content.id)

    # Verify the result
    assert content is not None
    assert content.status == "published"
    assert content.published_time is not None

    # Verify the mock was called
    mock_db_session.query.assert_called_once()
    mock_db_session.commit.assert_called_once()
