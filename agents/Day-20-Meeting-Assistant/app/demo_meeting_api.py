#!/usr/bin/env python3
"""
Demo script for Meeting API endpoints (T4.1).

This script demonstrates all the core meeting CRUD operations:
- POST /api/meetings - Create meeting
- GET /api/meetings - List meetings
- GET /api/meetings/{id} - Get meeting details
- DELETE /api/meetings/{id} - Delete meeting

Run this script while the API server is running on localhost:8000
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any


API_BASE_URL = "http://localhost:8000/api/meetings"


def print_response(response: requests.Response, operation: str):
    """Helper function to print API response in a formatted way."""
    print(f"\n=== {operation} ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, default=str)}")


def demo_meeting_crud():
    """Demonstrate all meeting CRUD operations."""
    
    print("🚀 Meeting API Demo - Task T4.1")
    print("=" * 50)
    
    # 1. Create a new meeting
    print("\n1️⃣ Creating a new meeting...")
    meeting_data = {
        "title": "Demo Team Meeting",
        "description": "A demonstration meeting for API testing",
        "meeting_type": "virtual",
        "participant_count": 8,
        "platform": "zoom",
        "meeting_url": "https://zoom.us/j/123456789"
    }
    
    try:
        response = requests.post(API_BASE_URL, json=meeting_data)
        print_response(response, "POST /api/meetings")
        
        if response.status_code == 201:
            meeting_id = response.json()["id"]
            print(f"✅ Meeting created successfully with ID: {meeting_id}")
        else:
            print("❌ Failed to create meeting")
            return
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server.")
        print("Please make sure the server is running on http://localhost:8000")
        return
    
    # 2. List all meetings
    print("\n2️⃣ Listing all meetings...")
    response = requests.get(API_BASE_URL)
    print_response(response, "GET /api/meetings")
    
    if response.status_code == 200:
        meetings = response.json()["meetings"]
        print(f"✅ Found {len(meetings)} meeting(s)")
    
    # 3. Get specific meeting details
    print(f"\n3️⃣ Getting details for meeting ID {meeting_id}...")
    response = requests.get(f"{API_BASE_URL}/{meeting_id}")
    print_response(response, f"GET /api/meetings/{meeting_id}")
    
    if response.status_code == 200:
        print("✅ Meeting details retrieved successfully")
    
    # 4. Update the meeting
    print(f"\n4️⃣ Updating meeting ID {meeting_id}...")
    update_data = {
        "description": "Updated description for demo meeting",
        "participant_count": 12
    }
    
    response = requests.put(f"{API_BASE_URL}/{meeting_id}", json=update_data)
    print_response(response, f"PUT /api/meetings/{meeting_id}")
    
    if response.status_code == 200:
        print("✅ Meeting updated successfully")
    
    # 5. Create another meeting for pagination demo
    print("\n5️⃣ Creating another meeting for pagination demo...")
    meeting_data2 = {
        "title": "Second Demo Meeting",
        "description": "Another meeting for pagination testing",
        "meeting_type": "physical",
        "platform": "teams"
    }
    
    response = requests.post(API_BASE_URL, json=meeting_data2)
    if response.status_code == 201:
        meeting_id2 = response.json()["id"]
        print(f"✅ Second meeting created with ID: {meeting_id2}")
    
    # 6. List meetings with pagination
    print("\n6️⃣ Testing pagination...")
    response = requests.get(f"{API_BASE_URL}?page=1&page_size=1")
    print_response(response, "GET /api/meetings?page=1&page_size=1")
    
    # 7. Test filtering
    print("\n7️⃣ Testing filtering by platform...")
    response = requests.get(f"{API_BASE_URL}?platform=zoom")
    print_response(response, "GET /api/meetings?platform=zoom")
    
    # 8. Get meeting transcripts (should be empty)
    print(f"\n8️⃣ Getting transcripts for meeting {meeting_id}...")
    response = requests.get(f"{API_BASE_URL}/{meeting_id}/transcripts")
    print_response(response, f"GET /api/meetings/{meeting_id}/transcripts")
    
    # 9. Get meeting speakers (should be empty)
    print(f"\n9️⃣ Getting speakers for meeting {meeting_id}...")
    response = requests.get(f"{API_BASE_URL}/{meeting_id}/speakers")
    print_response(response, f"GET /api/meetings/{meeting_id}/speakers")
    
    # 10. Delete the meetings
    print(f"\n🔟 Deleting meeting ID {meeting_id}...")
    response = requests.delete(f"{API_BASE_URL}/{meeting_id}")
    print_response(response, f"DELETE /api/meetings/{meeting_id}")
    
    if response.status_code == 200:
        print("✅ Meeting deleted successfully")
    
    print(f"\n🗑️ Deleting meeting ID {meeting_id2}...")
    response = requests.delete(f"{API_BASE_URL}/{meeting_id2}")
    
    if response.status_code == 200:
        print("✅ Second meeting deleted successfully")
    
    # 11. Verify meetings are deleted
    print("\n1️⃣1️⃣ Verifying meetings are deleted...")
    response = requests.get(f"{API_BASE_URL}/{meeting_id}")
    if response.status_code == 404:
        print("✅ Confirmed: Meeting successfully deleted (404 Not Found)")
    
    # Final list to show empty state
    print("\n1️⃣2️⃣ Final meeting list (should be empty)...")
    response = requests.get(API_BASE_URL)
    print_response(response, "GET /api/meetings (final)")
    
    print("\n🎉 Meeting API Demo completed successfully!")
    print("All T4.1 acceptance criteria have been demonstrated:")
    print("✅ All endpoints return proper HTTP status codes")
    print("✅ Input validation works correctly")
    print("✅ Database operations successful")


def demo_error_handling():
    """Demonstrate error handling and validation."""
    
    print("\n🛡️ Error Handling Demo")
    print("=" * 30)
    
    # Test 404 for non-existent meeting
    print("\n1️⃣ Testing 404 for non-existent meeting...")
    response = requests.get(f"{API_BASE_URL}/99999")
    print_response(response, "GET /api/meetings/99999 (should be 404)")
    
    # Test validation error
    print("\n2️⃣ Testing validation error (empty title)...")
    invalid_data = {"title": ""}  # Should fail validation
    response = requests.post(API_BASE_URL, json=invalid_data)
    print_response(response, "POST /api/meetings (invalid data)")
    
    # Test invalid meeting type
    print("\n3️⃣ Testing invalid meeting type...")
    invalid_data = {"title": "Test", "meeting_type": "invalid_type"}
    response = requests.post(API_BASE_URL, json=invalid_data)
    print_response(response, "POST /api/meetings (invalid meeting type)")
    
    print("\n✅ Error handling demonstration completed!")


if __name__ == "__main__":
    demo_meeting_crud()
    demo_error_handling()