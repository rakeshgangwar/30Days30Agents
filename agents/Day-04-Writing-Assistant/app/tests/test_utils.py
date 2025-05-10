"""
Tests for utility functions.
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.utils.generate_api_key import main as generate_api_key_main
from app.core.security import generate_api_key


def test_generate_api_key_script():
    """Test the generate_api_key script."""
    # Mock the generate_api_key function to return a known value
    mock_key = "test-api-key-12345"
    
    # Mock stdout to capture output
    mock_stdout = StringIO()
    
    with patch("app.utils.generate_api_key.generate_api_key", return_value=mock_key), \
         patch("sys.stdout", mock_stdout):
        # Run the script
        generate_api_key_main()
        
        # Check the output
        output = mock_stdout.getvalue()
        assert "Generated API Key:" in output
        assert mock_key in output
        assert f"API_KEY={mock_key}" in output
