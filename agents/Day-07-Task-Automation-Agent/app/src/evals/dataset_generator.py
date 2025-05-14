"""
Task Automation Agent - Dataset Generator

This module provides functions to generate evaluation datasets for the Task Automation Agent.
"""

import asyncio
from pathlib import Path
from typing import Optional

from pydantic_evals import Dataset
from pydantic_evals.generation import generate_dataset

from src.evals.models import TaskInput, TaskOutput, TaskMetadata

async def generate_task_dataset(
    n_examples: int = 5,
    output_file: Optional[Path] = None,
    categories: Optional[list[str]] = None
) -> Dataset[TaskInput, TaskOutput, TaskMetadata]:
    """
    Generate a dataset of task automation examples.
    
    Args:
        n_examples: Number of examples to generate
        output_file: Optional file to save the dataset to
        categories: Optional list of task categories to include
        
    Returns:
        Dataset of task automation examples
    """
    # Default categories if none provided
    if categories is None:
        categories = [
            "file_operation",
            "api_request",
            "scheduling",
            "data_processing",
            "web_monitoring"
        ]
    
    # Generate instructions based on categories
    category_instructions = "\n".join([
        f"- {category}: Tasks related to {category.replace('_', ' ')}" 
        for category in categories
    ])
    
    # Generate the dataset
    dataset = await generate_dataset(
        dataset_type=Dataset[TaskInput, TaskOutput, TaskMetadata],
        n_examples=n_examples,
        extra_instructions=f"""
        Generate a diverse set of task automation examples across different categories.
        
        Categories to include:
        {category_instructions}
        
        For each task:
        1. Provide a clear task description that a task automation agent could understand
        2. Include appropriate context information if needed
        3. Specify the expected tools that would be used for this task
        4. Set an appropriate difficulty level (easy, medium, hard)
        5. Define a reasonable timeout in seconds
        
        Make sure the tasks are realistic and could be automated by an agent with access to:
        - File operations (read, write, list files)
        - API requests (GET, POST, PUT, DELETE)
        - Scheduling capabilities
        - Web monitoring tools
        - Data processing functions
        """,
    )
    
    # Save the dataset if an output file is provided
    if output_file:
        dataset.to_file(output_file)
    
    return dataset

async def generate_file_operations_dataset(
    n_examples: int = 3,
    output_file: Optional[Path] = None
) -> Dataset[TaskInput, TaskOutput, TaskMetadata]:
    """
    Generate a dataset specifically for file operation tasks.
    
    Args:
        n_examples: Number of examples to generate
        output_file: Optional file to save the dataset to
        
    Returns:
        Dataset of file operation task examples
    """
    return await generate_task_dataset(
        n_examples=n_examples,
        output_file=output_file,
        categories=["file_operation"]
    )

async def generate_api_requests_dataset(
    n_examples: int = 3,
    output_file: Optional[Path] = None
) -> Dataset[TaskInput, TaskOutput, TaskMetadata]:
    """
    Generate a dataset specifically for API request tasks.
    
    Args:
        n_examples: Number of examples to generate
        output_file: Optional file to save the dataset to
        
    Returns:
        Dataset of API request task examples
    """
    return await generate_task_dataset(
        n_examples=n_examples,
        output_file=output_file,
        categories=["api_request"]
    )

async def generate_web_monitoring_dataset(
    n_examples: int = 3,
    output_file: Optional[Path] = None
) -> Dataset[TaskInput, TaskOutput, TaskMetadata]:
    """
    Generate a dataset specifically for web monitoring tasks.
    
    Args:
        n_examples: Number of examples to generate
        output_file: Optional file to save the dataset to
        
    Returns:
        Dataset of web monitoring task examples
    """
    return await generate_task_dataset(
        n_examples=n_examples,
        output_file=output_file,
        categories=["web_monitoring"]
    )

if __name__ == "__main__":
    # Generate and save a general dataset
    asyncio.run(generate_task_dataset(
        n_examples=10,
        output_file=Path("task_automation_dataset.yaml")
    ))
    
    # Generate and save category-specific datasets
    asyncio.run(generate_file_operations_dataset(
        output_file=Path("file_operations_dataset.yaml")
    ))
    
    asyncio.run(generate_api_requests_dataset(
        output_file=Path("api_requests_dataset.yaml")
    ))
    
    asyncio.run(generate_web_monitoring_dataset(
        output_file=Path("web_monitoring_dataset.yaml")
    ))
