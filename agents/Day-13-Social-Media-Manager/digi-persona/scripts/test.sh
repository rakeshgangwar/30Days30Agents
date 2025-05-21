#!/bin/bash
# Test script for Digi-Persona

# Default values
TEST_TYPE="api"
VERBOSE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --unit)
      TEST_TYPE="unit"
      shift
      ;;
    --api)
      TEST_TYPE="api"
      shift
      ;;
    --all)
      TEST_TYPE="all"
      shift
      ;;
    --verbose)
      VERBOSE="-v"
      shift
      ;;
    --help)
      echo "Usage: $0 [--unit|--api|--all] [--verbose] [--help]"
      echo ""
      echo "Options:"
      echo "  --unit         Run unit tests only"
      echo "  --api          Run API integration tests only (default)"
      echo "  --all          Run all tests"
      echo "  --verbose      Show verbose output"
      echo "  --help         Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Running setup first..."
    ./scripts/setup.sh
fi

# Activate the virtual environment
source .venv/bin/activate

# Install any missing dependencies
echo "Checking for missing dependencies..."
uv pip install -q pydantic-settings requests pytest pytest-asyncio httpx

# Set environment variables if .env file exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file"
    export $(grep -v '^#' .env | xargs)
fi

# Make sure the tests directory exists
if [ ! -d "tests" ]; then
    echo "Creating tests directory..."
    mkdir -p tests
    touch tests/__init__.py
fi

# Run the tests based on the selected type
case $TEST_TYPE in
  unit)
    echo "Running unit tests..."
    python -m pytest tests/unit $VERBOSE
    ;;
  api)
    echo "Running API integration tests..."
    python scripts/test_api.py
    ;;
  all)
    echo "Running all tests..."
    python -m pytest tests $VERBOSE
    python scripts/test_api.py
    ;;
  *)
    echo "Unknown test type: $TEST_TYPE"
    exit 1
    ;;
esac
