#!/bin/bash
# Run script for Digi-Persona

# Default values
HOST="0.0.0.0"
PORT="8000"
RELOAD="--reload"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --host=*)
      HOST="${1#*=}"
      shift
      ;;
    --port=*)
      PORT="${1#*=}"
      shift
      ;;
    --no-reload)
      RELOAD=""
      shift
      ;;
    --help)
      echo "Usage: $0 [--host=HOST] [--port=PORT] [--no-reload] [--help]"
      echo ""
      echo "Options:"
      echo "  --host=HOST     Specify the host to bind to (default: 0.0.0.0)"
      echo "  --port=PORT     Specify the port to bind to (default: 8000)"
      echo "  --no-reload     Disable auto-reload on code changes"
      echo "  --help          Show this help message"
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
uv pip install -q pydantic-settings

# Set environment variables if .env file exists
if [ -f ".env" ]; then
    echo "Loading environment variables from .env file"
    export $(grep -v '^#' .env | xargs)
fi

# Run the application
echo "Starting Digi-Persona API server on $HOST:$PORT"
uvicorn app.main:app --host $HOST --port $PORT $RELOAD
