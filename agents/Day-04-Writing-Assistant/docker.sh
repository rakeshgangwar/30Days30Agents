#!/bin/bash
# Helper script for Docker operations

set -e

# Function to display help message
show_help() {
    echo "Usage: ./docker.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build       Build the Docker image"
    echo "  start       Start the Docker container"
    echo "  stop        Stop the Docker container"
    echo "  restart     Restart the Docker container"
    echo "  logs        Show container logs"
    echo "  test        Run tests in the container"
    echo "  shell       Open a shell in the container"
    echo "  help        Show this help message"
    echo ""
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed or not in PATH"
    exit 1
fi

# Process commands
case "$1" in
    build)
        echo "Building Docker image..."
        docker-compose build
        ;;
    start)
        echo "Starting Docker container..."
        docker-compose up -d
        echo "Container started. API available at http://localhost:8000"
        ;;
    stop)
        echo "Stopping Docker container..."
        docker-compose down
        ;;
    restart)
        echo "Restarting Docker container..."
        docker-compose down
        docker-compose up -d
        echo "Container restarted. API available at http://localhost:8000"
        ;;
    logs)
        echo "Showing container logs (press Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
    test)
        echo "Running tests in container..."
        docker-compose exec api python run_tests.py "$2"
        ;;
    shell)
        echo "Opening shell in container..."
        docker-compose exec api /bin/bash
        ;;
    help|*)
        show_help
        ;;
esac
