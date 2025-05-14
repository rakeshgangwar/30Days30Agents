"""
Task Automation Agent - Main Application

This is the main entry point for the Task Automation Agent, which combines
PydanticAI for intelligent processing and Beehive for event-driven task execution.
"""

import os
import asyncio
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, ModelRetry

# Import our models
from models.user_task import TaskResult
from models.dependencies import AppDependencies

# Load environment variables
load_dotenv()

# Create PydanticAI agent
agent = Agent(
    os.getenv("MODEL_NAME", "openai:gpt-4"),
    deps_type=AppDependencies,
    output_type=str,
    system_prompt="You are a task automation agent that helps users automate repetitive tasks. "
                 "You can interact with files, APIs, and set up automated workflows using Beehive."
)

# File operations tools
@agent.tool
def list_files(ctx: RunContext[AppDependencies], directory: str = ".") -> List[str]:
    """
    List files in a directory.

    Args:
        directory: The directory to list files from (default: current directory)

    Returns:
        List of filenames in the directory
    """
    try:
        return os.listdir(directory)
    except Exception as e:
        raise ModelRetry(f"Error listing files in {directory}: {str(e)}")

@agent.tool
def read_file(ctx: RunContext[AppDependencies], file_path: str) -> str:
    """
    Read the contents of a file.

    Args:
        file_path: Path to the file to read

    Returns:
        Contents of the file as a string
    """
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise ModelRetry(f"File {file_path} not found. Please provide a valid file path.")
    except Exception as e:
        raise ModelRetry(f"Error reading file {file_path}: {str(e)}")

@agent.tool
def write_file(ctx: RunContext[AppDependencies], file_path: str, content: str) -> str:
    """
    Write content to a file.

    Args:
        file_path: Path to the file to write
        content: Content to write to the file

    Returns:
        Success message or error
    """
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        raise ModelRetry(f"Error writing to file {file_path}: {str(e)}")

# API tools
@agent.tool
async def make_get_request(ctx: RunContext[AppDependencies], url: str, params: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None) -> str:
    """
    Make a GET request to an API.

    Args:
        url: The URL to make the request to
        params: Optional query parameters
        headers: Optional request headers

    Returns:
        Response from the API as a string
    """
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        # Try to parse as JSON, fall back to text if not JSON
        try:
            return str(response.json())
        except:
            return response.text
    except Exception as e:
        raise ModelRetry(f"Error making GET request to {url}: {str(e)}")

@agent.tool
async def make_post_request(ctx: RunContext[AppDependencies], url: str, data: Optional[Dict[str, Any]] = None,
                      json_data: Optional[Dict[str, Any]] = None,
                      headers: Optional[Dict[str, str]] = None) -> str:
    """
    Make a POST request to an API.

    Args:
        url: The URL to make the request to
        data: Optional form data
        json_data: Optional JSON data
        headers: Optional request headers

    Returns:
        Response from the API as a string
    """
    try:
        response = requests.post(url, data=data, json=json_data, headers=headers)
        response.raise_for_status()

        try:
            return str(response.json())
        except:
            return response.text
    except Exception as e:
        raise ModelRetry(f"Error making POST request to {url}: {str(e)}")

# Beehive tools
@agent.tool
async def setup_web_monitor(ctx: RunContext[AppDependencies], url: str, css_selector: str,
                      target_value: float, condition: str,
                      callback_action: str, callback_params: Dict[str, Any]) -> str:
    """
    Set up a web monitoring task in Beehive.

    Args:
        url: The URL to monitor
        css_selector: CSS selector for the element to monitor
        target_value: Target value to compare against
        condition: Comparison condition (e.g., 'less_than', 'greater_than')
        callback_action: Action to take when condition is met
        callback_params: Parameters for the callback action

    Returns:
        Task ID or error message
    """
    try:
        data = {
            "task_type": "web_monitor",
            "config": {
                "url": url,
                "css_selector": css_selector,
                "target_value": target_value,
                "condition": condition,
                "callback": {
                    "action": callback_action,
                    "params": callback_params
                }
            }
        }

        response = requests.post(
            f"{ctx.deps.mcp_server_url}/tasks",
            json=data,
            headers=ctx.deps.get_mcp_headers()
        )
        response.raise_for_status()
        return str(response.json())
    except Exception as e:
        raise ModelRetry(f"Error setting up web monitor: {str(e)}")

@agent.tool
async def setup_scheduled_task(ctx: RunContext[AppDependencies], schedule: str, task_type: str,
                         task_params: Dict[str, Any]) -> str:
    """
    Set up a scheduled task in Beehive.

    Args:
        schedule: Cron expression for the schedule
        task_type: Type of task to schedule
        task_params: Parameters for the task

    Returns:
        Task ID or error message
    """
    try:
        data = {
            "schedule": schedule,
            "task_type": task_type,
            "params": task_params
        }

        response = requests.post(
            f"{ctx.deps.mcp_server_url}/scheduled-tasks",
            json=data,
            headers=ctx.deps.get_mcp_headers()
        )
        response.raise_for_status()
        return str(response.json())
    except Exception as e:
        raise ModelRetry(f"Error setting up scheduled task: {str(e)}")

async def process_user_input(user_input: str) -> TaskResult:
    """
    Process user input, collect parameters if needed, and execute the task.

    Args:
        user_input: The natural language input from the user

    Returns:
        TaskResult: The result of the task execution
    """
    # Create dependencies
    deps = AppDependencies.from_env()

    # Parse the user input to understand the task
    result = await agent.run(
        user_input,
        deps=deps
    )

    # Create a TaskResult object
    task_result = TaskResult(
        task="Task execution",
        success=True,
        results=[result],
        summary=result
    )

    return task_result

async def main_async():
    """Async main entry point for the application."""
    print("Task Automation Agent initialized. Type 'exit' to quit.")

    while True:
        user_input = input("\nWhat task would you like me to automate? ")

        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        try:
            result = await process_user_input(user_input)
            print(f"\nTask: {result.task}")
            print(f"Success: {result.success}")
            print(f"Summary: {result.summary}")
        except Exception as e:
            print(f"Error: {str(e)}")

def main():
    """Main entry point for the application."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
