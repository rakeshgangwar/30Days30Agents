# agents/Day-01-Personal-Assistant/app/tests/test_entity_extraction.py

import pytest
from chains.entity_extraction import EntityExtractionChain

def test_entity_extraction():
    """Test the entity extraction chain for different entity types."""
    extractor = EntityExtractionChain()

    test_cases = [
        # Format: (input_query, entity_type, expected_entity)
        ("What's the weather like in San Francisco?", "location", "San Francisco"),
        ("Remind me to call mom tomorrow at 5pm", "time", "5pm"),
        ("Remind me to call mom tomorrow at 5pm", "task", "call mom"),
        ("Find news about SpaceX's latest launch", "topic", "SpaceX's latest launch"),
    ]

    for query, entity_type, expected in test_cases:
        entities = extractor.extract_entities(query, intent="WEATHER")
        assert entities, f"No entities extracted from '{query}'"
        # The entities are nested under the intent
        if entity_type == "location":
            assert "location" in entities.get("WEATHER", {}), f"Entity type '{entity_type}' not found in extraction results"
            assert expected in entities.get("WEATHER", {}).get("location", ""), f"Failed to extract {entity_type} '{expected}' from '{query}'"
        elif entity_type == "task":
            assert "task" in entities.get("REMINDER", {}), f"Entity type '{entity_type}' not found in extraction results"
            assert expected in entities.get("REMINDER", {}).get("task", ""), f"Failed to extract {entity_type} '{expected}' from '{query}'"
        elif entity_type == "time":
            assert "time" in entities.get("REMINDER", {}), f"Entity type '{entity_type}' not found in extraction results"
            assert expected in entities.get("REMINDER", {}).get("time", ""), f"Failed to extract {entity_type} '{expected}' from '{query}'"
        elif entity_type == "topic":
            assert "topic" in entities.get("NEWS", {}), f"Entity type '{entity_type}' not found in extraction results"
            assert expected in entities.get("NEWS", {}).get("topic", ""), f"Failed to extract {entity_type} '{expected}' from '{query}'"

def test_multiple_entity_extraction():
    """Test extracting multiple entities from a single query."""
    extractor = EntityExtractionChain()

    query = "Remind me to call mom tomorrow at 5pm"
    entities = extractor.extract_entities(query, intent="REMINDER")

    assert "task" in entities.get("REMINDER", {}), "Failed to extract task entity"
    assert "time" in entities.get("REMINDER", {}), "Failed to extract time entity"
    assert "call mom" in entities.get("REMINDER", {}).get("task", ""), "Extracted incorrect task entity"
    assert "5pm" in entities.get("REMINDER", {}).get("time", ""), "Failed to extract time correctly"

def test_entity_extraction_edge_cases():
    """Test entity extraction with edge cases."""
    extractor = EntityExtractionChain()

    # Empty input
    entities = extractor.extract_entities("", intent="UNKNOWN")
    # The implementation returns default entities, so we'll just check that it doesn't crash
    assert entities is not None, "Empty input should return some entities"

    # Very long input
    long_input = "weather " * 100 + "in New York"
    entities = extractor.extract_entities(long_input, intent="WEATHER")
    assert "location" in entities.get("WEATHER", {}), "Failed to extract location from long input"
    assert "New York" in entities.get("WEATHER", {}).get("location", ""), "Extracted incorrect location from long input"

    # Ambiguous input
    ambiguous = "Tell me about Python"
    entities = extractor.extract_entities(ambiguous, intent="GENERAL_QUESTION")
    assert entities, "Should extract some entities from ambiguous input"
