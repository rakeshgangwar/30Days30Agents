# Learning Coach Agent - Backend

This is the backend for the Learning Coach Agent, built with FastAPI, LangChain, and LangGraph.

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
uv install
```

## Development

Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.

API documentation will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Core functionality
│   ├── db/             # Database models and utilities
│   ├── models/         # Pydantic models
│   ├── services/       # Business logic
│   ├── utils/          # Utility functions
│   └── main.py         # Application entry point
├── tests/              # Test suite
└── README.md           # This file
```

## Testing

Run tests:
```bash
pytest
```