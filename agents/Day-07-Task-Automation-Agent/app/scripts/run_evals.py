#!/usr/bin/env python
"""
Run evaluations on the Task Automation Agent.

This script runs evaluations using the Pydantic Evals framework.
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evals.run_evals import run_evaluation

def main():
    """Parse arguments and run the evaluation."""
    parser = argparse.ArgumentParser(description="Run evaluations on the Task Automation Agent")
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/evals/example_dataset.yaml",
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
        default="data/evals/evaluation_report.yaml",
        help="Path to save the evaluation report"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Maximum number of concurrent evaluations"
    )
    
    args = parser.parse_args()
    
    # Convert string paths to Path objects
    dataset_path = Path(args.dataset) if args.dataset else None
    output_path = Path(args.output) if args.output else None
    
    # Create output directory if it doesn't exist
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
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
