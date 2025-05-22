#!/usr/bin/env python3

import os
import argparse
from dotenv import load_dotenv
import streamlit.web.cli as stcli
import sys

def run_streamlit_app():
    """Run the Streamlit app"""
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "email_assist/ui/streamlit_app.py")
    sys.argv = ["streamlit", "run", filename, "--browser.serverAddress=localhost", "--server.port=8501"]
    sys.exit(stcli.main())

def main():
    """Main entry point for the email assistant application"""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Email Assistant Agent")
    parser.add_argument("--ui", action="store_true", help="Start the Streamlit UI")
    args = parser.parse_args()
    
    if args.ui:
        # Start the Streamlit UI
        run_streamlit_app()
    else:
        # Default to starting the Streamlit UI
        run_streamlit_app()

if __name__ == "__main__":
    main()
