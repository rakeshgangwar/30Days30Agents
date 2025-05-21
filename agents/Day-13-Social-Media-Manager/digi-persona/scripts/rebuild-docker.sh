#!/bin/bash
# Script to rebuild and restart Docker containers after configuration changes

# Set environment variables for development
export APP_ENV=development
export DEBUG=True
export RELOAD_FLAG="--reload"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Creating one based on .env.example"
    cp .env.example .env
    echo "Created .env file. Please update the values as needed."
fi

echo "Stopping existing containers..."
docker-compose down

echo "Rebuilding containers..."
docker-compose build frontend

echo "Starting containers..."
docker-compose up -d

echo ""
echo "Containers rebuilt and started!"
echo "Frontend available at: http://localhost:5173"
echo "Backend API available at: http://localhost:8000"
echo "API Documentation available at: http://localhost:8000/api/v1/docs"
echo ""
echo "To view logs, run: docker-compose logs -f"
