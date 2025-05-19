"""
Main entry point for the news curator agent.

This module provides entry points for both CLI and interactive web interfaces.
"""

import argparse
import os
import sys

from news_agent.cli import cli_main
from news_agent.logging import loggers
from news_agent.run_interactive import main as interactive_main

# Get logger for this module
logger = loggers["app"]


def main():
    """Main entry point with command selection."""
    logger.info("Starting News Curator Agent")

    # Set up command line argument parser
    parser = argparse.ArgumentParser(description="News Curator Agent")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # CLI command
    cli_parser = subparsers.add_parser("cli", help="Run the command-line interface")

    # Interactive command
    interactive_parser = subparsers.add_parser("interactive", help="Run the interactive web interface")
    interactive_parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    interactive_parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    interactive_parser.add_argument("--api-url", help="FreshRSS API URL")
    interactive_parser.add_argument("--username", help="FreshRSS username")
    interactive_parser.add_argument("--password", help="FreshRSS password")
    interactive_parser.add_argument("--server-path", help="Path to FreshRSS MCP server executable")
    interactive_parser.add_argument("--model", help="LLM model to use")

    # OpenRouter options
    interactive_parser.add_argument("--use-openrouter", action="store_true", help="Use OpenRouter instead of direct API access")
    interactive_parser.add_argument("--openrouter-api-key", help="OpenRouter API key")
    interactive_parser.add_argument("--openrouter-base-url", help="OpenRouter API base URL")

    # Logging options
    interactive_parser.add_argument("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    interactive_parser.add_argument("--log-file", help="Path to log file")

    # Parse arguments
    args = parser.parse_args()

    # Set log level if specified
    if hasattr(args, 'log_level') and args.log_level:
        os.environ["NEWS_AGENT_LOG_LEVEL"] = args.log_level
        logger.info(f"Setting log level to {args.log_level}")

    # Set log directory if specified
    if hasattr(args, 'log_file') and args.log_file:
        log_dir = os.path.dirname(os.path.abspath(args.log_file))
        os.environ["NEWS_AGENT_LOG_DIR"] = log_dir
        logger.info(f"Setting log directory to {log_dir}")

    logger.debug(f"Command line arguments: {args}")

    if args.command == "interactive":
        logger.info("Starting interactive web interface")
        # Pass arguments to interactive main
        sys.argv = [sys.argv[0]]
        if args.host:
            sys.argv.extend(["--host", args.host])
            logger.debug(f"Setting host to {args.host}")
        if args.port:
            sys.argv.extend(["--port", str(args.port)])
            logger.debug(f"Setting port to {args.port}")
        if args.api_url:
            sys.argv.extend(["--api-url", args.api_url])
            logger.debug(f"Setting API URL to {args.api_url}")
        if args.username:
            sys.argv.extend(["--username", args.username])
            logger.debug(f"Setting username to {args.username}")
        if args.password:
            sys.argv.extend(["--password", args.password])
            logger.debug("Password provided")
        if args.server_path:
            sys.argv.extend(["--server-path", args.server_path])
            logger.debug(f"Setting server path to {args.server_path}")
        if args.model:
            sys.argv.extend(["--model", args.model])
            logger.debug(f"Setting model to {args.model}")
        if args.use_openrouter:
            sys.argv.append("--use-openrouter")
            logger.debug("Using OpenRouter")
        if args.openrouter_api_key:
            sys.argv.extend(["--openrouter-api-key", args.openrouter_api_key])
            logger.debug("OpenRouter API key provided")
        if args.openrouter_base_url:
            sys.argv.extend(["--openrouter-base-url", args.openrouter_base_url])
            logger.debug(f"Setting OpenRouter base URL to {args.openrouter_base_url}")

        try:
            interactive_main()
        except Exception as e:
            logger.error(f"Error in interactive mode: {e}", exc_info=True)
            sys.exit(1)
    else:
        # Default to CLI
        logger.info("Starting command-line interface")
        try:
            cli_main()
        except Exception as e:
            logger.error(f"Error in CLI mode: {e}", exc_info=True)
            sys.exit(1)


if __name__ == "__main__":
    main()
