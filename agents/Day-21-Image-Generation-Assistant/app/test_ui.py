"""Test script for Gradio UI functionality."""

import os
from gradio_ui import enhance_prompt_func, view_history_func, get_setup_status

def test_enhance_prompt():
    """Test the enhance prompt functionality."""
    print("🧪 Testing enhance prompt function...")
    
    # Test basic enhancement
    enhanced, details = enhance_prompt_func(
        prompt="a cat",
        style="photorealistic",
        provider="auto",
        context=""
    )
    
    print(f"Enhanced prompt: {enhanced}")
    print(f"Details: {details}")
    print("✅ Enhance prompt test completed\n")

def test_view_history():
    """Test the view history functionality."""
    print("🧪 Testing view history function...")
    
    # Test history viewing
    history_text, details = view_history_func(
        limit=5,
        search_term="",
        provider_filter="all"
    )
    
    print(f"History: {history_text}")
    print(f"Details: {details}")
    print("✅ View history test completed\n")

def test_setup_status():
    """Test the setup status function."""
    print("🧪 Testing setup status function...")
    
    status = get_setup_status()
    print(f"Status: {status}")
    print("✅ Setup status test completed\n")

if __name__ == "__main__":
    print("🎨 Testing Image Generation Assistant UI Functions\n")
    
    # Set up minimal environment for testing
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("FAL_KEY"):
        print("⚠️ No API keys found. Some tests may show 'not configured' messages.")
        print("This is expected if you haven't set up API keys yet.\n")
    
    test_setup_status()
    test_enhance_prompt()
    test_view_history()
    
    print("🎉 All tests completed!") 