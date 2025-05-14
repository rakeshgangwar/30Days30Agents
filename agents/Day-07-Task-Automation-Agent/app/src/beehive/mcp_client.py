"""
Task Automation Agent - MCP Client

This module provides a client for interacting with the MCP server,
which serves as a bridge between the PydanticAI agent and Beehive.
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional

class MCPClient:
    """
    Client for interacting with the MCP server.
    
    The MCP server is a bridge between the PydanticAI agent and Beehive,
    allowing the agent to control and query Beehive.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCP server (default: from environment variable)
        """
        self.base_url = base_url or os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    
    def get_hives(self) -> Dict[str, Any]:
        """
        Get a list of available Hives.
        
        Returns:
            Dictionary containing Hive information
        """
        response = requests.get(f"{self.base_url}/hives")
        response.raise_for_status()
        return response.json()
    
    def get_bees(self) -> Dict[str, Any]:
        """
        Get a list of configured Bees.
        
        Returns:
            Dictionary containing Bee information
        """
        response = requests.get(f"{self.base_url}/bees")
        response.raise_for_status()
        return response.json()
    
    def create_task(self, task_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new task in Beehive.
        
        Args:
            task_type: Type of task to create
            config: Configuration for the task
            
        Returns:
            Dictionary containing the created task information
        """
        data = {
            "task_type": task_type,
            "config": config
        }
        
        response = requests.post(f"{self.base_url}/tasks", json=data)
        response.raise_for_status()
        return response.json()
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Get information about a task.
        
        Args:
            task_id: ID of the task to get
            
        Returns:
            Dictionary containing task information
        """
        response = requests.get(f"{self.base_url}/tasks/{task_id}")
        response.raise_for_status()
        return response.json()
    
    def trigger_task(self, task_id: str) -> Dict[str, Any]:
        """
        Trigger a task.
        
        Args:
            task_id: ID of the task to trigger
            
        Returns:
            Dictionary containing the result of triggering the task
        """
        response = requests.post(f"{self.base_url}/tasks/{task_id}/trigger")
        response.raise_for_status()
        return response.json()
    
    def create_scheduled_task(self, schedule: str, task_type: str, 
                              params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a scheduled task.
        
        Args:
            schedule: Cron expression for the schedule
            task_type: Type of task to schedule
            params: Parameters for the task
            
        Returns:
            Dictionary containing the created scheduled task information
        """
        data = {
            "schedule": schedule,
            "task_type": task_type,
            "params": params
        }
        
        response = requests.post(f"{self.base_url}/scheduled-tasks", json=data)
        response.raise_for_status()
        return response.json()
