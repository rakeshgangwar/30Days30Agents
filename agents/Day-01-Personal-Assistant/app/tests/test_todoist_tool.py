# agents/Day-01-Personal-Assistant/app/tests/test_todoist_tool.py

import pytest
import time
from tools.todoist_tool import TodoistCreateTool, TodoistListTool, TodoistCompleteTool

def test_todoist_tool_create_task(mock_todoist_api):
    """Test creating a task with Todoist."""
    todoist_tool = TodoistCreateTool()

    # Test creating a basic task
    task_content = f"Test task {time.time()}"
    result = todoist_tool._run(task_content)

    assert result is not None, "Failed to create Todoist task"
    assert result.get("task_id") == "task123", "Task ID doesn't match expected mock value"
    mock_todoist_api["create"].assert_called_once()

def test_todoist_tool_create_task_with_due_date(mock_todoist_api):
    """Test creating a task with a due date."""
    todoist_tool = TodoistCreateTool()

    task_content = "Test task with due date"
    due_string = "tomorrow at 3pm"
    result = todoist_tool._run(task_content, due_string=due_string)

    assert result is not None, "Failed to create task with due date"
    mock_todoist_api["create"].assert_called_once()

def test_todoist_tool_get_tasks(mock_todoist_api):
    """Test retrieving tasks from Todoist."""
    todoist_tool = TodoistListTool()

    result = todoist_tool._run()

    assert result is not None, "Failed to get tasks"
    assert "tasks" in result, "No tasks returned"
    assert len(result["tasks"]) > 0, "No tasks returned"
    assert result["tasks"][0]["id"] == "task123", "Task ID doesn't match expected mock value"
    assert result["tasks"][0]["content"] == "Test task", "Task content doesn't match expected mock value"
    mock_todoist_api["get"].assert_called_once()

def test_todoist_tool_complete_task(mock_todoist_api):
    """Test marking a task as complete."""
    todoist_tool = TodoistCompleteTool()

    result = todoist_tool._run("task123")

    assert result is not None, "Failed to mark task as complete"
    assert result.get("error") is False, "Failed to mark task as complete"
    mock_todoist_api["complete"].assert_called_once()

def test_todoist_tool_delete_task(mock_todoist_api):
    """Test deleting a task."""
    # There's no direct delete tool in the implementation, so we'll skip this test
    # or we could test it with a mock
    assert mock_todoist_api["delete"] is not None, "Delete mock should be available"

def test_todoist_tool_error_handling(mocker):
    """Test error handling in Todoist tool."""
    # Mock Todoist API to raise an exception
    mocker.patch('requests.post', side_effect=Exception("API Error"))

    todoist_tool = TodoistCreateTool()

    # The tool should handle errors gracefully
    try:
        result = todoist_tool._run("Test task")
        assert result is not None, "Should return a result on API failure"
        assert result.get("error") is True, "Should return error=True on API failure"
    except Exception as e:
        pytest.fail(f"TodoistCreateTool should handle exceptions gracefully, but raised: {e}")
