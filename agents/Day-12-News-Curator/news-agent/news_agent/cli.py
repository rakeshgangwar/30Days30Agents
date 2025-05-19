"""
Command-line interface for the news curator agent.

This module provides a CLI for interacting with the news curator agent.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import List, Optional

from .agent import NewsCuratorAgent
from .config import Config, load_config
from .models import UserPreferences


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="News Curator Agent CLI")

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Briefing command
    briefing_parser = subparsers.add_parser("briefing", help="Create a news briefing")
    briefing_parser.add_argument("--title", help="Title for the briefing")
    briefing_parser.add_argument("--sources", nargs="+", help="Sources to include")
    briefing_parser.add_argument("--max-articles", type=int, help="Maximum number of articles to fetch")
    briefing_parser.add_argument("--output", help="Output file for the briefing (JSON)")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for news articles")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--sources", nargs="+", help="Sources to include")
    search_parser.add_argument("--max-articles", type=int, help="Maximum number of articles to fetch")
    search_parser.add_argument("--output", help="Output file for the results (JSON)")
    search_parser.add_argument("--search-source", choices=["all", "freshrss", "google", "brave"],
                              default="all", help="Which news source to search (default: all)")

    # Get article command
    get_article_parser = subparsers.add_parser("get-article", help="Get a specific article")
    get_article_parser.add_argument("article_id", help="ID of the article to get")

    # List feeds command
    subparsers.add_parser("list-feeds", help="List all feed subscriptions")

    # List unread command
    unread_parser = subparsers.add_parser("list-unread", help="List unread articles")
    unread_parser.add_argument("--limit", type=int, default=50, help="Maximum number of articles to return")

    # Mark as read command
    mark_read_parser = subparsers.add_parser("mark-read", help="Mark an article as read")
    mark_read_parser.add_argument("article_id", help="ID of the article to mark as read")

    return parser.parse_args()


def create_user_preferences(args) -> Optional[UserPreferences]:
    """Create UserPreferences from command-line arguments."""
    # Check if any preference arguments were provided
    has_prefs = any([
        args.sources,
        getattr(args, 'max_articles', None)
    ])

    if not has_prefs:
        return None

    # Create preferences with provided values
    prefs = UserPreferences()

    if args.sources:
        prefs.sources = args.sources

    if getattr(args, 'max_articles', None):
        prefs.max_articles = args.max_articles

    return prefs


async def run_briefing_command(agent: NewsCuratorAgent, args):
    """Run the briefing command."""
    preferences = create_user_preferences(args)
    title = args.title or "Daily News Briefing"

    print(f"Creating briefing: {title}")
    briefing = await agent.create_briefing(preferences, title)

    # Print briefing
    print("\n" + "=" * 50)
    print(f"BRIEFING: {briefing.title}")
    print("=" * 50)

    # Print articles
    print(f"\nFound {len(briefing.articles)} articles:\n")
    for i, article in enumerate(briefing.articles, 1):
        print(f"{i}. {article.title}")
        print(f"   Source: {article.source}")
        print(f"   Date: {article.published_date.date()}")
        print(f"   ID: {article.id}")
        print()

    # Save to file if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump(briefing.model_dump(), f, indent=2, default=str)
        print(f"\nBriefing saved to {args.output}")


async def run_search_command(agent: NewsCuratorAgent, args):
    """Run the search command."""
    preferences = create_user_preferences(args)

    print(f"Searching for: {args.query} (source: {args.search_source})")
    articles = await agent.search_news(args.query, preferences, args.search_source)

    # Print results
    print("\n" + "=" * 50)
    print(f"SEARCH RESULTS: {args.query} (source: {args.search_source})")
    print("=" * 50)
    print(f"\nFound {len(articles)} matching articles:\n")

    for i, article in enumerate(articles, 1):
        print(f"{i}. {article.title}")
        print(f"   Source: {article.source}")
        print(f"   Date: {article.published_date.date()}")
        print(f"   ID: {article.id}")
        print(f"   URL: {article.url}")
        print()

    # Save to file if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump([a.model_dump() for a in articles], f, indent=2, default=str)
        print(f"\nResults saved to {args.output}")


async def run_get_article_command(agent: NewsCuratorAgent, args):
    """Run the get-article command."""
    print(f"Getting article: {args.article_id}")

    try:
        article = await agent.get_article(args.article_id)

        print("\n" + "=" * 50)
        print(f"ARTICLE: {article.title}")
        print("=" * 50)
        print(f"Source: {article.source}")
        print(f"Date: {article.published_date.date()}")
        print(f"URL: {article.url}")
        print("\nCONTENT:")

        # Print a preview of the content (first 500 characters)
        if article.content:
            content_preview = article.content[:500] + "..." if len(article.content) > 500 else article.content
            print(content_preview)
        else:
            print("No content available")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


async def run_list_feeds_command(agent: NewsCuratorAgent, args):
    """Run the list-feeds command."""
    print("Listing feed subscriptions...")

    async with agent.agent.run_mcp_servers():
        result = await agent.freshrss_server.call_tool("list_feeds", {})
        feeds_data = json.loads(result)

        if "feeds" in feeds_data:
            print("\n" + "=" * 50)
            print("FEED SUBSCRIPTIONS")
            print("=" * 50)

            for feed in feeds_data["feeds"]:
                print(f"ID: {feed['id']}")
                print(f"Title: {feed['title']}")
                print(f"URL: {feed.get('url', 'N/A')}")
                print(f"Site URL: {feed.get('site_url', 'N/A')}")
                print()
        else:
            print("No feeds found or error in response")


async def run_list_unread_command(agent: NewsCuratorAgent, args):
    """Run the list-unread command."""
    print(f"Listing unread articles (limit: {args.limit})...")

    async with agent.agent.run_mcp_servers():
        result = await agent.freshrss_server.call_tool("get_unread", {"limit": args.limit})
        unread_data = json.loads(result)

        if "items" in unread_data:
            print("\n" + "=" * 50)
            print("UNREAD ARTICLES")
            print("=" * 50)

            for item in unread_data["items"]:
                print(f"ID: {item['id']}")
                print(f"Title: {item['title']}")
                print(f"Source: {item.get('feed_title', 'Unknown')}")
                print(f"Date: {datetime.fromtimestamp(item['created_on_time']).date()}")
                print()
        else:
            print("No unread articles found or error in response")


async def run_mark_read_command(agent: NewsCuratorAgent, args):
    """Run the mark-read command."""
    print(f"Marking article as read: {args.article_id}")

    async with agent.agent.run_mcp_servers():
        result = await agent.freshrss_server.call_tool("mark_item_read", {"item_id": args.article_id})
        print(result)


async def main():
    """Main entry point for the CLI."""
    args = parse_args()

    if not args.command:
        print("Error: No command specified")
        sys.exit(1)

    # Create agent
    agent = NewsCuratorAgent()

    # Run the appropriate command
    if args.command == "briefing":
        await run_briefing_command(agent, args)
    elif args.command == "search":
        await run_search_command(agent, args)
    elif args.command == "get-article":
        await run_get_article_command(agent, args)
    elif args.command == "list-feeds":
        await run_list_feeds_command(agent, args)
    elif args.command == "list-unread":
        await run_list_unread_command(agent, args)
    elif args.command == "mark-read":
        await run_mark_read_command(agent, args)


def cli_main():
    """Entry point for the CLI."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
