"""
Integration tests for the API workflow.
"""
import pytest
from datetime import datetime, timedelta, timezone
from fastapi import status


def test_complete_workflow(client):
    """Test the complete workflow from persona creation to content publishing."""
    # Step 1: Create a persona
    persona_data = {
        "name": "Tech Guru",
        "background": "A technology enthusiast with 15 years of experience in Silicon Valley.",
        "interests": ["AI", "Blockchain", "IoT"],
        "values": ["Innovation", "Education", "Ethics"],
        "tone": "Professional but approachable",
        "expertise": ["Machine Learning", "Cloud Computing", "Data Science"],
        "purpose": "To share insights about emerging technologies and their impact on society."
    }

    response = client.post("/api/v1/personas", json=persona_data)
    assert response.status_code == status.HTTP_201_CREATED

    persona = response.json()
    persona_id = persona["id"]

    # Step 2: Generate content for the persona
    content_request = {
        "persona_id": persona_id,
        "content_type": "tweet",
        "topic": "artificial intelligence",
        "platform": "twitter",
        "additional_context": "Focus on recent advancements in AI and their ethical implications.",
        "max_length": 280,
        "save": True
    }

    response = client.post("/api/v1/content/generate", json=content_request)
    assert response.status_code == status.HTTP_201_CREATED

    content = response.json()
    content_id = content["id"]

    # Step 3: Approve the content
    response = client.post(f"/api/v1/content/{content_id}/approve")
    assert response.status_code == status.HTTP_200_OK

    approved_content = response.json()
    assert approved_content["status"] == "approved"

    # Step 4: Schedule the content
    scheduled_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    schedule_data = {
        "scheduled_time": scheduled_time
    }

    response = client.post(f"/api/v1/content/{content_id}/schedule", json=schedule_data)
    assert response.status_code == status.HTTP_200_OK

    scheduled_content = response.json()
    assert scheduled_content["status"] == "scheduled"
    assert scheduled_content["scheduled_time"] is not None

    # Step 5: Check upcoming content
    response = client.get("/api/v1/content/list/upcoming")
    assert response.status_code == status.HTTP_200_OK

    upcoming_content = response.json()
    assert isinstance(upcoming_content, list)

    # Find our content in the list
    found = False
    for item in upcoming_content:
        if item["id"] == content_id:
            found = True
            break

    assert found, "Scheduled content not found in upcoming content list"

    # Step 6: Publish the content
    response = client.post(f"/api/v1/content/{content_id}/publish")
    assert response.status_code == status.HTTP_200_OK

    published_content = response.json()
    assert published_content["status"] == "published"
    assert published_content["published_time"] is not None

    # Step 7: Clean up - delete the content and persona
    response = client.delete(f"/api/v1/content/{content_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = client.delete(f"/api/v1/personas/{persona_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
