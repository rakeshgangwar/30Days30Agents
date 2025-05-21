#!/bin/bash
# Script to run Docker in development mode

# Set environment variables for development
export APP_ENV=development
export DEBUG=True
export RELOAD_FLAG="--reload"

# Start Docker containers
docker-compose up "$@"
