#!/bin/bash
# Script to fix Alembic migration state and apply the new migration

# Check if we're running in Docker or locally
if [ -f /.dockerenv ]; then
    echo "Running in Docker environment..."
    # We are in Docker, commands are run directly
    
    # Mark the initial migration as complete without running it
    echo "Marking initial migration as complete..."
    alembic stamp 001
    
    # Apply the new migration
    echo "Applying new migration to add owner_id column..."
    alembic upgrade head
else
    echo "Running via Docker..."
    # We are on the host, use Docker to run commands
    
    # Mark the initial migration as complete without running it
    echo "Marking initial migration as complete..."
    docker-compose exec app alembic stamp 001
    
    # Apply the new migration
    echo "Applying new migration to add owner_id column..."
    docker-compose exec app alembic upgrade head
fi

# Check if the migration was successful
if [ $? -eq 0 ]; then
    echo "Migration completed successfully!"
else
    echo "Migration failed! Check logs for errors."
    exit 1
fi
