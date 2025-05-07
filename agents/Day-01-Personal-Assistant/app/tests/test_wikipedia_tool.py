# agents/Day-01-Personal-Assistant/app/tests/test_wikipedia_tool.py

import pytest
from tools.wikipedia_tool import WikipediaTool

def test_wikipedia_tool_basic_search():
    """Test basic Wikipedia search functionality."""
    wiki_tool = WikipediaTool()
    
    # Test searching for a well-known entity
    result = wiki_tool.search("Albert Einstein")
    assert result, "Wikipedia search returned empty result"
    assert isinstance(result, str), "Wikipedia search should return a string"
    assert len(result) > 100, "Wikipedia result seems too short"
    assert "physicist" in result.lower(), "Expected content missing from Wikipedia result"

def test_wikipedia_tool_disambiguation(mocker):
    """Test handling of disambiguation pages."""
    # Mock Wikipedia API to return a disambiguation-like response
    mock_search = mocker.patch('wikipedia.search')
    mock_search.return_value = ["Python (programming)", "Python (snake)", "Monty Python"]
    
    mock_summary = mocker.patch('wikipedia.summary')
    mock_summary.side_effect = [
        "Python is a programming language",
        "Python is a genus of snakes",
        "Monty Python was a comedy group"
    ]
    
    wiki_tool = WikipediaTool()
    result = wiki_tool.search("Python")
    
    assert result, "Wikipedia disambiguation handling failed"
    assert "programming" in result.lower() or "snake" in result.lower() or "comedy" in result.lower(), \
        "Disambiguation handling should return one of the possible meanings"

def test_wikipedia_tool_nonexistent_topic(mocker):
    """Test searching for non-existent topics."""
    # Mock Wikipedia API to simulate a page not found
    mock_search = mocker.patch('wikipedia.search')
    mock_search.return_value = []
    
    mock_summary = mocker.patch('wikipedia.summary')
    mock_summary.side_effect = Exception("Page not found")
    
    wiki_tool = WikipediaTool()
    result = wiki_tool.search("xyznonexistenttopic123")
    
    assert result, "Wikipedia tool should return a message for non-existent topics"
    assert "no results" in result.lower() or "not found" in result.lower() or "couldn't find" in result.lower(), \
        "Should indicate that the topic wasn't found"

def test_wikipedia_tool_error_handling(mocker):
    """Test error handling in Wikipedia tool."""
    # Mock Wikipedia API to raise an exception
    mock_search = mocker.patch('wikipedia.search')
    mock_search.side_effect = Exception("API Error")
    
    wiki_tool = WikipediaTool()
    result = wiki_tool.search("Albert Einstein")
    
    assert result, "Wikipedia tool should handle errors gracefully"
    assert "error" in result.lower() or "unable" in result.lower() or "couldn't" in result.lower(), \
        "Error message should be returned when API fails"
