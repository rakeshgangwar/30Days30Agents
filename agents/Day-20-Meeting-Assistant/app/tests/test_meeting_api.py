"""
Tests for meeting API endpoints.

This module tests all the meeting CRUD operations and validates
that they meet the acceptance criteria for task T4.1.
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import Base, get_database_session
from src.models import Meeting, MeetingType, ProcessingStatus


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_meetings.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_database_session] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_database():
    """Set up test database for each test."""
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the database tables after each test
    Base.metadata.drop_all(bind=engine)


class TestMeetingCRUD:
    """Test class for meeting CRUD operations."""

    def test_create_meeting_success(self, setup_database):
        """Test successful meeting creation."""
        meeting_data = {
            "title": "Test Meeting",
            "description": "A test meeting for API validation",
            "meeting_type": "virtual",
            "participant_count": 5,
            "platform": "zoom"
        }
        
        response = client.post("/api/meetings/", json=meeting_data)
        
        # Check status code
        assert response.status_code == 201
        
        # Check response data
        data = response.json()
        assert data["title"] == meeting_data["title"]
        assert data["description"] == meeting_data["description"]
        assert data["meeting_type"] == meeting_data["meeting_type"]
        assert data["participant_count"] == meeting_data["participant_count"]
        assert data["platform"] == meeting_data["platform"]
        assert data["processing_status"] == "pending"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_meeting_minimal_data(self, setup_database):
        """Test meeting creation with minimal required data."""
        meeting_data = {
            "title": "Minimal Meeting"
        }
        
        response = client.post("/api/meetings/", json=meeting_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == meeting_data["title"]
        assert data["meeting_type"] == "virtual"  # default value
        assert data["processing_status"] == "pending"

    def test_create_meeting_invalid_data(self, setup_database):
        """Test meeting creation with invalid data."""
        # Test empty title
        response = client.post("/api/meetings/", json={"title": ""})
        assert response.status_code == 422
        
        # Test missing title
        response = client.post("/api/meetings/", json={"description": "No title"})
        assert response.status_code == 422
        
        # Test invalid participant count
        response = client.post("/api/meetings/", json={
            "title": "Test",
            "participant_count": 0
        })
        assert response.status_code == 422

    def test_list_meetings_empty(self, setup_database):
        """Test listing meetings when none exist."""
        response = client.get("/api/meetings/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["meetings"] == []
        assert data["total_count"] == 0
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 0

    def test_list_meetings_with_data(self, setup_database):
        """Test listing meetings when some exist."""
        # Create test meetings
        meetings = [
            {"title": "Meeting 1", "platform": "zoom"},
            {"title": "Meeting 2", "platform": "teams"},
            {"title": "Meeting 3", "platform": "zoom"}
        ]
        
        created_meetings = []
        for meeting_data in meetings:
            response = client.post("/api/meetings/", json=meeting_data)
            assert response.status_code == 201
            created_meetings.append(response.json())
        
        # Test listing all meetings
        response = client.get("/api/meetings/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["meetings"]) == 3
        assert data["total_count"] == 3
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 1

    def test_list_meetings_pagination(self, setup_database):
        """Test meeting list pagination."""
        # Create 15 test meetings
        for i in range(15):
            response = client.post("/api/meetings/", json={"title": f"Meeting {i+1}"})
            assert response.status_code == 201
        
        # Test page 1 with page_size 5
        response = client.get("/api/meetings/?page=1&page_size=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["meetings"]) == 5
        assert data["total_count"] == 15
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert data["total_pages"] == 3
        
        # Test page 2
        response = client.get("/api/meetings/?page=2&page_size=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["meetings"]) == 5
        assert data["page"] == 2

    def test_list_meetings_filtering(self, setup_database):
        """Test meeting list filtering."""
        # Create meetings with different attributes
        meetings = [
            {"title": "Zoom Meeting", "platform": "zoom", "meeting_type": "virtual"},
            {"title": "Teams Meeting", "platform": "teams", "meeting_type": "virtual"},
            {"title": "Physical Meeting", "platform": None, "meeting_type": "physical"}
        ]
        
        for meeting_data in meetings:
            response = client.post("/api/meetings/", json=meeting_data)
            assert response.status_code == 201
        
        # Test filter by platform
        response = client.get("/api/meetings/?platform=zoom")
        assert response.status_code == 200
        data = response.json()
        assert len(data["meetings"]) == 1
        assert data["meetings"][0]["platform"] == "zoom"
        
        # Test filter by meeting type
        response = client.get("/api/meetings/?meeting_type=virtual")
        assert response.status_code == 200
        data = response.json()
        assert len(data["meetings"]) == 2

    def test_get_meeting_success(self, setup_database):
        """Test getting a specific meeting."""
        # Create a test meeting
        meeting_data = {
            "title": "Test Meeting",
            "description": "Test description",
            "platform": "zoom"
        }
        
        create_response = client.post("/api/meetings/", json=meeting_data)
        assert create_response.status_code == 201
        meeting_id = create_response.json()["id"]
        
        # Get the meeting
        response = client.get(f"/api/meetings/{meeting_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == meeting_id
        assert data["title"] == meeting_data["title"]
        assert data["description"] == meeting_data["description"]
        assert data["platform"] == meeting_data["platform"]
        assert "transcript_count" in data
        assert "speaker_count" in data
        assert "summary_count" in data
        assert "action_item_count" in data

    def test_get_meeting_not_found(self, setup_database):
        """Test getting a non-existent meeting."""
        response = client.get("/api/meetings/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_meeting_success(self, setup_database):
        """Test updating a meeting."""
        # Create a test meeting
        meeting_data = {"title": "Original Title", "platform": "zoom"}
        create_response = client.post("/api/meetings/", json=meeting_data)
        assert create_response.status_code == 201
        meeting_id = create_response.json()["id"]
        
        # Update the meeting
        update_data = {
            "title": "Updated Title",
            "description": "New description",
            "participant_count": 10
        }
        
        response = client.put(f"/api/meetings/{meeting_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["participant_count"] == update_data["participant_count"]
        assert data["platform"] == "zoom"  # Should remain unchanged

    def test_update_meeting_not_found(self, setup_database):
        """Test updating a non-existent meeting."""
        update_data = {"title": "New Title"}
        response = client.put("/api/meetings/999", json=update_data)
        assert response.status_code == 404

    def test_delete_meeting_success(self, setup_database):
        """Test deleting a meeting."""
        # Create a test meeting
        meeting_data = {"title": "Meeting to Delete"}
        create_response = client.post("/api/meetings/", json=meeting_data)
        assert create_response.status_code == 201
        meeting_id = create_response.json()["id"]
        
        # Delete the meeting
        response = client.delete(f"/api/meetings/{meeting_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert "deleted successfully" in data["message"]
        assert data["deleted_meeting_id"] == meeting_id
        
        # Verify meeting is gone
        get_response = client.get(f"/api/meetings/{meeting_id}")
        assert get_response.status_code == 404

    def test_delete_meeting_not_found(self, setup_database):
        """Test deleting a non-existent meeting."""
        response = client.delete("/api/meetings/999")
        assert response.status_code == 404

    def test_get_meeting_transcripts(self, setup_database):
        """Test getting transcripts for a meeting."""
        # Create a test meeting
        meeting_data = {"title": "Test Meeting"}
        create_response = client.post("/api/meetings/", json=meeting_data)
        assert create_response.status_code == 201
        meeting_id = create_response.json()["id"]
        
        # Get transcripts (should be empty)
        response = client.get(f"/api/meetings/{meeting_id}/transcripts")
        assert response.status_code == 200
        
        data = response.json()
        assert data["meeting_id"] == meeting_id
        assert data["transcript_count"] == 0
        assert data["transcripts"] == []

    def test_get_meeting_speakers(self, setup_database):
        """Test getting speakers for a meeting."""
        # Create a test meeting
        meeting_data = {"title": "Test Meeting"}
        create_response = client.post("/api/meetings/", json=meeting_data)
        assert create_response.status_code == 201
        meeting_id = create_response.json()["id"]
        
        # Get speakers (should be empty)
        response = client.get(f"/api/meetings/{meeting_id}/speakers")
        assert response.status_code == 200
        
        data = response.json()
        assert data["meeting_id"] == meeting_id
        assert data["speaker_count"] == 0
        assert data["speakers"] == []

    def test_get_meeting_summaries(self, setup_database):
        """Test getting summaries for a meeting."""
        # Create a test meeting
        meeting_data = {"title": "Test Meeting"}
        create_response = client.post("/api/meetings/", json=meeting_data)
        assert create_response.status_code == 201
        meeting_id = create_response.json()["id"]
        
        # Get summaries (should be empty)
        response = client.get(f"/api/meetings/{meeting_id}/summaries")
        assert response.status_code == 200
        
        data = response.json()
        assert data["meeting_id"] == meeting_id
        assert data["summary_count"] == 0
        assert data["summaries"] == []

    def test_get_meeting_action_items(self, setup_database):
        """Test getting action items for a meeting."""
        # Create a test meeting
        meeting_data = {"title": "Test Meeting"}
        create_response = client.post("/api/meetings/", json=meeting_data)
        assert create_response.status_code == 201
        meeting_id = create_response.json()["id"]
        
        # Get action items (should be empty)
        response = client.get(f"/api/meetings/{meeting_id}/action-items")
        assert response.status_code == 200
        
        data = response.json()
        assert data["meeting_id"] == meeting_id
        assert data["action_item_count"] == 0
        assert data["action_items"] == []


class TestHTTPStatusCodes:
    """Test that all endpoints return proper HTTP status codes."""

    def test_post_create_meeting_status_codes(self, setup_database):
        """Test POST /api/meetings/ status codes."""
        # Success case
        response = client.post("/api/meetings/", json={"title": "Test"})
        assert response.status_code == 201
        
        # Invalid data
        response = client.post("/api/meetings/", json={})
        assert response.status_code == 422

    def test_get_list_meetings_status_codes(self, setup_database):
        """Test GET /api/meetings/ status codes."""
        # Success case (empty list)
        response = client.get("/api/meetings/")
        assert response.status_code == 200
        
        # Invalid pagination
        response = client.get("/api/meetings/?page=0")
        assert response.status_code == 422

    def test_get_meeting_detail_status_codes(self, setup_database):
        """Test GET /api/meetings/{id} status codes."""
        # Create a meeting first
        create_response = client.post("/api/meetings/", json={"title": "Test"})
        meeting_id = create_response.json()["id"]
        
        # Success case
        response = client.get(f"/api/meetings/{meeting_id}")
        assert response.status_code == 200
        
        # Not found
        response = client.get("/api/meetings/999")
        assert response.status_code == 404

    def test_put_update_meeting_status_codes(self, setup_database):
        """Test PUT /api/meetings/{id} status codes."""
        # Create a meeting first
        create_response = client.post("/api/meetings/", json={"title": "Test"})
        meeting_id = create_response.json()["id"]
        
        # Success case
        response = client.put(f"/api/meetings/{meeting_id}", json={"title": "Updated"})
        assert response.status_code == 200
        
        # Not found
        response = client.put("/api/meetings/999", json={"title": "Updated"})
        assert response.status_code == 404

    def test_delete_meeting_status_codes(self, setup_database):
        """Test DELETE /api/meetings/{id} status codes."""
        # Create a meeting first
        create_response = client.post("/api/meetings/", json={"title": "Test"})
        meeting_id = create_response.json()["id"]
        
        # Success case
        response = client.delete(f"/api/meetings/{meeting_id}")
        assert response.status_code == 200
        
        # Not found
        response = client.delete("/api/meetings/999")
        assert response.status_code == 404


class TestInputValidation:
    """Test input validation for all endpoints."""

    def test_meeting_title_validation(self, setup_database):
        """Test meeting title validation."""
        # Valid title
        response = client.post("/api/meetings/", json={"title": "Valid Title"})
        assert response.status_code == 201
        
        # Empty title
        response = client.post("/api/meetings/", json={"title": ""})
        assert response.status_code == 422
        
        # Missing title
        response = client.post("/api/meetings/", json={"description": "No title"})
        assert response.status_code == 422
        
        # Title too long (over 255 chars)
        long_title = "x" * 256
        response = client.post("/api/meetings/", json={"title": long_title})
        assert response.status_code == 422

    def test_participant_count_validation(self, setup_database):
        """Test participant count validation."""
        # Valid participant count
        response = client.post("/api/meetings/", json={
            "title": "Test",
            "participant_count": 5
        })
        assert response.status_code == 201
        
        # Zero participants (invalid)
        response = client.post("/api/meetings/", json={
            "title": "Test",
            "participant_count": 0
        })
        assert response.status_code == 422
        
        # Negative participants (invalid)
        response = client.post("/api/meetings/", json={
            "title": "Test",
            "participant_count": -1
        })
        assert response.status_code == 422

    def test_meeting_type_validation(self, setup_database):
        """Test meeting type validation."""
        # Valid meeting types
        for meeting_type in ["virtual", "physical", "hybrid"]:
            response = client.post("/api/meetings/", json={
                "title": f"Test {meeting_type}",
                "meeting_type": meeting_type
            })
            assert response.status_code == 201
        
        # Invalid meeting type
        response = client.post("/api/meetings/", json={
            "title": "Test",
            "meeting_type": "invalid_type"
        })
        assert response.status_code == 422

    def test_pagination_validation(self, setup_database):
        """Test pagination parameter validation."""
        # Valid pagination
        response = client.get("/api/meetings/?page=1&page_size=10")
        assert response.status_code == 200
        
        # Invalid page (less than 1)
        response = client.get("/api/meetings/?page=0")
        assert response.status_code == 422
        
        # Invalid page_size (greater than 100)
        response = client.get("/api/meetings/?page_size=101")
        assert response.status_code == 422
        
        # Invalid page_size (less than 1)
        response = client.get("/api/meetings/?page_size=0")
        assert response.status_code == 422


class TestDatabaseOperations:
    """Test that database operations work correctly."""

    def test_meeting_persistence(self, setup_database):
        """Test that meetings are properly persisted to database."""
        meeting_data = {
            "title": "Persistent Meeting",
            "description": "This should persist",
            "platform": "zoom"
        }
        
        # Create meeting
        response = client.post("/api/meetings/", json=meeting_data)
        assert response.status_code == 201
        meeting_id = response.json()["id"]
        
        # Retrieve meeting and verify data persisted
        response = client.get(f"/api/meetings/{meeting_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == meeting_data["title"]
        assert data["description"] == meeting_data["description"]
        assert data["platform"] == meeting_data["platform"]

    def test_meeting_update_persistence(self, setup_database):
        """Test that meeting updates are properly persisted."""
        # Create meeting
        create_response = client.post("/api/meetings/", json={"title": "Original"})
        meeting_id = create_response.json()["id"]
        
        # Update meeting
        update_data = {"title": "Updated", "description": "New description"}
        response = client.put(f"/api/meetings/{meeting_id}", json=update_data)
        assert response.status_code == 200
        
        # Retrieve and verify update persisted
        response = client.get(f"/api/meetings/{meeting_id}")
        data = response.json()
        assert data["title"] == "Updated"
        assert data["description"] == "New description"

    def test_meeting_deletion_cleanup(self, setup_database):
        """Test that meeting deletion removes it from database."""
        # Create meeting
        create_response = client.post("/api/meetings/", json={"title": "To Delete"})
        meeting_id = create_response.json()["id"]
        
        # Verify meeting exists
        response = client.get(f"/api/meetings/{meeting_id}")
        assert response.status_code == 200
        
        # Delete meeting
        response = client.delete(f"/api/meetings/{meeting_id}")
        assert response.status_code == 200
        
        # Verify meeting is gone
        response = client.get(f"/api/meetings/{meeting_id}")
        assert response.status_code == 404