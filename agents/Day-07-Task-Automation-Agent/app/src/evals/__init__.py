"""
Task Automation Agent - Evaluations Package

This package provides tools for evaluating the Task Automation Agent.
"""

from src.evals.models import TaskInput, TaskOutput, TaskMetadata
from src.evals.evaluators import (
    SuccessEvaluator,
    ToolUsageEvaluator,
    PerformanceEvaluator,
    LLMResultEvaluator
)
from src.evals.dataset_generator import (
    generate_task_dataset,
    generate_file_operations_dataset,
    generate_api_requests_dataset,
    generate_web_monitoring_dataset
)
from src.evals.example_dataset import create_example_dataset, save_example_dataset

__all__ = [
    "TaskInput",
    "TaskOutput",
    "TaskMetadata",
    "SuccessEvaluator",
    "ToolUsageEvaluator",
    "PerformanceEvaluator",
    "LLMResultEvaluator",
    "generate_task_dataset",
    "generate_file_operations_dataset",
    "generate_api_requests_dataset",
    "generate_web_monitoring_dataset",
    "create_example_dataset",
    "save_example_dataset"
]
