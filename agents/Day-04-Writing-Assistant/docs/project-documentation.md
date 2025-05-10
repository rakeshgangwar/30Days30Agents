# Writing Assistant Project Documentation

## Project Overview

The Writing Assistant is an AI-powered tool designed to help users with various writing tasks, including drafting content, editing, proofreading, summarizing, and adapting text for different audiences or tones. Unlike standalone writing applications, this project takes an integration-first approach, focusing on bringing AI writing assistance directly into users' existing workflows through extensions and plugins for popular writing tools.

## Architecture

The Writing Assistant follows a layered architecture with three main components:

1. **Backend Service**: A FastAPI-based Python service that handles the core AI functionality
2. **Shared Connector Library**: A TypeScript/JavaScript library that provides common functionality for all client integrations
3. **Client Integrations**: Extensions and plugins for various writing tools (VS Code, Obsidian, etc.)

### Architecture Diagram

```
┌─────────────────────────┐
│ User Writing Environments│
│  (VS Code, Obsidian)     │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│ Connectors / Plugins     │
│  (Using Shared Library)  │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│ Core Writing Assistant   │
│ Service (Backend)        │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│ LLM Services             │
│ (OpenRouter)             │
└─────────────────────────┘
```

## Key Features

- **Content Generation**: Draft emails, articles, social media posts based on prompts
- **Text Summarization**: Create concise summaries in paragraph or bullet point format
- **Grammar and Style Analysis**: Check text for grammar, style, and spelling issues
- **Tone Adjustment**: Change the tone of text (formal, casual, professional, etc.)
- **User Preferences**: Save and apply user preferences across different writing environments
- **Dynamic Model Selection**: Fetch available models from OpenRouter API with caching

## Technical Components

### Backend (Python/FastAPI)

The backend service is built with FastAPI and provides the following endpoints:

- `/api/v1/draft` - Generate draft text based on a prompt
- `/api/v1/analyze_grammar_style` - Analyze text for grammar and style issues
- `/api/v1/summarize` - Summarize text in different formats
- `/api/v1/adjust_tone` - Adjust the tone of text
- `/api/v1/preferences/{user_id}` - Manage user preferences
- `/api/v1/models` - Get available LLM models from OpenRouter
- `/health` - Health check endpoint

The backend uses:
- **FastAPI**: For the web framework
- **OpenRouter**: As a gateway to access various LLM models
- **SQLite/PostgreSQL**: For storing user preferences
- **uv**: For Python package management
- **httpx**: For making asynchronous HTTP requests

### Shared Connector Library (TypeScript)

The shared connector library provides a consistent interface for all client integrations to interact with the backend service. It includes:

- **ApiService**: For making API calls to the backend
- **Data Models**: TypeScript interfaces and enums for request/response objects
- **Utility Functions**: For working with API responses
- **Error Handling**: Custom error classes for better error handling

### VS Code Extension (TypeScript)

The VS Code extension integrates the Writing Assistant into VS Code, providing:

- **Commands**: For triggering writing assistant features
- **Context Menu**: For easy access to commands
- **Toolbar Buttons**: For quick access to common features
- **Preferences Panel**: For managing user preferences
- **Result Display**: For showing results in a new editor or webview

## Development Setup

### Backend Setup

1. Clone the repository
2. Navigate to the project directory: `cd agents/Day-04-Writing-Assistant/app`
3. Create a virtual environment: `python -m venv .venv`
4. Activate the virtual environment: `source .venv/bin/activate`
5. Install dependencies: `pip install uv && uv pip install -e .`
6. Create a `.env` file with your OpenRouter API key
7. Run the server: `python -m app.main`

### Library Setup

1. Navigate to the library directory: `cd agents/Day-04-Writing-Assistant/lib`
2. Install dependencies: `npm install`
3. Build the library: `npm run build`
4. Link for local development: `npm link`

### VS Code Extension Setup

1. Navigate to the extension directory: `cd agents/Day-04-Writing-Assistant/vscode-extension`
2. Install dependencies: `npm install`
3. Link the library: `npm link writing-assistant-connector`
4. Build the extension: `npm run compile`
5. Launch the extension: Press F5 in VS Code

## Docker Support

The project includes Docker support for easier deployment:

1. Navigate to the project directory: `cd agents/Day-04-Writing-Assistant`
2. Create a `.env` file in the `app` directory
3. Build and start the container: `docker-compose up --build`

## Future Enhancements

1. **Additional Client Integrations**: Develop plugins for Obsidian, LibreOffice, and browser-based editors
2. **Advanced Features**:
   - Handling longer documents through chunking
   - User-specific style profiles
   - Integration with external grammar checking tools
3. **Performance Optimization**: Improve caching and response times
4. **Comprehensive Documentation**: Create detailed user guides and API documentation

## Conclusion

The Writing Assistant project provides a flexible, integration-first approach to AI-powered writing assistance. By focusing on bringing AI capabilities directly into users' existing writing tools, it eliminates context switching and enhances productivity. The modular architecture allows for easy extension to support additional writing environments in the future.
