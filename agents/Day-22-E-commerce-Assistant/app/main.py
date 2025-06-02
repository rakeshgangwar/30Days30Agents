#!/usr/bin/env python3
"""
Main entry point for the Shopping Assistant
"""

import argparse
import sys
import asyncio
import os
from dotenv import load_dotenv
from src.shopping_assistant.database import init_database

# Load environment variables
load_dotenv()


def main():
    """Main entry point with mode selection"""
    parser = argparse.ArgumentParser(description="AI Shopping Assistant")
    parser.add_argument(
        "--mode", 
        choices=["web", "cli", "pydantic-cli"], 
        default="pydantic-cli",
        help="Run mode: web server, original CLI, or Pydantic AI CLI (default: pydantic-cli)"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host for web mode")
    parser.add_argument("--port", type=int, default=8000, help="Port for web mode")
    
    # Parse known args to allow CLI subcommands to pass through
    args, remaining = parser.parse_known_args()
    
    # Initialize database
    init_database()
    
    if args.mode == "web":
        import uvicorn
        print("🚀 Starting web server...")
        print(f"📍 Access at: http://{args.host}:{args.port}")
        uvicorn.run(
            "src.shopping_assistant.api:app",
            host=args.host,
            port=args.port,
            reload=True
        )
    elif args.mode == "cli":
        print("🔧 Starting original CLI...")
        from src.shopping_assistant.cli import main as cli_main
        # Restore sys.argv for CLI parsing
        sys.argv = [sys.argv[0]] + remaining
        cli_main()
    elif args.mode == "pydantic-cli":
        print("🤖 Starting Pydantic AI CLI...")
        
        # Check for OpenAI API key
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ OPENAI_API_KEY environment variable not set")
            print("Please add your OpenAI API key to the .env file")
            return
        
        from src.shopping_assistant.pydantic_cli import main as pydantic_cli_main
        # Restore sys.argv for CLI parsing
        sys.argv = [sys.argv[0]] + remaining
        pydantic_cli_main()


if __name__ == "__main__":
    main() 