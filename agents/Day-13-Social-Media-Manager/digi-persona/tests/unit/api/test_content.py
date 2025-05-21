"""
Tests for the content API endpoints.
"""
import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status


@pytest.fixture
def test_content(client, test_persona):
    """Create a test content item."""
    content_data = {
        "persona_id": test_persona.id,
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

    response = client.post("/api/v1/content", json=content_data)
    assert response.status_code == status.HTTP_201_CREATED

    yield response.json()


def test_create_content(client, test_persona):
    """Test creating a content item."""
    content_data = {
        "persona_id": test_persona.id,
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

    response = client.post("/api/v1/content", json=content_data)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["persona_id"] == content_data["persona_id"]
    assert data["content_type"] == content_data["content_type"]
    assert data["text"] == content_data["text"]
    assert data["platform"] == content_data["platform"]
    assert data["status"] == content_data["status"]
    assert data["content_metadata"] == content_data["content_metadata"]
    assert "id" in data


def test_get_content(client, test_content):
    """Test getting a content item by ID."""
    response = client.get(f"/api/v1/content/{test_content['id']}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == test_content["id"]
    assert data["persona_id"] == test_content["persona_id"]
    assert data["content_type"] == test_content["content_type"]
    assert data["text"] == test_content["text"]
    assert data["platform"] == test_content["platform"]
    assert data["status"] == test_content["status"]


def test_get_nonexistent_content(client):
    """Test getting a content item that doesn't exist."""
    response = client.get("/api/v1/content/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_content(client, test_content):
    """Test updating a content item."""
    update_data = {
        "persona_id": test_content["persona_id"],
        "content_type": test_content["content_type"],
        "text": "Updated test tweet for unit testing.",
        "platform": test_content["platform"],
        "status": test_content["status"],
        "content_metadata": test_content["content_metadata"]
    }

    response = client.put(f"/api/v1/content/{test_content['id']}", json=update_data)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == test_content["id"]
    assert data["text"] == update_data["text"]


def test_delete_content(client, test_content):
    """Test deleting a content item."""
    response = client.delete(f"/api/v1/content/{test_content['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify the content is deleted
    response = client.get(f"/api/v1/content/{test_content['id']}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_content(client, test_content):
    """Test listing all content items."""
    response = client.get("/api/v1/content")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # Check if the test content is in the list
    content_ids = [content["id"] for content in data]
    assert test_content["id"] in content_ids


def test_approve_content(client, test_content):
    """Test approving a content item."""
    response = client.post(f"/api/v1/content/{test_content['id']}/approve")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == test_content["id"]
    assert data["status"] == "approved"


def test_schedule_content(client, test_content):
    """Test scheduling a content item."""
    # First approve the content
    client.post(f"/api/v1/content/{test_content['id']}/approve")

    # Then schedule it
    scheduled_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    schedule_data = {
        "scheduled_time": scheduled_time
    }

    response = client.post(f"/api/v1/content/{test_content['id']}/schedule", json=schedule_data)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == test_content["id"]
    assert data["status"] == "scheduled"
    assert data["scheduled_time"] is not None


def test_generate_content(client, test_persona):
    """Test generating content."""
    content_request = {
        "persona_id": test_persona.id,
        "content_type": "tweet",
        "topic": "artificial intelligence",
        "platform": "twitter",
        "additional_context": "Focus on recent advancements in AI and their ethical implications.",
        "max_length": 280,
        "save": True
    }

    response = client.post("/api/v1/content/generate", json=content_request)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["persona_id"] == content_request["persona_id"]
    assert data["content_type"] == content_request["content_type"]
    assert data["platform"] == content_request["platform"]
    assert data["status"] == "draft"
    assert data["text"] is not None
    assert len(data["text"]) > 0
    assert "id" in data
