# Day 1: Personal Assistant

This directory contains the implementation of the Personal Assistant agent based on the LangChain framework.

## Overview

The Personal Assistant is a foundation agent that handles basic personal assistance tasks such as setting reminders, answering questions, and providing information.

## Architecture

This implementation follows the architecture outlined in `../docs/architecture.md`, featuring:

- A hierarchical memory system (working, short-term, and long-term memory)
- Intent classification and entity extraction for query understanding
- Execution planning for orchestrating tool use
- Multiple tool integrations (Weather, Wikipedia, News, Todoist)
- Adaptable interfaces (CLI, Streamlit, and Telegram)

## Features

- Natural language query processing
- Information retrieval from multiple sources (Weather API, Wikipedia, News API)
- Basic memory to track user preferences
- Task management through Todoist integration
- Multiple user interfaces:
  - Command-line interface
  - Web-based interface (Streamlit)
  - Telegram bot interface

## Directory Structure

```
app/
├── agent.py            # Main agent definition
├── memory.py           # Hierarchical memory system
├── config.py           # Configuration settings
├── interface_adapter.py # Interface abstraction
├── cli.py              # Command-line interface
├── streamlit_app.py    # Web interface using Streamlit
├── telegram_bot.py     # Telegram bot interface
├── requirements.txt    # Dependencies
├── README.md           # This file
├── chains/             # Chain components
│   ├── intent_classification.py  # Intent classifier
│   ├── entity_extraction.py      # Entity extractor
│   └── execution_planner.py      # Execution planner
├── prompts/            # Prompt templates
│   └── base_prompts.py           # Prompt definitions
├── tests/              # Test files
│   ├── test_intent_classification.py  # Intent classification tests
│   └── test_weather_tool.py           # Weather tool tests
└── tools/              # Tool integrations
    ├── weather_tool.py           # Weather API integration
    ├── wikipedia_tool.py         # Wikipedia API integration
    ├── news_tool.py              # News API integration
    └── todoist_tool.py           # Todoist API integration
```

## Setup

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver that we use for this project.

1. Install uv if you haven't already:
   ```bash
   pip install uv
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   # Navigate to the app directory
   cd agents/Day-01-Personal-Assistant/app

   # Create a virtual environment
   uv venv

   # Activate the virtual environment
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   # Install in development mode
   uv pip install -e .
   ```

   If you encounter any build errors, try cleaning up any previous build artifacts:
   ```bash
   rm -rf *.egg-info build dist
   ```

4. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   WEATHER_API_KEY=your_weather_api_key
   NEWS_API_KEY=your_news_api_key
   TODOIST_API_KEY=your_todoist_api_key
   EXA_API_KEY=your_exa_api_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   ```

   You can copy the .env.example file and fill in your API keys:
   ```bash
   cp .env.example .env
   ```

### Using Traditional pip/venv (Alternative)

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your API keys as described above.

## Running the Assistant

### Using Entry Points (After Installing with uv)

After installing the package with `uv pip install -e .`, you can use the entry points:

```bash
# Run the CLI interface
personal-assistant

# Run the Streamlit interface
personal-assistant-streamlit
```

### Running Scripts Directly

#### Command Line Interface

```bash
# If you've installed the package
python -m app.main

# Or run the script directly
python main.py
```

#### Streamlit Web Interface

```bash
# If you've installed the package
python -m streamlit run app.streamlit_app

# Or run the script directly
streamlit run streamlit_app.py
```

#### Telegram Bot Interface

```bash
# If you've installed the package
python -m app.telegram_bot

# Or run the script directly
python telegram_bot.py

# Or use the convenience script
./run_telegram_bot.sh
```

For detailed instructions on setting up the Telegram bot, see [docs/telegram_setup.md](docs/telegram_setup.md).

## Usage Examples

### Weather Query
```
You: What's the weather like in New York today?
```

### Setting a Reminder
```
You: Remind me to call my doctor tomorrow at 10 AM
```

### Knowledge Query
```
You: How many calories are in an apple?
```

### News Query
```
You: Tell me the latest news about technology
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest app/tests/test_intent_classification.py
```

### Linting and Type Checking

```bash
# Run linting with ruff
ruff check .

# Run type checking with mypy
mypy .
```

## Troubleshooting

### Package Build Issues

If you encounter issues with `uv sync` or `uv pip install -e .`, try the following:

1. Clean up any previous build artifacts:
   ```bash
   rm -rf *.egg-info build dist
   ```

2. Make sure you're running the commands from the `app` directory:
   ```bash
   cd agents/Day-01-Personal-Assistant/app
   ```

3. Check for any syntax errors in your Python files:
   ```bash
   python -m compileall .
   ```

### Import Errors

If you see import errors like `ModuleNotFoundError: No module named 'app'`, ensure:

1. The package is installed in development mode:
   ```bash
   uv pip install -e .
   ```

2. You're running the code from the correct directory:
   ```bash
   # To run directly
   cd agents/Day-01-Personal-Assistant
   python -m app.main

   # To run after installation
   personal-assistant
   ```

## Future Improvements

- Add more sophisticated memory management with VectorStoreRetrieverMemory
- Implement more advanced tools and API integrations
- Add user authentication for multi-user support
- Enhance the Telegram interface implementation
- Add voice interface support