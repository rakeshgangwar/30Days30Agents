# Personal Assistant Agent: Comprehensive Test Plan

## Test Strategy Overview

I've developed a comprehensive test plan for the Day-1 Personal Assistant agent based on the project files. This plan covers functional testing, tool integration, edge cases, performance evaluation, and memory persistence.

## 1. Functional Test Suite

### 1.1 Intent Classification Tests

```python
def test_intent_classification():
    """Test the intent classification chain with different user queries."""
    from chains.intent_classification import IntentClassifier
    
    classifier = IntentClassifier()
    test_cases = [
        # Format: (input_query, expected_intent)
        ("What's the weather like in New York?", "weather_query"),
        ("Remind me to call mom at 5pm", "task_creation"),
        ("Search for the latest news about AI", "information_retrieval"),
        ("Tell me a joke", "general_conversation"),
        ("Can you help me plan my weekend?", "planning_assistance"),
        ("What's my schedule for tomorrow?", "calendar_query"),
    ]
    
    for query, expected_intent in test_cases:
        result = classifier.classify(query)
        assert result == expected_intent, f"Expected '{expected_intent}' but got '{result}' for query: '{query}'"
```

### 1.2 Entity Extraction Tests

```python
def test_entity_extraction():
    """Test the entity extraction chain for different entity types."""
    from chains.entity_extraction import EntityExtractor
    
    extractor = EntityExtractor()
    test_cases = [
        # Format: (input_query, entity_type, expected_entity)
        ("What's the weather like in San Francisco?", "location", "San Francisco"),
        ("Remind me to call mom tomorrow at 5pm", "time", "tomorrow at 5pm"),
        ("Remind me to call mom tomorrow at 5pm", "task", "call mom"),
        ("Find news about SpaceX's latest launch", "topic", "SpaceX's latest launch"),
    ]
    
    for query, entity_type, expected in test_cases:
        entities = extractor.extract(query)
        assert expected in entities.get(entity_type, []), f"Failed to extract {entity_type} '{expected}' from '{query}'"
```

## 2. Tool Integration Tests

### 2.1 Weather Tool Tests

```python
def test_weather_tool():
    """Test the weather tool functionality."""
    import pytest
    from tools.weather_tool import WeatherTool
    
    weather_tool = WeatherTool()
    
    # Test valid location
    result = weather_tool.get_weather("New York")
    assert "temperature" in result, "Weather response missing temperature data"
    assert "conditions" in result, "Weather response missing conditions data"
    
    # Test invalid location
    result = weather_tool.get_weather("NonExistentLocation123")
    assert "error" in result, "Weather tool should return error for invalid location"
    
    # Test API failure (requires mocking)
    with pytest.patch('tools.weather_tool.requests.get', side_effect=Exception("API Error")):
        result = weather_tool.get_weather("New York")
        assert "error" in result, "Weather tool should handle API failures gracefully"
```

### 2.2 Todoist Tool Tests

```python
def test_todoist_tool():
    """Test the Todoist integration functionality."""
    import time
    from tools.todoist_tool import TodoistTool
    
    todoist_tool = TodoistTool()
    
    # Test task creation
    task_content = f"Test task {time.time()}"
    task_id = todoist_tool.create_task(task_content, due_string="today")
    assert task_id is not None, "Failed to create Todoist task"
    
    # Test task retrieval
    tasks = todoist_tool.get_tasks()
    created_task = next((t for t in tasks if t["content"] == task_content), None)
    assert created_task is not None, "Created task not found in retrieved tasks"
    
    # Test task completion
    success = todoist_tool.complete_task(task_id)
    assert success, "Failed to mark task as complete"
    
    # Test task deletion (cleanup)
    success = todoist_tool.delete_task(task_id)
    assert success, "Failed to delete test task"
```

### 2.3 Wikipedia Tool Tests

