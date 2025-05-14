"""
Task Automation Agent - Beehive MCP Server Integration

This module provides integration with the Beehive MCP server using stdio transport.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

class BeehiveMCPServer:
    """
    Integration with Beehive MCP server using stdio transport.

    This class provides methods to create and configure the Beehive MCP server
    for use with the Task Automation Agent.
    """

    @staticmethod
    def create_server(config: Dict[str, Any]) -> MCPServerStdio:
        """
        Create a Beehive MCP server instance based on the provided configuration.

        Args:
            config: Configuration for the Beehive MCP server

        Returns:
            MCPServerStdio: The configured MCP server
        """
        command = config.get("command", "node")
        args = config.get("args", [])
        env = config.get("env", {})

        # Merge with current environment
        full_env = os.environ.copy()
        full_env.update(env)

        # Create the MCP server
        server = MCPServerStdio(
            command=command,
            args=args,
            env=full_env
        )

        return server

    @staticmethod
    def register_server_with_agent(agent: Agent, server: MCPServerStdio) -> Agent:
        """
        Register the Beehive MCP server with the agent.

        Args:
            agent: The PydanticAI agent
            server: The Beehive MCP server

        Returns:
            Agent: The agent with the MCP server registered
        """
        # Register the MCP server with the agent
        agent.mcp_servers = [server]

        return agent

    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """
        Get the default configuration for the Beehive MCP server.

        Returns:
            Dict[str, Any]: The default configuration
        """
        # Get configuration from environment variables
        beehive_url = os.getenv("BEEHIVE_URL", "http://localhost:8181")
        beehive_mcp_server_path = os.getenv(
            "BEEHIVE_MCP_SERVER_PATH",
            "/Users/rakeshgangwar/Projects/beehive-mcp-server/src/beehive-mcp.js"
        )

        # Use the provided configuration that works for other MCP clients
        return {
            "autoApprove": [],
            "disabled": False,
            "timeout": 60,
            "command": "node",
            "args": [beehive_mcp_server_path],
            "env": {
                "BEEHIVE_URL": beehive_url,
                "MCP_SERVER_NAME": "beehive"
            },
            "transportType": "stdio"
        }

    @staticmethod
    def create_from_config_file(config_path: str) -> MCPServerStdio:
        """
        Create a Beehive MCP server from a configuration file.

        Args:
            config_path: Path to the configuration file

        Returns:
            MCPServerStdio: The configured MCP server
        """
        import json

        with open(config_path, 'r') as f:
            config = json.load(f)

        beehive_config = config.get("beehive", {})
        return BeehiveMCPServer.create_server(beehive_config)

    @staticmethod
    async def run_with_agent(agent: Agent, server: MCPServerStdio, user_input: str) -> str:
        """
        Run the agent with the Beehive MCP server.

        Args:
            agent: The PydanticAI agent
            server: The Beehive MCP server
            user_input: The user input to process

        Returns:
            str: The result of processing the user input
        """
        # Register the MCP server with the agent if not already registered
        if not hasattr(agent, 'mcp_servers') or server not in agent.mcp_servers:
            BeehiveMCPServer.register_server_with_agent(agent, server)

        # Run the agent with the MCP server
        async with agent.run_mcp_servers():
            result = await agent.run(user_input)
            return result.output
