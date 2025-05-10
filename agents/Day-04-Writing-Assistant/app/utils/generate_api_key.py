#!/usr/bin/env python
"""
API Key Generation Utility

This script generates a secure API key for the Writing Assistant API.
"""
import os
import sys

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.core.security import generate_api_key


def main():
    """Generate and print a new API key."""
    api_key = generate_api_key()
    print("\nGenerated API Key:")
    print("-" * 50)
    print(api_key)
    print("-" * 50)
    print("\nAdd this to your .env file as:")
    print(f"API_KEY={api_key}")
    print("\nThis key will be required for authenticated endpoints.")


if __name__ == "__main__":
    main()
