"""
Task Automation Agent - Run Evaluations

This script runs evaluations on the Task Automation Agent using the Pydantic Evals framework.
"""

import os
import asyncio
import argparse
from pathlib import Path
from typing import Optional, List

import logfire
from pydantic_evals import Dataset
from pydantic_evals.evaluators import IsInstance, LLMJudge

from src.models.user_task import TaskResult
from src.main import process_user_input
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

# Configure logfire for OpenTelemetry tracing
logfire.configure(
    send_to_logfire='if-token-present',
    environment='development',
    service_name='task-automation-agent-evals'
)
logfire.instrument_pydantic_ai()

async def task_automation_function(task_input: TaskInput) -> TaskOutput:
    """
    Function that processes a task using the Task Automation Agent.

    This is the function that will be evaluated by the Pydantic Evals framework.

    Args:
        task_input: The input for the task

    Returns:
        The output of the task
    """
    try:
        # Process the task using the Task Automation Agent
        with logfire.span('task_automation'):
            result = await process_user_input(task_input.task_description)

        # Convert the result to the expected output format
        output = TaskOutput(
            success=result.success,
            result=result.summary,
            steps_taken=[str(r) for r in result.results]
        )

        return output
    except Exception as e:
        # Return a failed result if an exception occurs
        return TaskOutput(
            success=False,
            result=f"Error: {str(e)}",
            steps_taken=[]
        )

async def load_or_generate_dataset(
    dataset_path: Optional[Path] = None,
    dataset_type: str = "general",
    n_examples: int = 5
) -> Dataset[TaskInput, TaskOutput, TaskMetadata]:
    """
    Load a dataset from a file or generate a new one.

    Args:
        dataset_path: Path to the dataset file
        dataset_type: Type of dataset to generate if no file is provided
        n_examples: Number of examples to generate

    Returns:
        The loaded or generated dataset
    """
    if dataset_path and dataset_path.exists():
        # Load the dataset from the file
        return Dataset[TaskInput, TaskOutput, TaskMetadata].from_file(dataset_path)

    # Generate a new dataset
    if dataset_type == "file_operations":
        return await generate_file_operations_dataset(n_examples=n_examples)
    elif dataset_type == "api_requests":
        return await generate_api_requests_dataset(n_examples=n_examples)
    elif dataset_type == "web_monitoring":
        return await generate_web_monitoring_dataset(n_examples=n_examples)
    else:
        return await generate_task_dataset(n_examples=n_examples)

async def run_evaluation(
    dataset_path: Optional[Path] = None,
    dataset_type: str = "general",
    n_examples: int = 5,
    output_path: Optional[Path] = None,
    max_concurrency: Optional[int] = None
) -> None:
    """
    Run an evaluation on the Task Automation Agent.

    Args:
        dataset_path: Path to the dataset file
        dataset_type: Type of dataset to generate if no file is provided
        n_examples: Number of examples to generate
        output_path: Path to save the evaluation report
        max_concurrency: Maximum number of concurrent evaluations
    """
    # Load or generate the dataset
    dataset = await load_or_generate_dataset(
        dataset_path=dataset_path,
        dataset_type=dataset_type,
        n_examples=n_examples
    )

    # Add evaluators to the dataset
    dataset.add_evaluator(IsInstance(type_name='TaskOutput'))
    dataset.add_evaluator(SuccessEvaluator())
    dataset.add_evaluator(ToolUsageEvaluator())
    dataset.add_evaluator(PerformanceEvaluator())
    dataset.add_evaluator(LLMResultEvaluator())

    # Run the evaluation
    print(f"Running evaluation on {len(dataset.cases)} cases...")
    report = await dataset.evaluate(
        task_automation_function,
        max_concurrency=max_concurrency
    )

    # Print the report
    report.print(
        include_input=True,
        include_output=True,
        include_durations=True
    )

    # Save the report if an output path is provided
    if output_path:
        # Convert the report to a dictionary and save it as YAML
        import yaml
        with open(output_path, 'w') as f:
            yaml.dump(report.model_dump(), f)
        print(f"Evaluation report saved to {output_path}")

def main():
    """Main entry point for the evaluation script."""
    parser = argparse.ArgumentParser(description="Run evaluations on the Task Automation Agent")
    parser.add_argument(
        "--dataset",
        type=str,
        help="Path to the dataset file"
    )
    parser.add_argument(
        "--type",
        type=str,
        default="general",
        choices=["general", "file_operations", "api_requests", "web_monitoring"],
        help="Type of dataset to generate if no file is provided"
    )
    parser.add_argument(
        "--examples",
        type=int,
        default=5,
        help="Number of examples to generate"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Path to save the evaluation report"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        help="Maximum number of concurrent evaluations"
    )

    args = parser.parse_args()

    # Convert string paths to Path objects
    dataset_path = Path(args.dataset) if args.dataset else None
    output_path = Path(args.output) if args.output else None

    # Run the evaluation
    asyncio.run(run_evaluation(
        dataset_path=dataset_path,
        dataset_type=args.type,
        n_examples=args.examples,
        output_path=output_path,
        max_concurrency=args.concurrency
    ))

if __name__ == "__main__":
    main()
