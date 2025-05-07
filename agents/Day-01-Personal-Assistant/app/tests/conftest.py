# agents/Day-01-Personal-Assistant/app/tests/conftest.py

import pytest
import os
import sys
import json

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def personal_assistant():
    """Fixture to create a personal assistant instance for testing."""
    from agent import PersonalAssistantAgent
    assistant = PersonalAssistantAgent()
    return assistant

@pytest.fixture
def mock_weather_api(mocker):
    """Fixture to mock the weather API responses."""
    def mock_get(*args, **kwargs):
        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.text = json.dumps({
                    "location": {"name": "New York", "country": "USA"},
                    "current": {
                        "temperature": 72,
                        "condition": {"text": "Sunny", "code": 1000}
                    }
                })

            def json(self):
                return json.loads(self.text)

        return MockResponse()

    # Apply the mock to requests.get
    return mocker.patch('requests.get', side_effect=mock_get)

@pytest.fixture
def mock_todoist_api(mocker):
    """Fixture to mock Todoist API responses."""
    # Mock task creation
    create_task_mock = mocker.patch('tools.todoist_tool.TodoistCreateTool._run')
    create_task_mock.return_value = {
        "error": False,
        "task_id": "task123",
        "content": "Test task",
        "message": "Successfully created task: Test task"
    }

    # Mock task retrieval
    get_tasks_mock = mocker.patch('tools.todoist_tool.TodoistListTool._run')
    get_tasks_mock.return_value = {
        "error": False,
        "tasks": [
            {"id": "task123", "content": "Test task", "due": {"date": "2025-07-05"}}
        ],
        "count": 1,
        "filter": None
    }

    # Mock task completion
    complete_task_mock = mocker.patch('tools.todoist_tool.TodoistCompleteTool._run')
    complete_task_mock.return_value = {
        "error": False,
        "task_id": "task123",
        "message": "Task completed successfully"
    }

    # Mock task deletion
    # No direct delete tool in the implementation, so we'll create a mock
    delete_task_mock = mocker.MagicMock()
    delete_task_mock.return_value = True

    return {
        "create": create_task_mock,
        "get": get_tasks_mock,
        "complete": complete_task_mock,
        "delete": delete_task_mock
    }

@pytest.fixture
def mock_wikipedia_api(mocker):
    """Fixture to mock Wikipedia API responses."""
    wiki_search_mock = mocker.patch('tools.wikipedia_tool.WikipediaTool._run')
    wiki_search_mock.return_value = "Albert Einstein was a German-born theoretical physicist who developed the theory of relativity, one of the two pillars of modern physics."
    return wiki_search_mock

@pytest.fixture
def mock_news_api(mocker):
    """Fixture to mock news API responses."""
    news_mock = mocker.patch('tools.news_tool.NewsTool._run')
    news_mock.return_value = [
        {"title": "Test news 1", "description": "Test description 1", "url": "https://example.com/1"},
        {"title": "Test news 2", "description": "Test description 2", "url": "https://example.com/2"}
    ]
    return news_mock
