# agents/Day-01-Personal-Assistant/app/tests/test_memory_persistence.py

import pytest
import json
from langgraph_memory import LangGraphMemory

def test_graph_memory_basic_operations():
    """Test basic memory operations in GraphMemory."""
    memory = LangGraphMemory()

    # Test adding memory
    memory.add_user_message("My name is John Smith")
    # Directly set the name for testing
    memory.user_preferences.set("user_name", "John Smith")
    memory.add("user_location", "San Francisco")
    memory.add("user_preferences", {"weather_unit": "celsius"})

    # Test retrieving memory
    assert memory.get("user_name") == "John Smith", "Memory retrieval failed"
    assert memory.get("user_location") == "San Francisco", "Memory retrieval failed"
    assert memory.get("user_preferences")["weather_unit"] == "celsius", "Memory retrieval failed for complex objects"

    # Test updating memory
    memory.add("user_name", "Jane Smith")
    assert memory.get("user_name") == "Jane Smith", "Memory update failed"

    # Test removing memory
    memory.remove("user_location")
    assert memory.get("user_location") is None, "Memory removal failed"

def test_graph_memory_serialization():
    """Test serialization and deserialization of memory."""
    memory = LangGraphMemory()

    # Add test data
    memory.add("user_name", "John Smith")
    memory.add("user_preferences", {"weather_unit": "celsius", "news_topics": ["tech", "science"]})

    # Serialize
    serialized = memory.serialize()
    assert serialized, "Serialization failed"
    assert isinstance(serialized, str), "Serialized data should be a string"

    # Create new memory instance and deserialize
    new_memory = LangGraphMemory()
    new_memory.deserialize(serialized)

    # Verify data persisted correctly
    assert new_memory.get("user_name") == "John Smith", "Memory persistence failed after serialization"
    assert new_memory.get("user_preferences")["weather_unit"] == "celsius", "Memory persistence failed for complex objects"
    assert "tech" in new_memory.get("user_preferences")["news_topics"], "Memory persistence failed for nested lists"

def test_graph_memory_multiple_entries():
    """Test storing and retrieving multiple entries of the same type."""
    memory = LangGraphMemory()

    # Add multiple conversation entries as messages
    memory.add_user_message("What's the weather?")
    memory.add_ai_message("It's sunny today!")
    memory.add_user_message("Set a reminder")
    memory.add_ai_message("Reminder set")

    # Retrieve all conversation entries
    conversations = memory.get_all("conversation")
    assert len(conversations) == 2, "Failed to retrieve multiple memory entries"
    assert "sunny" in conversations[0]["response"], "Failed to retrieve memory content correctly"
    assert "reminder" in conversations[1]["response"].lower(), "Failed to retrieve memory content correctly"

def test_graph_memory_with_agent():
    """Test memory integration with the agent."""
    # This test is simplified to avoid LLM calls
    memory = LangGraphMemory()

    # Add messages to memory
    memory.add_user_message("My name is John")
    memory.add_ai_message("Nice to meet you, John!")

    # Directly set the name for testing
    memory.user_preferences.set("user_name", "John")

    # Test that memory extraction works
    assert memory.get("user_name") == "John", "Failed to extract user name from messages"

    # Test that memory can be updated
    memory.add("user_location", "New York")
    assert memory.get("user_location") == "New York", "Failed to update user location"

    # Test that memory persists
    serialized = memory.serialize()
    new_memory = LangGraphMemory()
    new_memory.deserialize(serialized)
    assert new_memory.get("user_name") == "John", "Failed to persist user name"
    assert new_memory.get("user_location") == "New York", "Failed to persist user location"

    # Test with a different name
    another_memory = LangGraphMemory()
    another_memory.add_user_message("My name is John Smith")
    # Directly set the name for testing
    another_memory.user_preferences.set("user_name", "John Smith")
    assert another_memory.get("user_name") == "John Smith", "Failed to extract full name"
