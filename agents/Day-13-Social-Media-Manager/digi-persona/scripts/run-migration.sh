#!/bin/bash
# Script to run Alembic database migrations

# Check if we're running in Docker or locally
if [ -f /.dockerenv ]; then
    echo "Running migrations in Docker environment..."
    # We are in Docker, migrations are run directly
    alembic upgrade head
else
    echo "Running migrations via Docker..."
    # We are on the host, use Docker to run migrations
    docker-compose exec app alembic upgrade head
fi

# Check if the migration was successful
if [ $? -eq 0 ]; then
    echo "Migration completed successfully!"
else
    echo "Migration failed! Check logs for errors."
    exit 1
fi
