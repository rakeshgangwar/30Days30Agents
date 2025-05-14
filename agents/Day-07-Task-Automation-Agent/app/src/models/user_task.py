"""
Task Automation Agent - User Task Models

This module defines the Pydantic models for representing user tasks,
planned steps, and task results.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

class UserTaskInput(BaseModel):
    """
    Represents a user's task request after parsing and parameter collection.
    
    This model is used to structure the user's natural language input into
    a format that can be processed by the agent.
    """
    action: str = Field(
        description="The main action or intent of the task (e.g., 'extract_pdf_table', 'monitor_website')"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters required for the task, with keys as parameter names and values as parameter values"
    )
    missing_parameters: List[str] = Field(
        default_factory=list,
        description="List of parameter names that are required but not yet provided"
    )
    
    def is_complete(self) -> bool:
        """Check if all required parameters have been provided."""
        return len(self.missing_parameters) == 0

class PlannedStep(BaseModel):
    """
    Represents a single step in the execution plan for a task.
    
    Each step specifies a tool to use, an action to perform with that tool,
    and parameters to pass to the tool.
    """
    tool: str = Field(
        description="The name of the tool to use for this step (e.g., 'FileTool', 'ApiTool')"
    )
    action: str = Field(
        description="The specific action to perform with the tool (e.g., 'read_file', 'make_get_request')"
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters to pass to the tool for this action"
    )
    
    def __str__(self) -> str:
        """String representation of the planned step."""
        return f"{self.tool}.{self.action}({', '.join(f'{k}={v}' for k, v in self.params.items())})"

class TaskResult(BaseModel):
    """
    Represents the result of executing a task.
    
    This includes whether the task was successful, the results of each step,
    and a summary of the overall execution.
    """
    task: str = Field(
        description="The action or intent of the task that was executed"
    )
    success: bool = Field(
        description="Whether the task was executed successfully"
    )
    results: List[Any] = Field(
        default_factory=list,
        description="Results from each step of the task execution"
    )
    summary: str = Field(
        description="A human-readable summary of the task execution"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if the task failed"
    )
