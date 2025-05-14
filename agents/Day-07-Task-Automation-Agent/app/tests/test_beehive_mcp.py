"""
Task Automation Agent - Beehive MCP Integration Test

This script tests the integration with the Beehive MCP server.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.beehive.mcp_server import BeehiveMCPServer
from src.models.dependencies import AppDependencies
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

async def test_beehive_mcp_server():
    """Test the Beehive MCP server integration."""
    print("Testing Beehive MCP server integration...")
    
    # Create a test agent
    agent = Agent(
        "openai:gpt-4",
        output_type=str,
        system_prompt="You are a test agent for the Beehive MCP server integration."
    )
    
    # Get the Beehive MCP server configuration
    beehive_config = BeehiveMCPServer.get_default_config()
    
    # Create the Beehive MCP server
    beehive_server = BeehiveMCPServer.create_server(beehive_config)
    
    # Register the MCP server with the agent
    BeehiveMCPServer.register_server_with_agent(agent, beehive_server)
    
    # Create dependencies
    deps = AppDependencies.from_env()
    
    # Test the MCP server
    try:
        print("Starting MCP server...")
        async with agent.run_mcp_servers():
            print("MCP server started successfully!")
            
            # Test a simple query
            print("Testing a simple query...")
            result = await agent.run(
                "What is the current time?",
                deps=deps
            )
            print(f"Agent response: {result.output}")
            
            print("MCP server integration test passed!")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("MCP server integration test failed!")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_beehive_mcp_server())
    sys.exit(0 if success else 1)
