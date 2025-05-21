#!/bin/bash
# Script to run the full Digi-Persona application (frontend and backend) in Docker

# Set environment variables for development
export APP_ENV=development
export DEBUG=True
export RELOAD_FLAG="--reload"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please create one based on .env.example"
    exit 1
fi

# Start Docker containers
echo "Starting Digi-Persona application (frontend and backend)..."
docker-compose up "$@"

# Usage instructions
echo ""
echo "Frontend available at: http://localhost:5173"
echo "Backend API available at: http://localhost:8000"
echo "API Documentation available at: http://localhost:8000/api/v1/docs"
