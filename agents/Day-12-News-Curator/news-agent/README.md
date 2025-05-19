# News Agent

A simple PydanticAI agent for retrieving news content from multiple sources.

## Features

- Direct connection to FreshRSS via MCP server
- Integration with Google News via MCP server
- Integration with Brave Search News via MCP server
- Fetch news articles from your feeds
- Search for news content across multiple sources
- Command-line interface for easy interaction
- Interactive web interface for chat-based interaction

## Requirements

- Python 3.10+
- FreshRSS instance with API access enabled
- FreshRSS MCP server (https://github.com/rakeshgangwar/freshrss-mcp-server)
- OpenAI API key or OpenRouter API key

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/news-agent.git
cd news-agent
```

2. Install the package:

```bash
pip install -e .
```

3. Set up environment variables:

   a. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

   b. Edit the `.env` file with your configuration values:

   ```bash
   # Required variables
   FRESHRSS_API_URL="https://your-freshrss-instance.com"
   FRESHRSS_USERNAME="your-username"
   FRESHRSS_PASSWORD="your-password"

   # Optional path to FreshRSS MCP server
   FRESHRSS_SERVER_PATH="/path/to/freshrss-mcp-server/build/index.js"

   # OpenAI API key (if using OpenAI directly)
   OPENAI_API_KEY="your-openai-api-key"

   # Or use OpenRouter (if you prefer)
   USE_OPENROUTER="true"
   OPENROUTER_API_KEY="your-openrouter-api-key"
   AGENT_MODEL_NAME="anthropic/claude-3-5-sonnet"  # Model ID for OpenRouter
   ```

   See `.env.example` for all available configuration options, including user preferences.

## Usage

The agent can be used in two modes: command-line interface (CLI) or interactive web interface.

### Command-line Interface

The agent provides a command-line interface for common operations:

```bash
python -m news_agent cli <command>
```

Available commands:

#### Create a News Briefing

```bash
python -m news_agent cli briefing --sources "TechCrunch" "Wired" --max-articles 10
```

#### Search for News

```bash
python -m news_agent cli search "artificial intelligence" --sources "TechCrunch" "Wired" --max-articles 10 --search-source all
```

You can specify which news source to search with the `--search-source` option:

- `all`: Search all available sources (default)
- `freshrss`: Search only your FreshRSS feeds
- `google`: Search only Google News (requires SerpAPI key)
- `brave`: Search only Brave Search News (requires Brave Search API key)

#### Get a Specific Article

```bash
python -m news_agent cli get-article <article_id>
```

#### List Feed Subscriptions

```bash
python -m news_agent cli list-feeds
```

#### List Unread Articles

```bash
python -m news_agent cli list-unread --limit 20
```

#### Mark an Article as Read

```bash
python -m news_agent cli mark-read <article_id>
```

### Interactive Web Interface

The agent also provides an interactive web interface for chat-based interaction:

```bash
python -m news_agent interactive [options]
```

Options:
- `--host`: Host to bind to (default: 127.0.0.1)
- `--port`: Port to bind to (default: 8000)
- `--api-url`: FreshRSS API URL
- `--username`: FreshRSS username
- `--password`: FreshRSS password
- `--server-path`: Path to FreshRSS MCP server executable
- `--model`: LLM model to use
- `--use-openrouter`: Use OpenRouter instead of direct API access
- `--openrouter-api-key`: OpenRouter API key
- `--openrouter-base-url`: OpenRouter API base URL (default: https://openrouter.ai/api/v1)

Once started, open your browser to http://localhost:8000 (or the specified host/port) to interact with the agent through a chat interface.

Example with OpenRouter:
```bash
python -m news_agent interactive --api-url "https://your-freshrss-instance.com" --username "your-username" --password "your-password" --use-openrouter --openrouter-api-key "your-openrouter-api-key" --model "anthropic/claude-3-5-sonnet"
```

### Python API

You can also use the agent programmatically:

```python
import asyncio
from news_agent.agent import NewsCuratorAgent
from news_agent.models import UserPreferences

async def main():
    # Create agent
    agent = NewsCuratorAgent()

    # Define preferences
    preferences = UserPreferences(
        sources=["TechCrunch", "Wired"],
        max_articles=10
    )

    # Create a briefing
    briefing = await agent.create_briefing(preferences)

    # Print articles
    print(f"Found {len(briefing.articles)} articles:")
    for article in briefing.articles[:5]:
        print(f"- {article.title} ({article.source})")

    # Search for specific news in FreshRSS
    freshrss_results = await agent.search_news("artificial intelligence", source="freshrss")
    print(f"\nFound {len(freshrss_results)} articles about AI in FreshRSS:")
    for article in freshrss_results[:2]:
        print(f"- {article.title} ({article.source})")

    # Search for specific news in Google News (if configured)
    google_results = await agent.search_news("artificial intelligence", source="google")
    print(f"\nFound {len(google_results)} articles about AI in Google News:")
    for article in google_results[:2]:
        print(f"- {article.title} ({article.source})")

    # Search for specific news in Brave Search (if configured)
    brave_results = await agent.search_news("artificial intelligence", source="brave")
    print(f"\nFound {len(brave_results)} articles about AI in Brave Search:")
    for article in brave_results[:2]:
        print(f"- {article.title} ({article.source})")

    # Search across all sources
    all_results = await agent.search_news("artificial intelligence", source="all")
    print(f"\nFound {len(all_results)} articles about AI across all sources:")
    for article in all_results[:3]:
        print(f"- {article.title} ({article.source})")

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

The agent can be configured using environment variables or by passing a `Config` object directly:

```python
from news_agent.config import Config, FreshRSSConfig, AgentConfig
from news_agent.agent import NewsCuratorAgent

# Using OpenAI directly
config = Config(
    freshrss=FreshRSSConfig(
        api_url="https://your-freshrss-instance.com",
        username="your-username",
        password="your-password",
        server_path="/path/to/freshrss-mcp-server/build/index.js"
    ),
    agent=AgentConfig(
        model_name="openai:gpt-4o",
        temperature=0.2
    )
)

# Or using OpenRouter
config_with_openrouter = Config(
    freshrss=FreshRSSConfig(
        api_url="https://your-freshrss-instance.com",
        username="your-username",
        password="your-password",
        server_path="/path/to/freshrss-mcp-server/build/index.js"
    ),
    agent=AgentConfig(
        model_name="anthropic/claude-3-5-sonnet",
        temperature=0.2,
        use_openrouter=True,
        openrouter_api_key="your-openrouter-api-key"
    )
)

agent = NewsCuratorAgent(config)  # Or NewsCuratorAgent(config_with_openrouter)
```

## License

MIT