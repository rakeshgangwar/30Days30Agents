#!/bin/bash
# Script to run Docker in production mode

# Set environment variables for production
export APP_ENV=production
export DEBUG=False
export RELOAD_FLAG=""  # Empty string means no reload flag

# Start Docker containers
docker-compose up "$@"
