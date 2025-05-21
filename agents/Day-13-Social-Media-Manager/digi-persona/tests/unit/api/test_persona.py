"""
Tests for the persona API endpoints.
"""
import pytest
from fastapi import status


def test_create_persona(client):
    """Test creating a persona."""
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
    
    data = response.json()
    assert data["name"] == persona_data["name"]
    assert data["background"] == persona_data["background"]
    assert data["interests"] == persona_data["interests"]
    assert data["values"] == persona_data["values"]
    assert data["tone"] == persona_data["tone"]
    assert data["expertise"] == persona_data["expertise"]
    assert data["purpose"] == persona_data["purpose"]
    assert "id" in data


def test_get_persona(client, test_persona):
    """Test getting a persona by ID."""
    response = client.get(f"/api/v1/personas/{test_persona.id}")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == test_persona.id
    assert data["name"] == test_persona.name
    assert data["background"] == test_persona.background
    assert data["interests"] == test_persona.interests
    assert data["values"] == test_persona.values
    assert data["tone"] == test_persona.tone
    assert data["expertise"] == test_persona.expertise
    assert data["purpose"] == test_persona.purpose


def test_get_nonexistent_persona(client):
    """Test getting a persona that doesn't exist."""
    response = client.get("/api/v1/personas/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_persona(client, test_persona):
    """Test updating a persona."""
    update_data = {
        "name": "Updated Persona",
        "background": test_persona.background,
        "interests": test_persona.interests,
        "values": test_persona.values,
        "tone": test_persona.tone,
        "expertise": test_persona.expertise,
        "purpose": test_persona.purpose
    }
    
    response = client.put(f"/api/v1/personas/{test_persona.id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == test_persona.id
    assert data["name"] == update_data["name"]


def test_delete_persona(client, test_persona):
    """Test deleting a persona."""
    response = client.delete(f"/api/v1/personas/{test_persona.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify the persona is deleted
    response = client.get(f"/api/v1/personas/{test_persona.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_personas(client, test_persona):
    """Test listing all personas."""
    response = client.get("/api/v1/personas")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # Check if the test persona is in the list
    persona_ids = [persona["id"] for persona in data]
    assert test_persona.id in persona_ids
