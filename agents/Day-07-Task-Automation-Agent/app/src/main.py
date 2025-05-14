"""
Task Automation Agent - Main Application

This is the main entry point for the Task Automation Agent, which combines
PydanticAI for intelligent processing and Beehive for event-driven task execution.
"""

import os
import asyncio
import requests
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, ModelRetry
from pydantic_ai.mcp import MCPServerStdio

# Import our models
from models.user_task import TaskResult
from models.dependencies import AppDependencies

# Load environment variables
load_dotenv()

# Create PydanticAI agent with enhanced system prompt
agent = Agent(
    os.getenv("MODEL_NAME", "openai:gpt-4o"),
    deps_type=AppDependencies,
    output_type=str,
    system_prompt="""You are a task automation agent that helps users automate repetitive tasks.
You can interact with files, APIs, and set up automated workflows using Beehive.

Beehive is an event and agent system that allows you to create automated workflows. It consists of:
1. Hives: These are plugins or integrations with various services like Twitter, GitHub, RSS, etc.
2. Bees: These are instances of Hives configured for specific tasks.
3. Chains: These connect events from one Bee to actions in another Bee.

You have access to Beehive MCP tools like:
- list_hives: List all available Hives
- get_hive_details: Get details about a specific Hive
- list_bees: List all configured Bees
- create_bee: Create a new Bee
- update_bee: Update an existing Bee
- delete_bee: Delete a Bee
- list_chains: List all Chains
- create_chain: Create a new Chain
- update_chain: Update an existing Chain
- delete_chain: Delete a Chain
- trigger_action: Trigger an action in a Bee

Some common Hives include Twitter, GitHub, RSS Feeds, HTTP Client, Telegram, Discord, and many others.
Use these tools to interact with the Beehive system and help users automate their tasks.
"""
)

# Create and register the Beehive MCP server
try:
    # Use the provided configuration
    beehive_config = {
        "autoApprove": [],
        "disabled": False,
        "timeout": 60,
        "command": "node",
        "args": ["/Users/rakeshgangwar/Projects/beehive-mcp-server/src/beehive-mcp.js"],
        "env": {
            "BEEHIVE_URL": "http://localhost:8181",
            "MCP_SERVER_NAME": "beehive"
        },
        "transportType": "stdio"
    }
    print(f"Beehive MCP server config: {json.dumps(beehive_config, indent=2)}")

    # Create the MCP server directly using the MCPServerStdio class
    command = beehive_config.get("command", "node")
    args = beehive_config.get("args", [])
    env_vars = beehive_config.get("env", {})

    # Merge with current environment
    full_env = os.environ.copy()
    full_env.update(env_vars)

    # Create the MCP server - this is the key part
    # The MCPServerStdio will start the server as a subprocess when agent.run_mcp_servers() is called
    beehive_server = MCPServerStdio(
        command=command,
        args=args,
        env=full_env
    )

    # Register the MCP server with the agent
    # This tells the agent to use this MCP server for tool calls
    agent.mcp_servers = [beehive_server]
    print("Beehive MCP server registered successfully")
except Exception as e:
    print(f"Warning: Failed to initialize Beehive MCP server: {str(e)}")
    print("The agent will continue to function, but Beehive-related tools may not work properly.")

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

# Note: We're removing the custom Beehive tool implementations
# The MCP server will handle these tools directly

