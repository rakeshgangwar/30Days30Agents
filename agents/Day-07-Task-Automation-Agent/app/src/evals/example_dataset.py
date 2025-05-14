"""
Task Automation Agent - Example Dataset

This module provides a simple example dataset for testing the evaluation framework.
"""

from pathlib import Path

from pydantic_evals import Case, Dataset

from src.evals.models import TaskInput, TaskOutput, TaskMetadata

def create_example_dataset() -> Dataset[TaskInput, TaskOutput, TaskMetadata]:
    """
    Create a simple example dataset for testing.
    
    Returns:
        A dataset with a few example cases
    """
    # Create test cases
    cases = [
        Case(
            name="list_files",
            inputs=TaskInput(
                task_description="List all files in the current directory"
            ),
            expected_output=TaskOutput(
                success=True,
                result="Successfully listed files in the current directory",
                steps_taken=["List files in current directory"]
            ),
            metadata=TaskMetadata(
                category="file_operation",
                difficulty="easy",
                expected_tools=["list_files"],
                timeout_seconds=5
            )
        ),
        Case(
            name="read_file",
            inputs=TaskInput(
                task_description="Read the contents of the README.md file"
            ),
            expected_output=TaskOutput(
                success=True,
                result="Successfully read the contents of README.md",
                steps_taken=["Read file README.md"]
            ),
            metadata=TaskMetadata(
                category="file_operation",
                difficulty="easy",
                expected_tools=["read_file"],
                timeout_seconds=5
            )
        ),
        Case(
            name="make_api_request",
            inputs=TaskInput(
                task_description="Make a GET request to https://jsonplaceholder.typicode.com/todos/1"
            ),
            expected_output=TaskOutput(
                success=True,
                result="Successfully made GET request",
                steps_taken=["Make GET request to https://jsonplaceholder.typicode.com/todos/1"]
            ),
            metadata=TaskMetadata(
                category="api_request",
                difficulty="medium",
                expected_tools=["make_get_request"],
                timeout_seconds=10
            )
        ),
        Case(
            name="monitor_website",
            inputs=TaskInput(
                task_description="Set up monitoring for the website https://example.com to check for changes to the title"
            ),
            expected_output=TaskOutput(
                success=True,
                result="Successfully set up website monitoring",
                steps_taken=["Set up web monitor for https://example.com"]
            ),
            metadata=TaskMetadata(
                category="web_monitoring",
                difficulty="hard",
                expected_tools=["setup_web_monitor"],
                timeout_seconds=15
            )
        )
    ]
    
    # Create the dataset
    dataset = Dataset[TaskInput, TaskOutput, TaskMetadata](cases=cases)
    
    return dataset

def save_example_dataset(output_path: Path = Path("example_dataset.yaml")) -> None:
    """
    Create and save an example dataset.
    
    Args:
        output_path: Path to save the dataset to
    """
    dataset = create_example_dataset()
    dataset.to_file(output_path)
    print(f"Example dataset saved to {output_path}")

if __name__ == "__main__":
    save_example_dataset()
