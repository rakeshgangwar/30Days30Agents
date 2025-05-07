#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Todoist tools for the Personal Assistant.

This module implements LangChain tools for interacting with the Todoist API
to create, retrieve, update, and complete tasks/reminders.
"""

import logging
import requests
from typing import Dict, Any, Type, Optional, List
from datetime import datetime

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from config import TODOIST_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Todoist API endpoints
TODOIST_API_BASE_URL = "https://api.todoist.com/rest/v2"
TASKS_ENDPOINT = f"{TODOIST_API_BASE_URL}/tasks"

class TodoistTaskInput(BaseModel):
    """Input schema for creating a Todoist task."""
    content: str = Field(description="The content/title of the task")
    due_string: Optional[str] = Field(None, description="Natural language due date (e.g., 'tomorrow at 3pm')")
    priority: Optional[int] = Field(None, description="Priority level (1-4, where 4 is highest)")
    description: Optional[str] = Field(None, description="Detailed description of the task")
    
class TodoistCreateTool(BaseTool):
    """Tool for creating tasks in Todoist."""
    
    name: str = "todoist_create_task"
    description: str = "Useful for creating reminders and tasks with optional due dates and priorities"
    args_schema: Type[BaseModel] = TodoistTaskInput
    api_token: str = None
    headers: Dict[str, str] = None
    
    def __init__(self, api_token: str = TODOIST_API_KEY):
        """
        Initialize the Todoist create task tool.
        
        Args:
            api_token (str): Todoist API token
        """
        super().__init__()
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def _run(
        self, 
        content: str, 
        due_string: Optional[str] = None, 
        priority: Optional[int] = None, 
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a task in Todoist.
        
        Args:
            content (str): The content/title of the task
            due_string (Optional[str]): Natural language due date
            priority (Optional[int]): Priority level (1-4)
            description (Optional[str]): Detailed description
            
        Returns:
            Dict[str, Any]: Result of the task creation
        """
        try:
            # Validate input
            if priority is not None and not (1 <= priority <= 4):
                return {
                    "error": True,
                    "message": "Priority must be between 1 and 4"
                }
            
            # Prepare request data
            data = {
                "content": content
            }
            
            if due_string:
                data["due_string"] = due_string
            
            if priority:
                data["priority"] = priority
            
            if description:
                data["description"] = description
            
            # Make API request
            logger.info(f"Creating Todoist task: {content}")
            response = requests.post(TASKS_ENDPOINT, headers=self.headers, json=data)
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"Todoist API error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return {
                    "error": True,
                    "message": "Failed to create task",
                    "status_code": response.status_code,
                    "details": response.text
                }
            
            # Parse response
            task_data = response.json()
            
            # Format result
            result = {
                "error": False,
                "task_id": task_data.get("id"),
                "content": task_data.get("content"),
                "url": task_data.get("url"),
                "message": f"Successfully created task: {content}"
            }
            
            # Add due date info if present
            if "due" in task_data and task_data["due"]:
                result["due"] = {
                    "string": task_data["due"].get("string"),
                    "date": task_data["due"].get("date")
                }
            
            logger.info(f"Successfully created Todoist task: {content}")
            return result
            
        except Exception as e:
            logger.error(f"Error in TodoistCreateTool: {str(e)}")
            return {
                "error": True,
                "message": f"Error creating task: {str(e)}"
            }

class TodoistListInput(BaseModel):
    """Input schema for listing Todoist tasks."""
    filter: Optional[str] = Field(None, description="Filter query (e.g., 'today', 'overdue')")
    limit: int = Field(default=5, description="Maximum number of tasks to return")

class TodoistListTool(BaseTool):
    """Tool for listing tasks from Todoist."""
    
    name: str = "todoist_list_tasks"
    description: str = "Useful for retrieving upcoming or filtered tasks/reminders"
    args_schema: Type[BaseModel] = TodoistListInput
    api_token: str = None
    headers: Dict[str, str] = None
    
    def __init__(self, api_token: str = TODOIST_API_KEY):
        """
        Initialize the Todoist list tasks tool.
        
        Args:
            api_token (str): Todoist API token
        """
        super().__init__()
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
    
    def _run(self, filter: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
        """
        List tasks from Todoist.
        
        Args:
            filter (Optional[str]): Filter query
            limit (int): Maximum number of tasks to return
            
        Returns:
            Dict[str, Any]: List of tasks
        """
        try:
            # Prepare request parameters
            params = {}
            if filter:
                params["filter"] = filter
            
            # Make API request
            logger.info(f"Listing Todoist tasks with filter: {filter}")
            response = requests.get(TASKS_ENDPOINT, headers=self.headers, params=params)
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"Todoist API error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return {
                    "error": True,
                    "message": "Failed to list tasks",
                    "status_code": response.status_code
                }
            
            # Parse response
            tasks = response.json()
            
            # Limit number of tasks
            tasks = tasks[:min(limit, len(tasks))]
            
            # Format results
            formatted_tasks = []
            for task in tasks:
                formatted_task = {
                    "id": task.get("id"),
                    "content": task.get("content"),
                    "url": task.get("url"),
                    "priority": task.get("priority")
                }
                
                # Add due date info if present
                if "due" in task and task["due"]:
                    formatted_task["due"] = {
                        "string": task["due"].get("string"),
                        "date": task["due"].get("date")
                    }
                
                formatted_tasks.append(formatted_task)
            
            logger.info(f"Successfully listed {len(formatted_tasks)} Todoist tasks")
            return {
                "error": False,
                "tasks": formatted_tasks,
                "count": len(formatted_tasks),
                "filter": filter
            }
            
        except Exception as e:
            logger.error(f"Error in TodoistListTool: {str(e)}")
            return {
                "error": True,
                "message": f"Error listing tasks: {str(e)}"
            }

class TodoistCompleteInput(BaseModel):
    """Input schema for completing a Todoist task."""
    task_id: str = Field(description="The ID of the task to complete")

class TodoistCompleteTool(BaseTool):
    """Tool for completing tasks in Todoist."""
    
    name: str = "todoist_complete_task"
    description: str = "Useful for marking tasks or reminders as completed"
    args_schema: Type[BaseModel] = TodoistCompleteInput
    api_token: str = None
    headers: Dict[str, str] = None
    
    def __init__(self, api_token: str = TODOIST_API_KEY):
        """
        Initialize the Todoist complete task tool.
        
        Args:
            api_token (str): Todoist API token
        """
        super().__init__()
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
    
    def _run(self, task_id: str) -> Dict[str, Any]:
        """
        Complete a task in Todoist.
        
        Args:
            task_id (str): The ID of the task to complete
            
        Returns:
            Dict[str, Any]: Result of the task completion
        """
        try:
            # Make API request
            endpoint = f"{TASKS_ENDPOINT}/{task_id}/close"
            logger.info(f"Completing Todoist task with ID: {task_id}")
            response = requests.post(endpoint, headers=self.headers)
            
            # Check for errors
            if response.status_code != 204:
                error_msg = f"Todoist API error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return {
                    "error": True,
                    "message": "Failed to complete task",
                    "status_code": response.status_code
                }
            
            logger.info(f"Successfully completed Todoist task with ID: {task_id}")
            return {
                "error": False,
                "task_id": task_id,
                "message": "Task completed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error in TodoistCompleteTool: {str(e)}")
            return {
                "error": True,
                "message": f"Error completing task: {str(e)}"
            }