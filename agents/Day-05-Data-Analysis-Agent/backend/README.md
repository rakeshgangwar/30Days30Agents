# Data Analysis Agent - Backend

This is the FastAPI backend for the Data Analysis Agent, which provides API endpoints for analyzing and visualizing data using natural language queries.

## Features

- CSV file upload and analysis
- SQL database connection and querying
- Natural language query processing using LangChain and OpenRouter
- Data visualization generation with Plotly

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── csv_analysis.py
│   │   └── sql_analysis.py
│   └── services/
│       ├── __init__.py
│       ├── llm_service.py
│       ├── csv_service.py
│       ├── db_service.py
│       └── visualization_service.py
├── .env
├── .env.example
└── requirements.txt
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- uv (Python package manager)

### Installation

1. Create a virtual environment:
   ```bash
   uv venv
   ```

2. Activate the virtual environment:
   ```bash
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and add your OpenRouter API key:
   ```
   OPENROUTER_API_KEY="your_openrouter_api_key_here"
   ```

## Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Health Check

- `GET /`: Check if the API is running

### LLM Test

- `GET /test-llm`: Test the LLM connection

### CSV Analysis

- `POST /csv/upload`: Upload and process a CSV file
- `POST /csv/query`: Execute a natural language query on a CSV file

### SQL Analysis

- `POST /db/connect`: Establish a connection to a database
- `POST /db/query`: Execute a natural language query on a database

## Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `DEFAULT_LLM_MODEL`: Default LLM model to use (default: "anthropic/claude-3.7-sonnet")
- `DEFAULT_TEMPERATURE`: Temperature setting for the LLM (default: 0.2)
- `DEFAULT_MAX_TOKENS`: Maximum tokens for LLM responses (default: 1024)
- `DEFAULT_REQUEST_TIMEOUT`: Timeout for LLM requests in seconds (default: 60)
- `DEFAULT_MAX_RETRIES`: Maximum retries for LLM requests (default: 3)
- `AGENT_MAX_ITERATIONS`: Maximum iterations for agents (default: 10)
- `AGENT_MAX_EXECUTION_TIME`: Maximum execution time for agents in seconds (default: 30)
- `AGENT_EARLY_STOPPING_METHOD`: Method for early stopping (default: "force")
- `AGENT_ALLOW_DANGEROUS_CODE`: Whether to allow potentially dangerous code (default: true)
- `DEFAULT_SQLITE_PATH`: Default path for SQLite databases (default: "test_data.db")
- `DEFAULT_DB_TYPE`: Default database type (default: "sqlite")
- `APP_TITLE`: Application title (default: "Data Analysis Agent")
- `CORS_ORIGINS`: List of allowed CORS origins (default: ["*"])
