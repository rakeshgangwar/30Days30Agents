"""
Configuration module for the news curator agent.

This module handles loading and managing configuration for the agent.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from .models import UserPreferences

# Load environment variables from .env file
load_dotenv()

# Ensure OPENAI_API_KEY is set
if not os.environ.get("OPENAI_API_KEY"):
    # Check common locations for API key
    possible_key_files = [
        Path.home() / ".openai" / "api_key",
        Path.home() / ".openai-api-key",
        Path(".env"),
        Path("../.env"),
        Path("../../.env"),
    ]

    for key_file in possible_key_files:
        if key_file.exists():
            with open(key_file, "r") as f:
                content = f.read().strip()
                if content and not content.startswith("#"):
                    if "=" in content:
                        # Parse as KEY=VALUE format
                        for line in content.splitlines():
                            if line.startswith("OPENAI_API_KEY="):
                                os.environ["OPENAI_API_KEY"] = line.split("=", 1)[1].strip().strip("'\"")
                                break
                    else:
                        # Assume the content is the API key itself
                        os.environ["OPENAI_API_KEY"] = content
                    break


class FreshRSSConfig(BaseModel):
    """Configuration for FreshRSS connection."""

    api_url: str = Field(..., description="URL to the FreshRSS instance")
    username: str = Field(..., description="FreshRSS username")
    password: str = Field(..., description="FreshRSS password")
    server_path: Optional[str] = Field(None, description="Path to the FreshRSS MCP server executable")


class GoogleNewsConfig(BaseModel):
    """Configuration for Google News MCP server."""

    serp_api_key: Optional[str] = Field(None, description="SerpAPI key for Google News")
    server_path: Optional[str] = Field(None, description="Path to the Google News MCP server executable")


class BraveSearchConfig(BaseModel):
    """Configuration for Brave Search MCP server."""

    api_key: Optional[str] = Field(None, description="Brave Search API key")
    server_path: Optional[str] = Field(None, description="Path to the Brave Search MCP server executable")


class AgentConfig(BaseModel):
    """Configuration for the PydanticAI agent."""

    model_name: str = Field("openai:gpt-4o", description="LLM model to use")
    temperature: float = Field(0.2, description="Temperature for LLM generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for LLM generation")
    use_openrouter: bool = Field(False, description="Whether to use OpenRouter instead of direct API access")
    openrouter_api_key: Optional[str] = Field(None, description="OpenRouter API key")
    openrouter_base_url: str = Field("https://openrouter.ai/api/v1", description="OpenRouter API base URL")


class Config(BaseModel):
    """Main configuration for the news curator agent."""

    freshrss: FreshRSSConfig
    google_news: GoogleNewsConfig = Field(default_factory=GoogleNewsConfig)
    brave_search: BraveSearchConfig = Field(default_factory=BraveSearchConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    default_preferences: UserPreferences = Field(default_factory=UserPreferences)


def load_config(config_file: Optional[str] = None) -> Config:
    """Load configuration from environment variables or config file.

    Args:
        config_file: Path to a JSON or YAML configuration file (optional)

    Returns:
        Config object with loaded configuration
    """
    # First try environment variables
    freshrss_config = FreshRSSConfig(
        api_url=os.environ.get("FRESHRSS_API_URL", ""),
        username=os.environ.get("FRESHRSS_USERNAME", ""),
        password=os.environ.get("FRESHRSS_PASSWORD", ""),
        server_path=os.environ.get("FRESHRSS_SERVER_PATH"),
    )

    # Load Google News configuration
    google_news_config = GoogleNewsConfig(
        serp_api_key=os.environ.get("GOOGLE_NEWS_SERP_API_KEY"),
        server_path=os.environ.get("GOOGLE_NEWS_SERVER_PATH"),
    )

    # Load Brave Search configuration
    brave_search_config = BraveSearchConfig(
        api_key=os.environ.get("BRAVE_SEARCH_API_KEY"),
        server_path=os.environ.get("BRAVE_SEARCH_SERVER_PATH"),
    )

    # Check if OpenRouter API key is available
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    use_openrouter = bool(openrouter_api_key) or os.environ.get("USE_OPENROUTER", "").lower() in ("true", "1", "yes")

    # If OpenRouter is enabled but no API key is provided, try to find it
    if use_openrouter and not openrouter_api_key:
        # Check common locations for API key
        possible_key_files = [
            Path.home() / ".openrouter" / "api_key",
            Path.home() / ".openrouter-api-key",
            Path(".env"),
            Path("../.env"),
            Path("../../.env"),
        ]

        for key_file in possible_key_files:
            if key_file.exists():
                with open(key_file, "r") as f:
                    content = f.read().strip()
                    if content and not content.startswith("#"):
                        if "=" in content:
                            # Parse as KEY=VALUE format
                            for line in content.splitlines():
                                if line.startswith("OPENROUTER_API_KEY="):
                                    openrouter_api_key = line.split("=", 1)[1].strip().strip("'\"")
                                    break
                        else:
                            # Assume the content is the API key itself
                            openrouter_api_key = content
                        break

    agent_config = AgentConfig(
        model_name=os.environ.get("AGENT_MODEL_NAME", "anthropic/claude-3-5-sonnet" if use_openrouter else "openai:gpt-4o"),
        temperature=float(os.environ.get("AGENT_TEMPERATURE", "0.2")),
        max_tokens=int(os.environ.get("AGENT_MAX_TOKENS", "0")) or None,
        use_openrouter=use_openrouter,
        openrouter_api_key=openrouter_api_key,
        openrouter_base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    )

    # TODO: Add support for loading from config file

    # Load user preferences from environment variables
    user_prefs = {}

    # Parse sources
    if sources_str := os.environ.get("USER_SOURCES"):
        user_prefs["sources"] = [s.strip() for s in sources_str.split(",")]

    # Parse max articles
    if max_articles := os.environ.get("USER_MAX_ARTICLES"):
        user_prefs["max_articles"] = int(max_articles)

    return Config(
        freshrss=freshrss_config,
        google_news=google_news_config,
        brave_search=brave_search_config,
        agent=agent_config,
        default_preferences=UserPreferences(**user_prefs),
    )
