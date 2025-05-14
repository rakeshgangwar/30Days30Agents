"""
Task Automation Agent - Dependencies

This module defines the dependencies used by the Task Automation Agent.
"""

from dataclasses import dataclass
import os
import requests
from typing import Optional

@dataclass
class AppDependencies:
    """
    Dependencies for the Task Automation Agent.
    
    This class holds all the dependencies needed by the agent, such as API keys,
    HTTP clients, and other services.
    """
    api_key: str
    mcp_server_url: str
    
    @classmethod
    def from_env(cls) -> 'AppDependencies':
        """
        Create an AppDependencies instance from environment variables.
        
        Returns:
            AppDependencies: An instance with values from environment variables
        """
        return cls(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            mcp_server_url=os.getenv("MCP_SERVER_URL", "http://localhost:8000"),
        )
    
    def get_mcp_headers(self) -> dict:
        """
        Get headers for MCP server requests.
        
        Returns:
            dict: Headers for MCP server requests
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
