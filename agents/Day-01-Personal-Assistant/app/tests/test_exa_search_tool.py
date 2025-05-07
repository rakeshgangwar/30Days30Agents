#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for the Exa search tool.

This script tests the functionality of the Exa search tool
by performing a simple search query.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to the path to import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.exa_search_tool import ExaSearchTool, ExaNewsSearchTool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_exa_search():
    """Test the Exa search tool with a simple query."""
    # Load environment variables
    load_dotenv()
    
    # Check if the Exa API key is available
    exa_api_key = os.getenv("EXA_API_KEY")
    if not exa_api_key:
        logger.error("EXA_API_KEY not found in environment variables. Skipping test.")
        return
    
    # Initialize the tool
    exa_tool = ExaSearchTool()
    
    # Perform a search
    query = "latest developments in artificial intelligence"
    results = exa_tool._run(query, num_results=3)
    
    # Print the results
    logger.info(f"Search query: {query}")
    logger.info(f"Error: {results.get('error', True)}")
    
    if not results.get("error", True):
        logger.info(f"Number of results: {len(results.get('results', []))}")
        
        for i, result in enumerate(results.get("results", []), 1):
            logger.info(f"\nResult {i}:")
            logger.info(f"Title: {result.get('title', 'No title')}")
            logger.info(f"URL: {result.get('url', 'No URL')}")
            logger.info(f"Published: {result.get('published_date', 'Unknown date')}")
            logger.info(f"Snippet: {result.get('snippet', 'No snippet')[:100]}...")
    else:
        logger.error(f"Error message: {results.get('message', 'Unknown error')}")

def test_exa_news_search():
    """Test the Exa news search tool with a simple query."""
    # Load environment variables
    load_dotenv()
    
    # Check if the Exa API key is available
    exa_api_key = os.getenv("EXA_API_KEY")
    if not exa_api_key:
        logger.error("EXA_API_KEY not found in environment variables. Skipping test.")
        return
    
    # Initialize the tool
    exa_news_tool = ExaNewsSearchTool()
    
    # Perform a search
    query = "latest technology news"
    results = exa_news_tool._run(query, num_results=3)
    
    # Print the results
    logger.info(f"News search query: {query}")
    logger.info(f"Error: {results.get('error', True)}")
    
    if not results.get("error", True):
        logger.info(f"Number of results: {len(results.get('results', []))}")
        
        for i, result in enumerate(results.get("results", []), 1):
            logger.info(f"\nResult {i}:")
            logger.info(f"Title: {result.get('title', 'No title')}")
            logger.info(f"URL: {result.get('url', 'No URL')}")
            logger.info(f"Published: {result.get('published_date', 'Unknown date')}")
            logger.info(f"Snippet: {result.get('snippet', 'No snippet')[:100]}...")
    else:
        logger.error(f"Error message: {results.get('message', 'Unknown error')}")

if __name__ == "__main__":
    logger.info("Testing Exa search tool...")
    test_exa_search()
    
    logger.info("\n\nTesting Exa news search tool...")
    test_exa_news_search()
