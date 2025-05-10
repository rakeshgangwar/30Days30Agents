# Docker Setup for Writing Assistant API

This document provides instructions for running the Writing Assistant API using Docker.

> **Note**: While the local development environment uses `uv` for package management, the Docker container uses `pip` directly to avoid virtual environment complexities in the containerized environment.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Getting Started

### 1. Environment Setup

Create a `.env` file in the `app` directory based on the provided `.env.example`:

```bash
cd app
cp .env.example .env
```

Edit the `.env` file to set your configuration values, especially:
- `SECRET_KEY`: A secure random string for JWT encryption
- `API_KEY`: Your API key for authentication
- `OPENROUTER_API_KEY`: Your OpenRouter API key for LLM access

### 2. Building and Starting the Service

From the project root directory (where the `docker-compose.yml` file is located), run:

```bash
docker-compose up --build
```

This will:
- Build the Docker image for the API
- Start the service on port 8000
- Mount the app directory as a volume for development

### 3. Accessing the API

Once the service is running, you can access:

- API documentation: http://localhost:8000/docs
- Health check endpoint: http://localhost:8000/health

### 4. Running in Production

For production deployment, consider:

1. Setting `DEBUG=false` in your `.env` file
2. Using a more robust database like PostgreSQL
3. Setting up proper logging
4. Using a reverse proxy like Nginx

To run in detached mode:

```bash
docker-compose up -d
```

### 5. Stopping the Service

To stop the service:

```bash
docker-compose down
```

## Docker Commands Reference

- Build the image: `docker-compose build`
- Start the service: `docker-compose up`
- Start in detached mode: `docker-compose up -d`
- Stop the service: `docker-compose down`
- View logs: `docker-compose logs -f`
- Execute commands in the container: `docker-compose exec api <command>`
- Run tests: `docker-compose exec api python -m pytest`
