"""
Task Automation Agent - Evaluation Models

This module defines the models used for evaluating the Task Automation Agent.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class TaskInput(BaseModel):
    """
    Input for a task automation evaluation.
    
    This model represents the input for a task that the agent should automate.
    """
    task_description: str = Field(
        description="Natural language description of the task to automate"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional context information for the task"
    )

class TaskOutput(BaseModel):
    """
    Expected output for a task automation evaluation.
    
    This model represents the expected output from the agent after automating a task.
    """
    success: bool = Field(
        description="Whether the task was completed successfully"
    )
    result: str = Field(
        description="The result of the task execution"
    )
    steps_taken: List[str] = Field(
        default_factory=list,
        description="List of steps taken to complete the task"
    )

class TaskMetadata(BaseModel):
    """
    Metadata for a task automation evaluation.
    
    This model represents additional metadata about the task being evaluated.
    """
    category: str = Field(
        description="Category of the task (e.g., 'file_operation', 'api_request', 'scheduling')"
    )
    difficulty: str = Field(
        description="Difficulty level of the task (e.g., 'easy', 'medium', 'hard')"
    )
    expected_tools: List[str] = Field(
        default_factory=list,
        description="List of tools that are expected to be used for this task"
    )
    timeout_seconds: int = Field(
        default=60,
        description="Maximum time in seconds that the task should take to complete"
    )
