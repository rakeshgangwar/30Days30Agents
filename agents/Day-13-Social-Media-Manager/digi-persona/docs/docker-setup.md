# Docker Setup for Digi-Persona

This document explains how to run the Digi-Persona application using Docker in both development and production environments.

## Overview

The Digi-Persona application is containerized using Docker, which provides a consistent environment for development, testing, and production. The Docker setup includes:

- **Frontend**: React application built with Vite and shadcn/ui
- **FastAPI Application**: The main API service
- **Celery Worker**: For background task processing
- **Celery Beat**: For scheduled tasks
- **PostgreSQL**: For database storage
- **Redis**: For caching and Celery message broker
- **Prometheus**: For metrics collection
- **Grafana**: For metrics visualization

## Prerequisites

- Docker and Docker Compose installed on your system
- Git repository cloned locally

## Configuration

The Docker setup is configured using the following files:

- `docker-compose.yml`: Defines the services, networks, and volumes
- `Dockerfile`: Defines how to build the backend application image
- `frontend/Dockerfile`: Defines how to build the frontend application image
- `.env`: Contains environment variables for the application
- `scripts/dev-docker.sh`: Script to run Docker in development mode (backend only)
- `scripts/prod-docker.sh`: Script to run Docker in production mode (backend only)
- `scripts/run-docker-full.sh`: Script to run the full application (frontend and backend)

## Development Mode

In development mode, the application runs with hot reloading enabled, which automatically restarts the application when code changes are detected. This is useful for rapid development and testing.

### Running in Development Mode

```bash
./scripts/dev-docker.sh
```

To run in detached mode (in the background):

```bash
./scripts/dev-docker.sh -d
```

### Development Mode Features

- Hot reloading enabled (`--reload` flag for Uvicorn)
- Debug mode enabled
- Environment set to "development"
- Volume mounts for live code changes

## Production Mode

In production mode, the application runs without hot reloading for better performance and stability.

### Running in Production Mode

```bash
./scripts/prod-docker.sh
```

To run in detached mode (in the background):

```bash
./scripts/prod-docker.sh -d
```

### Production Mode Features

- Hot reloading disabled
- Debug mode disabled
- Environment set to "production"
- Optimized for performance and stability

## Accessing the Application

Once the containers are running, you can access the application at:

- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Documentation: http://localhost:8000/api/v1/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

## Managing Containers

### Viewing Container Status

```bash
docker-compose ps
```

### Viewing Container Logs

```bash
docker-compose logs
```

To view logs for a specific service:

```bash
docker-compose logs frontend
docker-compose logs app
docker-compose logs worker
docker-compose logs db
```

### Stopping Containers

```bash
docker-compose down
```

### Rebuilding Containers

If you make changes to the Dockerfile or requirements.txt:

```bash
docker-compose build
```

## Database Management

The PostgreSQL database is accessible at:

- Host: localhost
- Port: 5432
- Username: postgres
- Password: postgres
- Database: digi_persona

### Connecting to the Database

```bash
docker-compose exec db psql -U postgres -d digi_persona
```

## Troubleshooting

### Container Won't Start

Check the logs for errors:

```bash
docker-compose logs app
```

### Database Connection Issues

Ensure the database container is running:

```bash
docker-compose ps db
```

Check the database logs:

```bash
docker-compose logs db
```

### Hot Reloading Not Working

Ensure you're running in development mode:

```bash
./scripts/dev-docker.sh
```

Check that the volume mount is working correctly:

```bash
docker-compose exec app ls -la /app
```

## Next Steps

After setting up the Docker environment, you can proceed with:

1. Implementing platform integrations (Twitter, LinkedIn, Bluesky)
2. Setting up scheduled content generation
3. Developing the web interface
