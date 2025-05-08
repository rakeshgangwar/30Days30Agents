#!/usr/bin/env python3
"""Main entry point for the Research Assistant."""

import os
import sys
import argparse
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("research_assistant.log")
    ]
)
logger = logging.getLogger(__name__)

# Add the app module to the path
sys.path.append(str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    from core.agent import ResearchAssistant
    from core.config import validate_config
except ImportError as e:
    logger.error(f"Import error: {e}. Please install dependencies with 'uv pip install -e .'")
    sys.exit(1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Research Assistant CLI")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Research command
    research_parser = subparsers.add_parser("research", help="Conduct research on a topic")
    research_parser.add_argument("query", help="Research query", nargs="+")
    research_parser.add_argument(
        "--output", "-o",
        help="Output file for research results (default: stdout)",
        default=None
    )
    research_parser.add_argument(
        "--format", "-f",
        help="Output format (markdown, json)",
        choices=["markdown", "json"],
        default="markdown"
    )
    research_parser.add_argument(
        "--max-sources", "-m",
        help="Maximum number of sources to use",
        type=int,
        default=7
    )

    # UI command
    ui_parser = subparsers.add_parser("ui", help="Launch the Streamlit UI")
    ui_parser.add_argument(
        "--port", "-p",
        help="Port to run the UI on",
        type=int,
        default=8501
    )

    # Version command
    subparsers.add_parser("version", help="Show version information")

    return parser.parse_args()


def run_research(args):
    """Run research with the specified arguments."""
    try:
        # Validate config
        validate_config()

        # Create the research assistant
        research_assistant = ResearchAssistant()

        # Join query parts into a single string
        query = " ".join(args.query)

        logger.info(f"Starting research on: {query}")
        print(f"Researching: {query}")

        # Conduct research
        result = research_assistant.research(
            query=query,
            max_iterations=50,  # Increased from 20 to 50 to avoid recursion limit errors
            return_intermediate_steps=False
        )

        # Format the output
        if args.format == "json":
            import json
            output = json.dumps(result, indent=2)
        else:  # markdown
            output = format_markdown(result)

        # Write the output
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Research results written to {args.output}")
        else:
            print("\n" + output)

        logger.info(f"Research completed: {query}")

    except Exception as e:
        logger.error(f"Error during research: {e}", exc_info=True)
        print(f"Error: {e}")
        sys.exit(1)


def format_markdown(result):
    """Format research results as Markdown."""
    report = result.get("report", {})

    if not report or "report_text" not in report:
        return f"# Research: {result['query']}\n\nNo research results available."

    # The report text should already be formatted as Markdown
    output = report["report_text"]

    # Add sources section if not already included
    if "## Sources" not in output:
        output += "\n\n## Sources\n\n"
        for idx, source in enumerate(result.get("sources", []), 1):
            output += f"{idx}. [{source['title']}]({source['url']})\n"

    return output


def launch_ui(args):
    """Launch the Streamlit UI."""
    try:
        import streamlit.web.cli as stcli

        # Path to the streamlit app
        streamlit_app = str(Path(__file__).parent / "interface" / "streamlit_app.py")

        # Check if the file exists
        if not os.path.exists(streamlit_app):
            logger.error(f"Streamlit app not found at {streamlit_app}")
            print(f"Error: Streamlit app not found at {streamlit_app}")
            sys.exit(1)

        # Launch the app
        sys.argv = [
            "streamlit", "run",
            streamlit_app,
            "--server.port", str(args.port)
        ]

        logger.info(f"Launching Streamlit UI on port {args.port}")
        print(f"Launching Research Assistant UI at http://localhost:{args.port}")

        stcli.main()

    except ImportError:
        logger.error("Streamlit not installed. Please install with 'uv pip install streamlit'")
        print("Error: Streamlit not installed. Please install with 'uv pip install streamlit'")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error launching UI: {e}", exc_info=True)
        print(f"Error launching UI: {e}")
        sys.exit(1)


def show_version():
    """Show version information."""
    # Get the version from pyproject.toml
    try:
        import tomli
        with open(Path(__file__).parent / "pyproject.toml", "rb") as f:
            pyproject = tomli.load(f)
        version = pyproject.get("project", {}).get("version", "unknown")
    except:
        version = "0.1.0"  # Fallback version

    print(f"Research Assistant v{version}")
    print("A comprehensive research assistant that conducts web research, synthesizes information, and provides summarized findings with citations.")


def main():
    """Main entry point for the Research Assistant."""
    # Load environment variables from .env file
    load_dotenv()

    # Parse command line arguments
    args = parse_args()

    # Execute the appropriate command
    if args.command == "research":
        run_research(args)
    elif args.command == "ui":
        launch_ui(args)
    elif args.command == "version":
        show_version()
    else:
        # No command or invalid command, show help
        show_version()
        print("\nUse one of the following commands:")
        print("  research \"your query\"  - Conduct research on a topic")
        print("  ui                     - Launch the Streamlit UI")
        print("  version                - Show version information")
        print("\nFor more information, use --help with any command")


if __name__ == "__main__":
    main()
