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
- Docker (containerization)

## Setup and Installation

### Prerequisites

- Python 3.9 or higher
- uv package manager

### Option 1: Local Installation

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

7. (Optional) Generate an API key for authentication

```bash
python utils/generate_api_key.py
```

Add the generated API key to your `.env` file.

8. Run the API server with:

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload
```

### Option 2: Docker Installation

1. Clone the repository
2. Navigate to the project directory

```bash
cd agents/Day-04-Writing-Assistant
```

3. Create a `.env` file based on the `.env.example` template

```bash
cd app
cp .env.example .env
cd ..
```

4. Edit the `.env` file and add your OpenRouter API key and other configuration

5. Build and start the Docker container

```bash
docker-compose up --build
```

For more detailed Docker instructions, see the [Docker README](../docker-README.md).

### Accessing the API

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

#### Local Testing

```bash
python run_tests.py
```

With coverage report:

```bash
python run_tests.py --coverage
```

#### Testing in Docker

```bash
docker-compose exec api python run_tests.py
```

## API Endpoints

- `/api/v1/draft` - Generate draft text
- `/api/v1/analyze_grammar_style` - Analyze grammar and style
- `/api/v1/summarize` - Summarize text
- `/api/v1/adjust_tone` - Adjust the tone of text
- `/api/v1/preferences/{user_id}` - Manage user preferences (requires API key)
- `/health` - Health check endpoint

## Authentication

The Writing Assistant API uses API key authentication for endpoints that manage user-specific data.
To use authenticated endpoints, include the API key in the request header:

```
X-API-Key: your-api-key
```

You can generate a secure API key using the provided utility script:

```bash
python utils/generate_api_key.py
```

## License

MIT