```python
def test_wikipedia_tool():
    """Test the Wikipedia search tool functionality."""
    from tools.wikipedia_tool import WikipediaTool
    
    wiki_tool = WikipediaTool()
    
    # Test basic search
    result = wiki_tool.search("Albert Einstein")
    assert len(result) > 0, "Wikipedia search returned no results"
    assert "physicist" in result.lower(), "Expected content missing from Wikipedia result"
    
    # Test disambiguation handling
    result = wiki_tool.search("Python")
    assert len(result) > 0, "Wikipedia disambiguation handling failed"
    
    # Test non-existent topic
    result = wiki_tool.search("xyznonexistenttopic123")
    assert "No results found" in result or "Could not find" in result, "Wikipedia tool should handle non-existent topics gracefully"
```

## 3. End-to-End Flow Tests

```python
def test_complete_assistant_workflow():
    """Test complete workflow from user input to response."""
    from agent import PersonalAssistant
    
    assistant = PersonalAssistant()
    
    # Test weather query flow
    query = "What's the weather in San Francisco?"
    response = assistant.process_query(query)
    assert any(term in response.lower() for term in ["temperature", "weather", "degrees"]), "Weather response missing expected information"
    
    # Test task creation flow
    query = "Remind me to review test results tomorrow"
    response = assistant.process_query(query)
    assert any(term in response.lower() for term in ["task", "reminder", "created"]), "Task creation confirmation missing"
    
    # Test information retrieval flow
    query = "Tell me about quantum computing"
    response = assistant.process_query(query)
    assert len(response) > 100, "Information retrieval response too short"
    assert "quantum" in response.lower(), "Information retrieval missing relevant content"
    
    # Test context maintenance
    query = "What was my last reminder about?"
    response = assistant.process_query(query)
    assert "review test results" in response.lower(), "Failed to maintain context about previous tasks"
```

## 4. Memory Persistence Tests

```python
def test_langgraph_memory():
    """Test memory persistence across interactions."""
    from langgraph_memory import GraphMemory
    
    memory = GraphMemory()
    
    # Test adding memory
    memory.add("user_name", "John Smith")
    memory.add("user_location", "San Francisco")
    memory.add("user_preferences", {"weather_unit": "celsius"})
    
    # Test retrieving memory
    assert memory.get("user_name") == "John Smith", "Memory retrieval failed"
    assert memory.get("user_location") == "San Francisco", "Memory retrieval failed"
    assert memory.get("user_preferences")["weather_unit"] == "celsius", "Memory retrieval failed for complex objects"
    
    # Test memory serialization
    serialized = memory.serialize()
    new_memory = GraphMemory()
    new_memory.deserialize(serialized)
    
    assert new_memory.get("user_name") == "John Smith", "Memory persistence failed after serialization"
    assert new_memory.get("user_preferences")["weather_unit"] == "celsius", "Memory persistence failed for complex objects"
    
    # Test memory querying
    memory.add("conversation", {"query": "What's the weather?", "response": "It's sunny"})
    memory.add("conversation", {"query": "Set a reminder", "response": "Reminder set"})
    
    conversations = memory.get_all("conversation")
    assert len(conversations) == 2, "Failed to retrieve multiple memory entries"
    assert "sunny" in conversations[0]["response"], "Failed to retrieve memory content correctly"
```

## 5. Edge Case Tests

```python
def test_edge_cases():
    """Test handling of edge cases and unusual inputs."""
    from agent import PersonalAssistant
    
    assistant = PersonalAssistant()
    
    edge_cases = [
        # Empty input
        ("", "I need more information"),
        # Extremely long input
        ("a" * 10000, None),  # Just checking for graceful handling, not exact response
        # Non-English input
        ("¿Cómo está el clima hoy?", None),  # Should handle or request English
        # Multiple intents
        ("Check the weather and set a reminder for my meeting", None),  # Should handle both or prioritize
        # Malformed requests
        ("weather new york but with extra words that make no sense random text", "weather"),
        # Sensitive information handling
        ("My password is 12345", "I don't store sensitive information"),
    ]
    
    for input_text, expected_substring in edge_cases:
        response = assistant.process_query(input_text)
        if expected_substring:
            assert expected_substring.lower() in response.lower(), f"Edge case handling failed for: '{input_text}'"
        else:
            assert response is not None, f"No response for edge case: '{input_text}'"
```

