"""
Task Automation Agent - Beehive MCP Example

This example demonstrates how to use the Task Automation Agent with the Beehive MCP server.
"""

import os
import sys
import asyncio
import json

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.dependencies import AppDependencies
from src.beehive.mcp_server import BeehiveMCPServer
from src.main import agent

async def main():
    """Run the example."""
    # Create dependencies
    deps = AppDependencies.from_env()

    # Get the Beehive MCP server configuration from the environment
    beehive_config = BeehiveMCPServer.get_default_config()

    # Create the Beehive MCP server
    beehive_server = BeehiveMCPServer.create_server(beehive_config)

    # Register the MCP server with the agent
    BeehiveMCPServer.register_server_with_agent(agent, beehive_server)

    # Example task: Set up a web monitor
    print("Setting up a web monitor task using Beehive MCP server...")

    try:
        # Run the agent with the MCP server
        async with agent.run_mcp_servers():
            result = await agent.run(
                "Monitor the website 'https://example.com' for changes to the title element. "
                "When it changes, send me an email at 'user@example.com'.",
                deps=deps
            )
            print(f"Agent response: {result.output}")
    except Exception as e:
        print(f"Error: {str(e)}")

    # Example task: Set up a scheduled task
    print("\nSetting up a scheduled task using Beehive MCP server...")

    try:
        # Run the agent with the MCP server
        async with agent.run_mcp_servers():
            result = await agent.run(
                "Every morning at 8 AM, check the weather forecast for New York "
                "and send it to my email at 'user@example.com'.",
                deps=deps
            )
            print(f"Agent response: {result.output}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