async def process_user_input(user_input: str, message_history=None) -> TaskResult:
    """
    Process user input, collect parameters if needed, and execute the task.

    Args:
        user_input: The natural language input from the user
        message_history: Optional message history for continuing a conversation

    Returns:
        TaskResult: The result of the task execution
    """
    # Create dependencies
    deps = AppDependencies.from_env()

    try:
        # Check if the agent has MCP servers registered
        has_mcp_servers = hasattr(agent, 'mcp_servers') and len(agent.mcp_servers) > 0

        if has_mcp_servers:
            # Run the agent with the MCP server
            try:
                # Log that we're starting the MCP server
                print("Starting Beehive MCP server...")

                # This is the key part - we're using the run_mcp_servers context manager
                # to ensure the MCP server is running during the agent's execution
                async with agent.run_mcp_servers():
                    print("Beehive MCP server started successfully")

                    # Check if the user's input is related to Beehive
                    beehive_related = any(term in user_input.lower() for term in
                                         ['beehive', 'hive', 'bee', 'chain', 'trigger'])

                    if beehive_related:
                        print("Detected Beehive-related query, using MCP server tools")

                    # Parse the user input to understand the task
                    result = await agent.run(
                        user_input,
                        deps=deps,
                        message_history=message_history
                    )
            except Exception as mcp_error:
                # If there's an error with the MCP server, log it and continue without MCP
                error_str = str(mcp_error)
                print(f"Warning: MCP server error: {error_str}")
                print("Continuing without MCP server...")

                # Check if it's a validation error
                is_validation_error = "Exceeded maximum retries" in error_str and "for result validation" in error_str

                if is_validation_error:
                    print("Detected validation error - this is likely due to a mismatch in expected response formats")

                    # For Beehive-specific queries, provide a more helpful response
                    if "hive" in user_input.lower() or "bee" in user_input.lower():
                        # Create a special message for Beehive-related queries
                        if "list" in user_input.lower() and "hive" in user_input.lower():
                            # For listing hives, provide a generic response about Beehive hives
                            result = await agent.run(
                                "The user asked to list hives in Beehive. Please provide general information about " +
                                "what hives are in Beehive and mention that you couldn't connect to the server to get " +
                                "the actual list. Mention some common hives like Twitter, GitHub, RSS, etc.",
                                deps=deps,
                                message_history=message_history
                            )
                            return result
                        elif "twitter" in user_input.lower():
                            # For Twitter-specific queries
                            result = await agent.run(
                                "The user asked about the Twitter hive in Beehive. Please provide general information " +
                                "about what the Twitter hive does in Beehive based on your knowledge.",
                                deps=deps,
                                message_history=message_history
                            )
                            return result

                # Create a more informative error message for the user
                error_message = (
                    f"There was an issue with the Beehive MCP server: {error_str}. "
                    "This might be because the Beehive server is not running or there's a configuration issue. "
                    "I'll try to process your request without using Beehive-specific tools."
                )

                # Run the agent without the MCP server, but include the error message
                result = await agent.run(
                    f"Note: {error_message}\n\nUser request: {user_input}",
                    deps=deps,
                    message_history=message_history
                )
        else:
            # Run the agent without the MCP server
            result = await agent.run(
                user_input,
                deps=deps,
                message_history=message_history
            )

        # Convert result to string if it's not already
        result_str = str(result)

        # Create a TaskResult object
        task_result = TaskResult(
            task="Task execution",
            success=True,
            results=[result_str],
            summary=result_str,
            message_history=result.all_messages() if hasattr(result, 'all_messages') else message_history
        )
    except Exception as e:
        # Handle any errors
        task_result = TaskResult(
            task="Task execution",
            success=False,
            results=[],
            summary=f"Error: {str(e)}",
            error=str(e),
            message_history=message_history
        )

    return task_result

async def main_async():
    """Async main entry point for the application."""
    print("Task Automation Agent initialized. Type 'exit' to quit.")

    # Initialize conversation state
    message_history = None
    current_task = None

    while True:
        # Get user input with appropriate prompt
        if current_task is True:  # We're in the middle of a conversation
            # We're in the middle of a conversation, ask for follow-up information
            user_input = input("\nYour response: ")
        else:
            # Starting a new task
            user_input = input("\nWhat task would you like me to automate? ")

        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        # Check if this is a URL response in a conversation
        is_url_response = user_input.startswith("http") and current_task is True

        # If user enters a new task, reset the conversation
        # Only consider it a new task if it's not a continuation and has substantial content
        if current_task is None or (user_input and len(user_input) > 3 and
                                   not is_url_response and
                                   not current_task):
            message_history = None
            current_task = user_input

        try:
            # Process the user input with the current conversation state
            result = await process_user_input(user_input, message_history)

            # Update the conversation state for the next interaction
            message_history = result.message_history

            print(f"\nTask: {result.task}")
            print(f"Success: {result.success}")

            # Extract the actual text content from the AgentRunResult object
            summary_text = result.summary
            if isinstance(summary_text, str) and 'AgentRunResult' in summary_text:
                # Extract the output text from the AgentRunResult string
                import re
                # Look for the pattern output='...' or output="..."
                match = re.search(r"output=['\"](.*?)['\"](\))?$", summary_text, re.DOTALL)
                if match:
                    # Get the captured text
                    extracted_text = match.group(1)
                    # Unescape any escaped characters
                    summary_text = extracted_text.replace("\\'", "'").replace('\\n', '\n').replace('\\"', '"')
                else:
                    # If regex fails, try a simpler approach
                    start_idx = summary_text.find("output='") + 8
                    if start_idx > 8:  # Found 'output='
                        end_idx = summary_text.rfind("')")
                        if end_idx > start_idx:
                            summary_text = summary_text[start_idx:end_idx].replace("\\'", "'").replace('\\n', '\n').replace('\\"', '"')

            print(f"Summary: {summary_text}")

            # Check if the response contains a question or request for more information
            has_followup = False

            if result.success and summary_text:
                # Check for common patterns that indicate a follow-up question
                followup_indicators = [
                    '?', 'Could you', 'Please provide', 'Can you', 'I need',
                    'What is', 'Which', 'When', 'Where', 'How', 'Who',
                    'following information', 'need to know', 'target price',
                    'details', 'provide', 'once I have', 'once you have'
                ]

                for indicator in followup_indicators:
                    if indicator in summary_text:
                        has_followup = True
                        break

            # If there's a follow-up question, we're in a conversation
            if has_followup:
                # Set current_task to True to indicate we're in a conversation
                current_task = True
                # No need to prompt for Enter, we'll directly ask for their response in the next loop
            else:
                # If no follow-up, we've completed this task
                current_task = None
                message_history = None

            # Debug output
            print(f"Conversation state: {'Active' if current_task is True else 'Inactive'}")
            print(f"Has followup: {has_followup}")

        except Exception as e:
            print(f"Error: {str(e)}")
            # Reset conversation on error
            message_history = None
            current_task = None

def main():
    """Main entry point for the application."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
