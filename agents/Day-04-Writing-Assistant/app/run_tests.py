#!/usr/bin/env python
"""
Script to run tests for the Writing Assistant application.

This script makes it easy to run the application tests from the project root.
"""
import os
import sys
import pytest

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    print(f"Running tests from {project_root}")
    # Run the tests
    pytest.main(["-xvs", "tests"])