#!/usr/bin/env python
"""
Test API Script

This script tests the API endpoints and provides a simple way to verify
that the API is working correctly. It performs a complete workflow from
creating a persona to generating, approving, and scheduling content.
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta, timezone

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class APITestError(Exception):
    """Exception raised when an API test fails."""
    pass


def test_api():
    """Test the API endpoints."""
    base_url = "http://localhost:8000/api/v1"
    success_count = 0
    total_tests = 0

    try:
        # Test 1: Health check endpoint
        total_tests += 1
        print("\n=== Test 1: Health Check ===")
        response = requests.get(f"{base_url}/health")
        if response.status_code != 200:
            raise APITestError(f"Health check failed with status code {response.status_code}")

        health_data = response.json()
        print(f"Health check: {response.status_code}")
        print(json.dumps(health_data, indent=2))
        success_count += 1

        # Test 2: Create a persona
        total_tests += 1
        print("\n=== Test 2: Create Persona ===")
        persona_data = {
            "name": "Tech Guru",
            "background": "A technology enthusiast with 15 years of experience in Silicon Valley.",
            "interests": ["AI", "Blockchain", "IoT"],
            "values": ["Innovation", "Education", "Ethics"],
            "tone": "Professional but approachable",
            "expertise": ["Machine Learning", "Cloud Computing", "Data Science"],
            "purpose": "To share insights about emerging technologies and their impact on society."
        }

        response = requests.post(f"{base_url}/personas", json=persona_data)
        if response.status_code != 201:
            raise APITestError(f"Create persona failed with status code {response.status_code}")

        persona = response.json()
        persona_id = persona["id"]
        print(f"Create persona: {response.status_code}")
        print(json.dumps(persona, indent=2))
        success_count += 1

        # Test 3: Get a persona
        total_tests += 1
        print("\n=== Test 3: Get Persona ===")
        response = requests.get(f"{base_url}/personas/{persona_id}")
        if response.status_code != 200:
            raise APITestError(f"Get persona failed with status code {response.status_code}")

        retrieved_persona = response.json()
        print(f"Get persona: {response.status_code}")
        print(json.dumps(retrieved_persona, indent=2))
        success_count += 1

        # Test 4: Generate content
        total_tests += 1
        print("\n=== Test 4: Generate Content ===")
        content_request = {
            "persona_id": persona_id,
            "content_type": "tweet",
            "topic": "artificial intelligence",
            "platform": "twitter",
            "additional_context": "Focus on recent advancements in AI and their ethical implications.",
            "max_length": 280,
            "save": True
        }

        response = requests.post(f"{base_url}/content/generate", json=content_request)
        if response.status_code != 201:
            raise APITestError(f"Generate content failed with status code {response.status_code}")

        content = response.json()
        content_id = content.get("id")
        if not content_id:
            raise APITestError("Generated content does not have an ID")

        print(f"Generate content: {response.status_code}")
        print(json.dumps(content, indent=2))
        success_count += 1

        # Test 5: Approve content
        total_tests += 1
        print("\n=== Test 5: Approve Content ===")
        response = requests.post(f"{base_url}/content/{content_id}/approve")
        if response.status_code != 200:
            raise APITestError(f"Approve content failed with status code {response.status_code}")

        approved_content = response.json()
        if approved_content["status"] != "approved":
            raise APITestError(f"Content status is {approved_content['status']}, expected 'approved'")

        print(f"Approve content: {response.status_code}")
        print(json.dumps(approved_content, indent=2))
        success_count += 1

        # Test 6: Schedule content
        total_tests += 1
        print("\n=== Test 6: Schedule Content ===")
        schedule_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        schedule_request = {
            "scheduled_time": schedule_time
        }

        response = requests.post(f"{base_url}/content/{content_id}/schedule", json=schedule_request)
        if response.status_code != 200:
            raise APITestError(f"Schedule content failed with status code {response.status_code}")

        scheduled_content = response.json()
        if scheduled_content["status"] != "scheduled":
            raise APITestError(f"Content status is {scheduled_content['status']}, expected 'scheduled'")

        print(f"Schedule content: {response.status_code}")
        print(json.dumps(scheduled_content, indent=2))
        success_count += 1

        # Test 7: Get upcoming content
        total_tests += 1
        print("\n=== Test 7: Get Upcoming Content ===")
        response = requests.get(f"{base_url}/content/list/upcoming")
        if response.status_code != 200:
            raise APITestError(f"Get upcoming content failed with status code {response.status_code}")

        upcoming_content = response.json()
        print(f"Get upcoming content: {response.status_code}")
        print(json.dumps(upcoming_content, indent=2))
        success_count += 1

        # Test 8: Clean up - delete content and persona
        total_tests += 1
        print("\n=== Test 8: Clean Up ===")
        response = requests.delete(f"{base_url}/content/{content_id}")
        if response.status_code != 204:
            raise APITestError(f"Delete content failed with status code {response.status_code}")

        response = requests.delete(f"{base_url}/personas/{persona_id}")
        if response.status_code != 204:
            raise APITestError(f"Delete persona failed with status code {response.status_code}")

        print("Clean up successful")
        success_count += 1

    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Could not connect to the API server at {base_url}")
        print("   Make sure the server is running and accessible.")
        return False
    except APITestError as e:
        print(f"\n❌ ERROR: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False
    finally:
        # Print summary
        print("\n=== Test Summary ===")
        print(f"Tests passed: {success_count}/{total_tests}")
        if success_count == total_tests:
            print("\n✅ All tests passed successfully!")
            return True
        else:
            print(f"\n❌ {total_tests - success_count} tests failed.")
            return False


if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
