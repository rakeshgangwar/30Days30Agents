"""
Run the interactive news curator agent.

This script starts the FastAPI server for the interactive news curator agent.
"""

import argparse
import os
import sys

from .interactive import run_server
from .logging import loggers

# Get logger for this module
logger = loggers["interactive"]


def main():
    """Run the interactive news curator agent."""
    logger.info("Initializing interactive news curator agent")

    parser = argparse.ArgumentParser(description="Run the interactive news curator agent")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")

    # Environment variable options
    parser.add_argument("--api-url", help="FreshRSS API URL")
    parser.add_argument("--username", help="FreshRSS username")
    parser.add_argument("--password", help="FreshRSS password")
    parser.add_argument("--server-path", help="Path to FreshRSS MCP server executable")
    parser.add_argument("--model", help="LLM model to use")

    # OpenRouter options
    parser.add_argument("--use-openrouter", action="store_true", help="Use OpenRouter instead of direct API access")
    parser.add_argument("--openrouter-api-key", help="OpenRouter API key")
    parser.add_argument("--openrouter-base-url", help="OpenRouter API base URL")

    # Logging options
    parser.add_argument("--log-level", help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    parser.add_argument("--log-file", help="Path to log file")

    args = parser.parse_args()
    logger.debug(f"Command line arguments: {args}")

    # Set log level if specified
    if args.log_level:
        os.environ["NEWS_AGENT_LOG_LEVEL"] = args.log_level
        logger.info(f"Setting log level to {args.log_level}")

    # Set log directory if specified
    if args.log_file:
        log_dir = os.path.dirname(os.path.abspath(args.log_file))
        os.environ["NEWS_AGENT_LOG_DIR"] = log_dir
        logger.info(f"Setting log directory to {log_dir}")

    # Set environment variables if provided
    if args.api_url:
        os.environ["FRESHRSS_API_URL"] = args.api_url
        logger.debug(f"Setting FRESHRSS_API_URL to {args.api_url}")
    if args.username:
        os.environ["FRESHRSS_USERNAME"] = args.username
        logger.debug(f"Setting FRESHRSS_USERNAME to {args.username}")
    if args.password:
        os.environ["FRESHRSS_PASSWORD"] = args.password
        logger.debug("Setting FRESHRSS_PASSWORD")
    if args.server_path:
        os.environ["FRESHRSS_SERVER_PATH"] = args.server_path
        logger.debug(f"Setting FRESHRSS_SERVER_PATH to {args.server_path}")
    if args.model:
        os.environ["AGENT_MODEL_NAME"] = args.model
        logger.debug(f"Setting AGENT_MODEL_NAME to {args.model}")

    # Set OpenRouter environment variables
    if args.use_openrouter:
        os.environ["USE_OPENROUTER"] = "true"
        logger.debug("Enabling OpenRouter")
    if args.openrouter_api_key:
        os.environ["OPENROUTER_API_KEY"] = args.openrouter_api_key
        logger.debug("Setting OPENROUTER_API_KEY")
    if args.openrouter_base_url:
        os.environ["OPENROUTER_BASE_URL"] = args.openrouter_base_url
        logger.debug(f"Setting OPENROUTER_BASE_URL to {args.openrouter_base_url}")

    # Check for required environment variables
    required_vars = ["FRESHRSS_API_URL", "FRESHRSS_USERNAME", "FRESHRSS_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them using environment variables or command-line arguments.")
        sys.exit(1)

    # Run the server
    logger.info(f"Starting interactive news curator agent on http://{args.host}:{args.port}")
    print(f"Starting interactive news curator agent on http://{args.host}:{args.port}")

    try:
        run_server(host=args.host, port=args.port)
    except Exception as e:
        logger.error(f"Error running interactive server: {e}", exc_info=True)
        print(f"Error running interactive server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
