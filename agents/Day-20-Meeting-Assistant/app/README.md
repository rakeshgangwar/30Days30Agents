# Meeting Assistant

AI-powered meeting assistant for virtual and physical meetings with transcription, speaker diarization, and intelligent summarization.

## Features

- **Real-time Transcription**: Live transcription using Whisper ASR
- **Speaker Diarization**: Identify and separate different speakers
- **Intelligent Summarization**: AI-powered meeting summaries and action items
- **Multiple LLM Support**: Works with local (Ollama) and cloud LLMs (OpenRouter)
- **RESTful API**: Clean FastAPI-based REST API
- **Background Processing**: Async processing with Celery
- **Security**: JWT authentication and encryption

## Tech Stack

- **Backend**: FastAPI, Python 3.11+
- **AI/ML**: Whisper, PyAnnote, Transformers
- **Database**: PostgreSQL with SQLAlchemy
- **Queue**: Redis + Celery
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: black, isort, flake8, mypy, pre-commit

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- uv (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd MeetingAssistant
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Install pre-commit hooks:
```bash
uv run pre-commit install
```

5. Run tests:
```bash
uv run pytest
```

6. Start the development server:
```bash
uv run python src/main.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Development

### Project Structure

```
├── src/                 # Source code
├── tests/              # Test files
├── docs/               # Documentation
├── scripts/            # Utility scripts
├── config/             # Configuration files
├── .env.example        # Environment template
├── pyproject.toml      # Project dependencies
└── README.md
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test file
uv run pytest tests/test_main.py
```

### Code Quality

```bash
# Format code
uv run black src tests

# Sort imports
uv run isort src tests

# Lint code
uv run flake8 src tests

# Type checking
uv run mypy src

# Run all quality checks
uv run pre-commit run --all-files
```

## License

This project is licensed under the MIT License.