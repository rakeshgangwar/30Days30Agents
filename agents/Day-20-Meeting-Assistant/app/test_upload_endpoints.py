#!/usr/bin/env python3
"""
Test script for the new upload endpoints in T4.2
"""

import asyncio
import httpx
import os
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_FILE_PATH = "test_files/sample.wav"  # We'll create a simple test file

async def create_test_audio_file():
    """Create a simple test audio file for testing."""
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create a simple test file (not a real audio file, but for testing upload)
    test_file = test_dir / "sample.wav"
    with open(test_file, "wb") as f:
        # Write some dummy data to simulate an audio file
        f.write(b"RIFF" + b"\x00" * 1000)  # Simple WAV-like header + data
    
    return test_file

async def test_single_upload():
    """Test single file upload endpoint."""
    print("Testing single file upload...")
    
    # Create test file
    test_file = await create_test_audio_file()
    
    async with httpx.AsyncClient() as client:
        try:
            # Test upload
            with open(test_file, "rb") as f:
                files = {"file": ("sample.wav", f, "audio/wav")}
                response = await client.post(f"{API_BASE_URL}/api/audio/upload-audio", files=files)
            
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.json()}")
            
            if response.status_code == 200:
                upload_result = response.json()
                upload_id = upload_result["upload_id"]
                print(f"✅ Upload successful! Upload ID: {upload_id}")
                return upload_id
            else:
                print(f"❌ Upload failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error during upload: {e}")
            return None

async def test_upload_progress(upload_id: str):
    """Test upload progress tracking."""
    print(f"Testing upload progress for {upload_id}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/api/audio/upload-progress/{upload_id}")
            print(f"Progress response status: {response.status_code}")
            print(f"Progress response body: {response.json()}")
            
            if response.status_code == 200:
                print("✅ Progress tracking working!")
            else:
                print(f"❌ Progress tracking failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error getting progress: {e}")

async def test_multiple_upload():
    """Test multiple file upload endpoint."""
    print("Testing multiple file upload...")
    
    # Create multiple test files
    test_files = []
    for i in range(3):
        test_dir = Path("test_files")
        test_file = test_dir / f"sample_{i}.wav"
        with open(test_file, "wb") as f:
            f.write(b"RIFF" + b"\x00" * (1000 + i * 100))
        test_files.append(test_file)
    
    async with httpx.AsyncClient() as client:
        try:
            # Prepare files for upload
            files = []
            for test_file in test_files:
                with open(test_file, "rb") as f:
                    files.append(("files", (test_file.name, f.read(), "audio/wav")))
            
            response = await client.post(f"{API_BASE_URL}/api/audio/upload-multiple", files=files)
            
            print(f"Multiple upload response status: {response.status_code}")
            print(f"Multiple upload response body: {response.json()}")
            
            if response.status_code == 200:
                print("✅ Multiple upload successful!")
            else:
                print(f"❌ Multiple upload failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error during multiple upload: {e}")

async def test_file_validation():
    """Test file validation with invalid files."""
    print("Testing file validation...")
    
    # Create an invalid file (wrong extension)
    test_dir = Path("test_files")
    invalid_file = test_dir / "invalid.txt"
    with open(invalid_file, "w") as f:
        f.write("This is not an audio file")
    
    async with httpx.AsyncClient() as client:
        try:
            with open(invalid_file, "rb") as f:
                files = {"file": ("invalid.txt", f, "text/plain")}
                response = await client.post(f"{API_BASE_URL}/api/audio/upload-audio", files=files)
            
            print(f"Validation test response status: {response.status_code}")
            print(f"Validation test response body: {response.json()}")
            
            if response.status_code == 400:
                print("✅ File validation working correctly!")
            else:
                print(f"❌ File validation not working as expected")
                
        except Exception as e:
            print(f"❌ Error during validation test: {e}")

async def test_delete_upload(upload_id: str):
    """Test upload deletion."""
    print(f"Testing upload deletion for {upload_id}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(f"{API_BASE_URL}/api/audio/upload/{upload_id}")
            print(f"Delete response status: {response.status_code}")
            print(f"Delete response body: {response.json()}")
            
            if response.status_code == 200:
                print("✅ Upload deletion working!")
            else:
                print(f"❌ Upload deletion failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error during deletion: {e}")

async def main():
    """Run all tests."""
    print("=" * 50)
    print("Testing T4.2 File Upload Implementation")
    print("=" * 50)
    
    # Test server health first
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/health")
            if response.status_code != 200:
                print(f"❌ Server not responding at {API_BASE_URL}")
                return
            print(f"✅ Server is running at {API_BASE_URL}")
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print("Make sure the server is running with: uv run uvicorn src.main:app --reload")
            return
    
    # Run tests
    upload_id = await test_single_upload()
    
    if upload_id:
        await test_upload_progress(upload_id)
        await test_delete_upload(upload_id)
    
    await test_multiple_upload()
    await test_file_validation()
    
    # Cleanup
    test_dir = Path("test_files")
    if test_dir.exists():
        for file in test_dir.glob("*"):
            if file.is_file():
                file.unlink()
        test_dir.rmdir()
    
    print("=" * 50)
    print("Testing completed!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())