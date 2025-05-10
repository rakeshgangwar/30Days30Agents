"""
Tests for the OpenRouter service integration.
"""
import os
import pytest
import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.services.openrouter_service import OpenRouterService

from dotenv import load_dotenv

load_dotenv()

@pytest.mark.asyncio
async def test_generate_draft_mock():
    """Test the draft generation with a mocked OpenAI client."""
    # Create a mock for the OpenAI client
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    
    # Set up the mock response structure
    mock_message.content = "This is a test generated text."
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion
    
    # Create the service with the mocked client
    service = OpenRouterService()
    service.client = mock_client
    
    # Call the service method
    result = await service.generate_draft("Write a test draft")
    
    # Check the result
    assert result == "This is a test generated text."
    
    # Verify that the client was called with correct parameters
    mock_client.chat.completions.create.assert_called_once()
    # Get the call arguments
    call_args = mock_client.chat.completions.create.call_args
    
    # Check key parameters
    assert call_args[1]['model'] == service.default_model
    assert call_args[1]['temperature'] == 0.7
    assert len(call_args[1]['messages']) >= 1
    
    # Check that the user message contains our prompt
    user_messages = [msg for msg in call_args[1]['messages'] if msg['role'] == 'user']
    assert len(user_messages) == 1
    assert "Write a test draft" in user_messages[0]['content']


@pytest.mark.asyncio
async def test_analyze_grammar_style_mock():
    """Test the grammar analysis with a mocked OpenAI client."""
    # Create a mock for the OpenAI client
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()
    
    # Set up the mock response structure
    mock_message.content = '{"issues": [{"type": "grammar", "description": "test issue", "severity": "warning"}]}'
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_completion
    
    # Create the service with the mocked client
    service = OpenRouterService()
    service.client = mock_client
    
    # Call the service method
    result = await service.analyze_grammar_style("This is a test text.")
    
    # Check that we got back a dictionary with expected keys
    assert isinstance(result, dict)
    assert "raw_analysis" in result
    assert "model_used" in result
    
    # Check the raw analysis matches our mock data
    assert result["raw_analysis"] == mock_message.content


@pytest.mark.skipif(not os.environ.get("OPENROUTER_API_KEY"), 
                   reason="OPENROUTER_API_KEY not set in environment")
@pytest.mark.asyncio
async def test_live_openrouter_connection():
    """
    Test a live connection to OpenRouter.
    
    This test is skipped if OPENROUTER_API_KEY is not set in the environment.
    Only run this test when specifically testing the live API connection.
    """
    service = OpenRouterService()
    result = await service.generate_draft(
        "Write a one-sentence test.", 
        max_length=50
    )
    
    # Check that we got a non-empty string back
    assert isinstance(result, str)
    assert len(result) > 0


if __name__ == "__main__":
    # Simple script to run tests directly
    async def run_tests():
        # Run the mock tests
        await test_generate_draft_mock()
        await test_analyze_grammar_style_mock()
        
        # Only run live test if API key is set
        if os.environ.get("OPENROUTER_API_KEY"):
            print("Running live test with OpenRouter API...")
            await test_live_openrouter_connection()
            print("Live test completed successfully!")
        else:
            print("Skipping live test (OPENROUTER_API_KEY not set)")
        
        print("All tests completed successfully!")
    
    # Run the tests
    asyncio.run(run_tests())