#!/usr/bin/env python
"""
Generate an example dataset for evaluating the Task Automation Agent.

This script creates and saves an example dataset with predefined test cases.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.evals.example_dataset import save_example_dataset

def main():
    """Generate and save the example dataset."""
    output_dir = Path("data/evals")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "example_dataset.yaml"
    save_example_dataset(output_path)

if __name__ == "__main__":
    main()
