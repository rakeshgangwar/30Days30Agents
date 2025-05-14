"""
Task Automation Agent - Beehive Control Tool

This module provides a tool for controlling Beehive via the MCP server.
"""

import json
import os
from typing import Dict, Any, List, Optional
import requests
from pydantic_ai.tools import Tool

class BeehiveControlTool(Tool):
    """
    Tool for controlling Beehive via the MCP server.
    
    This tool provides methods for interacting with Beehive, including
    setting up tasks, triggering tasks, and getting task status.
    """
    
    name = "BeehiveControlTool"
    description = "Tool for controlling Beehive via the MCP server."
    
    def __init__(self):
        """Initialize the BeehiveControlTool with the MCP server URL."""
        self.mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")
    
    def list_hives(self) -> str:
        """
        List available Hives in Beehive.
        
        Returns:
            List of available Hives as a JSON string
        """
        try:
            response = requests.get(f"{self.mcp_url}/hives")
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            return f"Error listing Hives: {str(e)}"
    
    def list_bees(self) -> str:
        """
        List configured Bees in Beehive.
        
        Returns:
            List of configured Bees as a JSON string
        """
        try:
            response = requests.get(f"{self.mcp_url}/bees")
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            return f"Error listing Bees: {str(e)}"
    
    def setup_web_monitor(self, url: str, css_selector_price: str, 
                          target_value: float, condition: str,
                          callback_action: str, callback_params: Dict[str, Any]) -> str:
        """
        Set up a web monitoring task in Beehive.
        
        Args:
            url: The URL to monitor
            css_selector_price: CSS selector for the price element
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
                    "css_selector": css_selector_price,
                    "target_value": target_value,
                    "condition": condition,
                    "callback": {
                        "action": callback_action,
                        "params": callback_params
                    }
                }
            }
            
            response = requests.post(f"{self.mcp_url}/tasks", json=data)
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            return f"Error setting up web monitor: {str(e)}"
    
    def setup_scheduled_task(self, schedule: str, task_type: str, 
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
            
            response = requests.post(f"{self.mcp_url}/scheduled-tasks", json=data)
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            return f"Error setting up scheduled task: {str(e)}"
    
    def get_task_status(self, task_id: str) -> str:
        """
        Get the status of a task in Beehive.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Task status as a JSON string
        """
        try:
            response = requests.get(f"{self.mcp_url}/tasks/{task_id}")
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            return f"Error getting task status: {str(e)}"
    
    def trigger_task(self, task_id: str) -> str:
        """
        Trigger a task in Beehive.
        
        Args:
            task_id: ID of the task to trigger
            
        Returns:
            Success message or error
        """
        try:
            response = requests.post(f"{self.mcp_url}/tasks/{task_id}/trigger")
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except Exception as e:
            return f"Error triggering task: {str(e)}"
