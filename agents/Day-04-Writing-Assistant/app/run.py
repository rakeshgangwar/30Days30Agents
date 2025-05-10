#!/usr/bin/env python
"""
Entry point script for running the Writing Assistant API.

This script makes it easy to run the application directly from the project root.
"""
import os
import sys
import uvicorn

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

if __name__ == "__main__":
    print(f"Starting server from {project_root}")
    # Start the application with reload enabled for development
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)