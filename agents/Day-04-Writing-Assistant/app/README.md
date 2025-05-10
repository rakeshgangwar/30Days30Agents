# Writing Assistant API

This is the backend service for the Writing Assistant application, providing AI-powered writing assistance via a RESTful API.

## Features

- Text drafting (generate new content based on a prompt)
- Grammar and style analysis
- Text summarization
- Tone adjustment
- User preference management

## Tech Stack

- Python 3.9+
- FastAPI (web framework)
- uv (package manager)
- LangChain (LLM orchestration)
- OpenRouter (LLM gateway)
- SQLite/PostgreSQL (database)

## Setup and Installation

### Prerequisites

- Python 3.9 or higher
- uv package manager

### Installation

1. Clone the repository
2. Navigate to the project directory

```bash
cd agents/Day-04-Writing-Assistant/app
```

3. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. Install dependencies using uv

```bash
pip install uv
uv pip install -e .
```

5. Create a `.env` file based on the `.env.example` template

```bash
cp .env.example .env
```

6. Edit the `.env` file and add your OpenRouter API key and other configuration

### Running the API

Run the API server with:

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

API documentation is available at http://localhost:8000/docs

## Development

### Project Structure

```
app/
├── core/           # Core application code
│   ├── config.py   # Configuration settings
├── models/         # Data models
├── routers/        # API routes 
├── services/       # Business logic
├── utils/          # Utility functions
└── tests/          # Test modules
```

### Running Tests

```bash
pytest
```

## API Endpoints

- `/api/v1/draft` - Generate draft text
- `/api/v1/analyze_grammar_style` - Analyze grammar and style
- `/api/v1/summarize` - Summarize text
- `/api/v1/adjust_tone` - Adjust the tone of text
- `/health` - Health check endpoint

## License

MIT