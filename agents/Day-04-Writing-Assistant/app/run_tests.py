#!/usr/bin/env python
"""
Script to run tests for the Writing Assistant application.

This script makes it easy to run the application tests from the project root.
"""
import os
import sys
import pytest
import argparse

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def main():
    """Run the tests with command line arguments."""
    parser = argparse.ArgumentParser(description="Run tests for the Writing Assistant application.")
    parser.add_argument(
        "--test-file",
        help="Specific test file to run (e.g., test_security.py)"
    )
    parser.add_argument(
        "--test-name",
        help="Specific test function to run (e.g., test_generate_api_key)"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )

    args = parser.parse_args()

    # Build the pytest arguments
    pytest_args = []

    # Add verbosity
    if args.verbose:
        pytest_args.append("-v")
    else:
        pytest_args.append("-xvs")

    # Add coverage if requested
    if args.coverage:
        pytest_args.extend(["--cov=app", "--cov-report=term-missing"])

    # Build the test path
    test_path = "tests"
    if args.test_file:
        test_path = os.path.join("tests", args.test_file)

    # Add test name if specified
    if args.test_name:
        test_path = f"{test_path}::{args.test_name}"

    pytest_args.append(test_path)

    print(f"Running tests from {project_root}")
    print(f"Test command: pytest {' '.join(pytest_args)}")

    # Run the tests
    return pytest.main(pytest_args)

if __name__ == "__main__":
    sys.exit(main())