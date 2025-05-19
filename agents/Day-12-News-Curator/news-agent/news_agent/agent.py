"""
Main agent implementation for the news curator.

This module provides the main NewsCuratorAgent class that integrates all components.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from httpx import AsyncClient
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from .config import Config, load_config
from .logging import loggers
from .models import NewsArticle, NewsBriefing, UserPreferences

# Get logger for this module
logger = loggers["agent"]


class NewsCuratorAgent:
    """Agent for curating news from FreshRSS feeds."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the news curator agent.

        Args:
            config: Configuration for the agent. If None, loads from environment.
        """
        logger.info("Initializing NewsCuratorAgent")
        self.config = config or load_config()
        logger.debug(f"Agent configuration: {self.config.model_dump_json(indent=2)}")

        # Initialize MCP servers
        self.mcp_servers = []

        # Initialize FreshRSS MCP server
        logger.info("Initializing FreshRSS MCP server")
        self.freshrss_server = self._initialize_freshrss_server()
        self.mcp_servers.append(self.freshrss_server)

        # Initialize Google News MCP server if configured
        self.google_news_server = None
        if self.config.google_news.serp_api_key:
            logger.info("Initializing Google News MCP server")
            self.google_news_server = self._initialize_google_news_server()
            if self.google_news_server:
                self.mcp_servers.append(self.google_news_server)

        # Initialize Brave Search MCP server if configured
        self.brave_search_server = None
        if self.config.brave_search.api_key:
            logger.info("Initializing Brave Search MCP server")
            self.brave_search_server = self._initialize_brave_search_server()
            if self.brave_search_server:
                self.mcp_servers.append(self.brave_search_server)

        # Initialize model
        logger.info("Initializing LLM model")
        if self.config.agent.use_openrouter and self.config.agent.openrouter_api_key:
            # Use OpenRouter
            logger.info(f"Using OpenRouter with model: {self.config.agent.model_name}")

            # Create a custom HTTP client with OpenRouter headers if needed
            custom_http_client = AsyncClient(
                headers={
                    "HTTP-Referer": "https://news-curator-agent.example.com",  # Optional
                    "X-Title": "News Curator Agent",  # Optional
                },
                timeout=60.0,  # Increase timeout for model calls
            )
            logger.debug("Created custom HTTP client with OpenRouter headers")

            try:
                model = OpenAIModel(
                    self.config.agent.model_name,
                    provider=OpenAIProvider(
                        base_url=self.config.agent.openrouter_base_url,
                        api_key=self.config.agent.openrouter_api_key,
                        http_client=custom_http_client,
                    ),
                )
                logger.debug("Successfully created OpenAIModel with OpenRouter provider")
            except Exception as e:
                logger.error(f"Error creating OpenRouter model: {e}", exc_info=True)
                raise
        else:
            # Use default model
            logger.info(f"Using default model: {self.config.agent.model_name}")
            model = self.config.agent.model_name

        # Initialize PydanticAI agent
        logger.info("Initializing PydanticAI agent")
        try:
            self.agent = Agent(
                model,
                model_settings={
                    "temperature": self.config.agent.temperature,
                    "max_tokens": self.config.agent.max_tokens,
                },
                system_prompt="""
                You are a news assistant that helps users find news articles from multiple sources.
                Your goal is to provide relevant information based on user requests.

                You have access to the following news sources through MCP tools:

                1. FreshRSS - Access to the user's personal RSS feeds
                   - Use `list_feeds` to see all feed subscriptions
                   - Use `get_unread` to fetch unread articles
                   - Use `get_feed_items` to get articles from a specific feed (requires feed_id)
                   - Use `mark_item_read` to mark an article as read (requires item_id)
                   - Use `mark_item_unread` to mark an article as unread (requires item_id)
                   - Use `mark_feed_read` to mark all items in a feed as read (requires feed_id)
                   - Use `get_items` to get specific articles by their IDs (requires item_ids array)

                2. Google News - Search for news articles across the web
                   - Use `google_news_search` to search for news articles with parameters:
                     - q: Search query (required)
                     - gl: Country code (e.g., us, uk) - default is "us"
                     - hl: Language code (e.g., en) - default is "en"
                     - topic_token: For specific news topics (optional)
                     - publication_token: For specific publishers (optional)
                     - story_token: For full coverage of a story (optional)
                     - section_token: For specific sections (optional)

                3. Brave Search - Search for news, web content, images, and videos
                   - Use `brave_news_search` to search for news articles with parameters:
                     - query: The search term (required)
                     - count: Number of results to return (optional, max 20)

                When responding to users:
                1. Be concise and direct
                2. Include article titles and sources
                3. Provide links when available
                4. For general news queries, use Google News or Brave Search
                5. For personal feed queries, use FreshRSS tools
                6. When appropriate, combine results from multiple sources
                7. Organize results by topic or relevance when there are many results
                """,
                mcp_servers=self.mcp_servers,
            )
            logger.debug("Successfully created PydanticAI agent")
        except Exception as e:
            logger.error(f"Error initializing PydanticAI agent: {e}", exc_info=True)
            raise

        logger.info("NewsCuratorAgent initialization complete")

    async def fetch_articles(self, preferences: Optional[UserPreferences] = None) -> List[NewsArticle]:
        """Fetch articles from FreshRSS.

        Args:
            preferences: User preferences to apply. If None, uses default preferences.

        Returns:
            List of articles
        """
        logger.info("Fetching articles")
        prefs = preferences or self.config.default_preferences
        logger.debug(f"Using preferences: {prefs.model_dump_json(indent=2)}")

        try:
            # Start MCP servers
            logger.debug("Starting MCP servers")
            async with self.agent.run_mcp_servers():
                logger.debug("MCP servers started successfully")

                # Get unread items
                logger.info("Fetching unread items from FreshRSS")
                try:
                    # Call the get_unread tool directly
                    result = await self.freshrss_server.call_tool("get_unread", {"limit": prefs.max_articles})
                    # Parse the JSON result
                    unread_data = json.loads(result)
                    logger.debug(f"Received {len(unread_data.get('items', []))} unread items")
                except Exception as e:
                    logger.error(f"Error fetching unread items: {e}", exc_info=True)
                    raise

                # Parse response and convert to NewsArticle objects
                logger.info("Converting FreshRSS items to NewsArticle objects")
                articles = []
                if "items" in unread_data:
                    for item in unread_data["items"]:
                        try:
                            article = NewsArticle(
                                id=str(item["id"]),
                                title=item["title"],
                                url=item["url"],
                                source=item.get("feed_title", "Unknown"),
                                published_date=datetime.fromtimestamp(item["created_on_time"]),
                                content=item.get("html", ""),
                            )
                            articles.append(article)
                        except Exception as e:
                            logger.warning(f"Error creating NewsArticle from item {item.get('id')}: {e}")
                            continue

                logger.info(f"Created {len(articles)} NewsArticle objects")
                return articles
        except Exception as e:
            logger.error(f"Error in fetch_articles: {e}", exc_info=True)
            raise

    async def create_briefing(
        self, preferences: Optional[UserPreferences] = None, title: str = "Daily News Briefing"
    ) -> NewsBriefing:
        """Create a news briefing with articles from FreshRSS.

        Args:
            preferences: User preferences to apply. If None, uses default preferences.
            title: Title for the briefing

        Returns:
            NewsBriefing object with articles
        """
        prefs = preferences or self.config.default_preferences

        # Fetch articles
        articles = await self.fetch_articles(prefs)

        if not articles:
            # Return empty briefing if no articles found
            return NewsBriefing(
                title=title,
                articles=[]
            )

        # Create the briefing
        return NewsBriefing(
            title=title,
            articles=articles,
        )

    async def search_news(
        self, query: str, preferences: Optional[UserPreferences] = None,
        source: str = "all"
    ) -> List[NewsArticle]:
        """Search for news articles using available sources.

        Args:
            query: Search query
            preferences: User preferences to apply. If None, uses default preferences.
            source: Source to search ("all", "freshrss", "google", "brave")

        Returns:
            List of articles
        """
        if source == "freshrss" or (source == "all" and not self.google_news_server and not self.brave_search_server):
            return await self._search_freshrss(query, preferences)
        elif source == "google" and self.google_news_server:
            return await self._search_google_news(query)
        elif source == "brave" and self.brave_search_server:
            return await self._search_brave_news(query)
        elif source == "all":
            # Combine results from all available sources
            results = []

            # Get FreshRSS results
            freshrss_results = await self._search_freshrss(query, preferences)
            results.extend(freshrss_results)

            # Get Google News results if available
            if self.google_news_server:
                google_results = await self._search_google_news(query)
                results.extend(google_results)

            # Get Brave Search results if available
            if self.brave_search_server:
                brave_results = await self._search_brave_news(query)
                results.extend(brave_results)

            return results
        else:
            # Default to FreshRSS search
            return await self._search_freshrss(query, preferences)

    async def _search_freshrss(
        self, query: str, preferences: Optional[UserPreferences] = None
    ) -> List[NewsArticle]:
        """Search for news articles in FreshRSS.

        Args:
            query: Search query
            preferences: User preferences to apply. If None, uses default preferences.

        Returns:
            List of articles
        """
        # Fetch all articles
        articles = await self.fetch_articles(preferences)

        # Simple client-side search
        if not query:
            return articles

        # Filter articles that contain the query in title or content
        query = query.lower()
        return [
            article for article in articles
            if query in article.title.lower() or
               (article.content and query in article.content.lower())
        ]

    async def _search_google_news(self, query: str, count: int = 10) -> List[NewsArticle]:
        """Search for news articles using Google News.

        Args:
            query: Search query
            count: Number of results to return

        Returns:
            List of articles
        """
        if not self.google_news_server:
            logger.warning("Google News MCP server not initialized")
            return []

        try:
            # Start MCP servers
            async with self.agent.run_mcp_servers():
                # Call the Google News search tool
                result = await self.google_news_server.call_tool(
                    "google_news_search",
                    {"q": query, "gl": "us", "hl": "en"}
                )

                # Parse the result
                news_data = json.loads(result)

                articles = []
                if "news_results" in news_data:
                    for item in news_data["news_results"][:count]:
                        try:
                            # Convert to our NewsArticle model
                            published_date = datetime.now()
                            if "date" in item:
                                # Try to parse the date
                                try:
                                    # Google News dates are often in format like "2 hours ago" or "3 days ago"
                                    # For now, just use current date
                                    published_date = datetime.now()
                                except:
                                    pass

                            article = NewsArticle(
                                id=f"google-{item.get('position', 0)}",
                                title=item.get("title", "Untitled"),
                                url=item.get("link", ""),
                                source=item.get("source", "Google News"),
                                published_date=published_date,
                                content=item.get("snippet", ""),
                            )
                            articles.append(article)
                        except Exception as e:
                            logger.warning(f"Error creating NewsArticle from Google News item: {e}")
                            continue

                return articles

        except Exception as e:
            logger.error(f"Error searching Google News: {e}", exc_info=True)
            return []

    async def _search_brave_news(self, query: str, count: int = 10) -> List[NewsArticle]:
        """Search for news articles using Brave Search.

        Args:
            query: Search query
            count: Number of results to return

        Returns:
            List of articles
        """
        if not self.brave_search_server:
            logger.warning("Brave Search MCP server not initialized")
            return []

        try:
            # Start MCP servers
            async with self.agent.run_mcp_servers():
                # Call the Brave News search tool
                result = await self.brave_search_server.call_tool(
                    "brave_news_search",
                    {"query": query, "count": count}
                )

                # Parse the result
                news_data = json.loads(result)

                articles = []
                if "results" in news_data:
                    for item in news_data["results"]:
                        try:
                            # Convert to our NewsArticle model
                            published_date = datetime.now()
                            if "age" in item:
                                # Try to parse the date
                                try:
                                    # Brave Search dates are often in format like "2 hours ago" or "3 days ago"
                                    # For now, just use current date
                                    published_date = datetime.now()
                                except:
                                    pass

                            article = NewsArticle(
                                id=f"brave-{item.get('index', 0)}",
                                title=item.get("title", "Untitled"),
                                url=item.get("url", ""),
                                source=item.get("source", "Brave Search"),
                                published_date=published_date,
                                content=item.get("description", ""),
                            )
                            articles.append(article)
                        except Exception as e:
                            logger.warning(f"Error creating NewsArticle from Brave Search item: {e}")
                            continue

                return articles

        except Exception as e:
            logger.error(f"Error searching Brave News: {e}", exc_info=True)
            return []

    def _initialize_freshrss_server(self) -> MCPServerStdio:
        """Initialize the FreshRSS MCP server.

        Returns:
            Initialized MCPServerStdio instance
        """
        # Find the server path if not provided
        server_path = self.config.freshrss.server_path
        if server_path is None:
            logger.info("No FreshRSS server path provided, searching in common locations")
            # Try to find the server in common locations
            possible_paths = [
                os.path.expanduser("~/Projects/news_curator/freshrss-mcp-server/build/index.js"),
                os.path.expanduser("~/freshrss-mcp-server/build/index.js"),
                "./freshrss-mcp-server/build/index.js",
                "../freshrss-mcp-server/build/index.js",
            ]

            for path in possible_paths:
                logger.debug(f"Checking path: {path}")
                if os.path.exists(path):
                    server_path = path
                    logger.info(f"Found FreshRSS MCP server at: {server_path}")
                    break

            if server_path is None:
                logger.error("Could not find FreshRSS MCP server in any common location")
                raise ValueError(
                    "Could not find FreshRSS MCP server. Please provide the path explicitly."
                )
        else:
            logger.info(f"Using provided FreshRSS server path: {server_path}")

            # Verify the server path exists
            if not os.path.exists(server_path):
                logger.error(f"Provided FreshRSS server path does not exist: {server_path}")
                raise ValueError(f"FreshRSS MCP server not found at: {server_path}")

        # Create the MCP server
        logger.info("Creating FreshRSS MCPServerStdio instance")
        try:
            return MCPServerStdio(
                "node",
                args=[server_path],
                env={
                    "FRESHRSS_API_URL": self.config.freshrss.api_url,
                    "FRESHRSS_USERNAME": self.config.freshrss.username,
                    "FRESHRSS_PASSWORD": self.config.freshrss.password,
                }
            )
        except Exception as e:
            logger.error(f"Error creating FreshRSS MCPServerStdio: {e}", exc_info=True)
            raise

    def _initialize_google_news_server(self) -> Optional[MCPServerStdio]:
        """Initialize the Google News MCP server.

        Returns:
            Initialized MCPServerStdio instance or None if not configured
        """
        if not self.config.google_news.serp_api_key:
            logger.warning("No Google News SerpAPI key provided, skipping initialization")
            return None

        # Find the server path
        server_path = self.config.google_news.server_path
        if server_path is None:
            logger.info("No Google News server path provided, searching in common locations")
            # Try to find the server in common locations
            possible_paths = [
                os.path.expanduser("~/Projects/news_curator/server-google-news/dist/index.js"),
                os.path.expanduser("~/server-google-news/dist/index.js"),
                "./server-google-news/dist/index.js",
                "../server-google-news/dist/index.js",
                # Try NPX path
                "server-google-news",
                "@chanmeng666/google-news-server",
            ]

            for path in possible_paths:
                if os.path.exists(path) or path.startswith("@"):
                    server_path = path
                    logger.info(f"Found Google News MCP server at: {server_path}")
                    break

            if server_path is None:
                logger.warning("Could not find Google News MCP server, skipping initialization")
                return None
        else:
            logger.info(f"Using provided Google News server path: {server_path}")

            # Verify the server path exists if it's a file path
            if not server_path.startswith("@") and not os.path.exists(server_path):
                logger.warning(f"Provided Google News server path does not exist: {server_path}")
                return None

        # Create the MCP server
        logger.info("Creating Google News MCPServerStdio instance")
        try:
            # If it's an NPX package, use npx to run it
            if server_path.startswith("@") or not os.path.exists(server_path):
                return MCPServerStdio(
                    "npx",
                    args=["-y", server_path],
                    env={
                        "SERP_API_KEY": self.config.google_news.serp_api_key,
                    }
                )
            else:
                # Otherwise run it directly with node
                return MCPServerStdio(
                    "node",
                    args=[server_path],
                    env={
                        "SERP_API_KEY": self.config.google_news.serp_api_key,
                    }
                )
        except Exception as e:
            logger.error(f"Error creating Google News MCPServerStdio: {e}", exc_info=True)
            return None

    def _initialize_brave_search_server(self) -> Optional[MCPServerStdio]:
        """Initialize the Brave Search MCP server.

        Returns:
            Initialized MCPServerStdio instance or None if not configured
        """
        if not self.config.brave_search.api_key:
            logger.warning("No Brave Search API key provided, skipping initialization")
            return None

        # Find the server path
        server_path = self.config.brave_search.server_path
        if server_path is None:
            logger.info("No Brave Search server path provided, searching in common locations")
            # Try to find the server in common locations
            possible_paths = [
                os.path.expanduser("~/Projects/news_curator/brave-search-mcp/dist/index.js"),
                os.path.expanduser("~/brave-search-mcp/dist/index.js"),
                "./brave-search-mcp/dist/index.js",
                "../brave-search-mcp/dist/index.js",
                # Try NPX path
                "brave-search-mcp",
            ]

            for path in possible_paths:
                if os.path.exists(path) or not path.startswith("./"):
                    server_path = path
                    logger.info(f"Found Brave Search MCP server at: {server_path}")
                    break

            if server_path is None:
                logger.warning("Could not find Brave Search MCP server, skipping initialization")
                return None
        else:
            logger.info(f"Using provided Brave Search server path: {server_path}")

            # Verify the server path exists if it's a file path
            if server_path.startswith("./") and not os.path.exists(server_path):
                logger.warning(f"Provided Brave Search server path does not exist: {server_path}")
                return None

        # Create the MCP server
        logger.info("Creating Brave Search MCPServerStdio instance")
        try:
            # If it's an NPX package, use npx to run it
            if not server_path.startswith("./"):
                return MCPServerStdio(
                    "npx",
                    args=["-y", server_path],
                    env={
                        "BRAVE_API_KEY": self.config.brave_search.api_key,
                    }
                )
            else:
                # Otherwise run it directly with node
                return MCPServerStdio(
                    "node",
                    args=[server_path],
                    env={
                        "BRAVE_API_KEY": self.config.brave_search.api_key,
                    }
                )
        except Exception as e:
            logger.error(f"Error creating Brave Search MCPServerStdio: {e}", exc_info=True)
            return None

    async def get_article(self, article_id: str) -> NewsArticle:
        """Get a specific article by ID.

        Args:
            article_id: ID of the article to get

        Returns:
            The article
        """
        # Start MCP servers
        async with self.agent.run_mcp_servers():
            # Get the article
            result = await self.freshrss_server.call_tool("get_items", {"item_ids": [article_id]})
            article_data = json.loads(result)

            if "items" not in article_data or not article_data["items"]:
                raise ValueError(f"Article with ID {article_id} not found")

            item = article_data["items"][0]
            article = NewsArticle(
                id=str(item["id"]),
                title=item["title"],
                url=item["url"],
                source=item.get("feed_title", "Unknown"),
                published_date=datetime.fromtimestamp(item["created_on_time"]),
                content=item.get("html", ""),
            )

            return article