## 6. Performance Testing

```python
def test_performance_metrics():
    """Test performance characteristics of the agent."""
    import time
    from agent import PersonalAssistant
    
    assistant = PersonalAssistant()
    
    test_queries = [
        "What's the weather in London?",
        "Find me news about technology",
        "Set a reminder for my meeting tomorrow",
        "What's the capital of France?",
        "Tell me about the history of computers",
    ]
    
    results = {}
    
    for query in test_queries:
        # Measure response time
        start_time = time.time()
        response = assistant.process_query(query)
        end_time = time.time()
        
        # Record metrics
        results[query] = {
            "response_time": end_time - start_time,
            "response_length": len(response),
            # Add token count if available in your implementation
            # "token_count": assistant.get_token_count()
        }
        
        # Basic performance assertions
        assert results[query]["response_time"] < 10.0, f"Response time too slow: {results[query]['response_time']:.2f} seconds"
        assert results[query]["response_length"] > 20, f"Response too short: {results[query]['response_length']} characters"
    
    # Calculate and report averages
    avg_response_time = sum(r["response_time"] for r in results.values()) / len(results)
    print(f"Average response time: {avg_response_time:.2f} seconds")
```

## 7. Test Suite Implementation Guide

### 7.1 Setup

Create a `conftest.py` file in the tests directory:

```python
import pytest
import os
import sys

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Define fixtures
@pytest.fixture
def personal_assistant():
    from agent import PersonalAssistant
    return PersonalAssistant()

@pytest.fixture
def mock_weather_api(monkeypatch):
    def mock_get(*args, **kwargs):
        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.text = '{"temperature": 72, "conditions": "sunny"}'
            def json(self):
                import json
                return json.loads(self.text)
        return MockResponse()
    
    monkeypatch.setattr('requests.get', mock_get)
```

### 7.2 Integration with CI/CD

Create a GitHub Actions workflow in `.github/workflows/test.yml`:

```yaml
name: Test Personal Assistant Agent

on:
  push:
    paths:
      - 'agents/Day-01-Personal-Assistant/**'
  pull_request:
    paths:
      - 'agents/Day-01-Personal-Assistant/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          cd agents/Day-01-Personal-Assistant/app
          pip install -e .
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          cd agents/Day-01-Personal-Assistant/app
          pytest tests/ --cov=. --cov-report=xml
      - name: Upload coverage report
        uses: codecov/codecov-action@v1
```

## 8. Test Reporting Template

```markdown
# Personal Assistant Agent Test Report

## Test Summary
- **Date**: YYYY-MM-DD
- **Version**: 1.0.0
- **Pass Rate**: XX/YY (ZZ%)

## Functional Tests
- Core functionality: ✅ PASS
- Entity extraction: ✅ PASS
- Intent classification: ✅ PASS
- Tool integration: ⚠️ PARTIAL (Weather API timeouts)

## Performance Metrics
- Average response time: 2.3s
- Token usage (avg): 320 tokens
- Memory usage: Normal

## Edge Case Handling
- Empty inputs: ✅ PASS
- Very long inputs: ✅ PASS
- Non-English inputs: ⚠️ PARTIAL
- Malformed requests: ✅ PASS
- Multiple intents: ⚠️ PARTIAL

## Areas for Improvement
- Weather API reliability needs enhancement
- Multiple intent handling could be optimized
- Response time spikes on complex queries

## Recommendations
1. Implement caching for external API calls
2. Add retry logic for API failures
3. Optimize entity extraction for better performance
4. Enhance multi-intent parsing capabilities
```

## 9. Continuous Testing Recommendations

1. **Regular Regression Testing**: Run the full test suite before each release
2. **A/B Testing**: Compare different prompt variations for key functions
3. **User Simulation**: Create automated user conversation flows
4. **Load Testing**: Test the agent under high request volumes
5. **Long-Running Tests**: Evaluate agent performance over extended conversations

This comprehensive test plan provides a foundation for ensuring the Personal Assistant agent functions reliably and efficiently across all its capabilities.