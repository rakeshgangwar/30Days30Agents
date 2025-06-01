"""
Test cases for main FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "running"


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "message" in data


def test_api_title():
    """Test that the API has the correct title in OpenAPI schema"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi_schema = response.json()
    assert openapi_schema["info"]["title"] == "Meeting Assistant API"
    assert openapi_schema["info"]["version"] == "0.1.0"