#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for the Personal Assistant agent with Exa search tools.

This script tests the agent's ability to use the Exa search tools
for web search and news search.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the parent directory to the path to import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import create_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_agent_exa_search():
    """Test the agent with a web search query."""
    # Load environment variables
    load_dotenv()
    
    # Check if the required API keys are available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    exa_api_key = os.getenv("EXA_API_KEY")
    
    if not openai_api_key or not exa_api_key:
        logger.error("Required API keys not found. Skipping test.")
        return
    
    # Create the agent
    logger.info("Creating agent...")
    agent_executor = create_agent(verbose=True)
    
    # Test web search query
    web_search_query = "What are the latest developments in quantum computing?"
    logger.info(f"Testing web search query: {web_search_query}")
    
    try:
        response = agent_executor.invoke({"input": web_search_query})["output"]
        logger.info(f"Agent response: {response}")
    except Exception as e:
        logger.error(f"Error during web search test: {str(e)}")

def test_agent_exa_news_search():
    """Test the agent with a news search query."""
    # Load environment variables
    load_dotenv()
    
    # Check if the required API keys are available
    openai_api_key = os.getenv("OPENAI_API_KEY")
    exa_api_key = os.getenv("EXA_API_KEY")
    
    if not openai_api_key or not exa_api_key:
        logger.error("Required API keys not found. Skipping test.")
        return
    
    # Create the agent
    logger.info("Creating agent...")
    agent_executor = create_agent(verbose=True)
    
    # Test news search query
    news_search_query = "What are the latest news about climate change?"
    logger.info(f"Testing news search query: {news_search_query}")
    
    try:
        response = agent_executor.invoke({"input": news_search_query})["output"]
        logger.info(f"Agent response: {response}")
    except Exception as e:
        logger.error(f"Error during news search test: {str(e)}")

if __name__ == "__main__":
    logger.info("Testing agent with Exa web search...")
    test_agent_exa_search()
    
    logger.info("\n\nTesting agent with Exa news search...")
    test_agent_exa_news_search()
