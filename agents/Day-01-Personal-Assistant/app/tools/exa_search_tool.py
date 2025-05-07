#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exa search tool for the Personal Assistant.

This module implements a LangChain tool for searching the web using Exa AI,
which provides more up-to-date information than Wikipedia.
"""

import logging
from typing import Dict, Any, Type, Optional, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_exa import ExaSearchRetriever

import sys
import os
# Add parent directory to path to import from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EXA_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExaSearchInput(BaseModel):
    """Input schema for the Exa search tool."""
    query: str = Field(description="The search query to look up on the web")
    num_results: int = Field(default=5, description="Number of search results to return (max 10)")

class ExaSearchTool(BaseTool):
    """Tool for searching the web using Exa AI."""

    name: str = "exa_search_tool"
    description: str = "Useful for searching the web for current information, news, and general knowledge."
    args_schema: Type[BaseModel] = ExaSearchInput

    def _run(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Search the web using Exa AI.

        Args:
            query (str): The search query to look up
            num_results (int): Number of search results to return

        Returns:
            Dict[str, Any]: Search results with snippets and URLs
        """
        try:
            # Limit the number of results to a reasonable number
            num_results = min(num_results, 10)

            logger.info(f"Searching Exa for: {query}")

            # Check if API key is available
            if not EXA_API_KEY:
                error_msg = "Exa API key not found. Please set the EXA_API_KEY environment variable."
                logger.error(error_msg)
                return {
                    "error": True,
                    "message": error_msg
                }

            # Initialize the Exa retriever
            retriever = ExaSearchRetriever(
                api_key=EXA_API_KEY,
                k=num_results,
                highlight_results=True,
                include_domains=None,  # Optional: Include only specific domains
                exclude_domains=None,  # Optional: Exclude specific domains
            )

            # Perform the search using the new invoke method instead of get_relevant_documents
            search_results = retriever.invoke(query)

            # Format the results
            formatted_results = []
            for doc in search_results:
                # Extract metadata
                metadata = doc.metadata

                # Format the result
                formatted_result = {
                    "title": metadata.get("title", "No title"),
                    "url": metadata.get("url", ""),
                    "published_date": metadata.get("published_date", ""),
                    "author": metadata.get("author", ""),
                    "snippet": doc.page_content,
                }

                formatted_results.append(formatted_result)

            logger.info(f"Successfully retrieved {len(formatted_results)} results from Exa")

            return {
                "error": False,
                "query": query,
                "results": formatted_results
            }

        except Exception as e:
            logger.error(f"Error in ExaSearchTool: {str(e)}")
            return {
                "error": True,
                "message": f"Error searching with Exa: {str(e)}",
                "query": query
            }

    def _arun(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Async implementation of the Exa search tool."""
        # This is just a placeholder - for actual async implementation,
        # we would use aiohttp or similar library
        return self._run(query, num_results)

class ExaNewsSearchTool(BaseTool):
    """Tool for searching news using Exa AI."""

    name: str = "exa_news_search_tool"
    description: str = "Useful for searching for recent news articles on specific topics."
    args_schema: Type[BaseModel] = ExaSearchInput

    def _run(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Search for news articles using Exa AI.

        Args:
            query (str): The search query for news articles
            num_results (int): Number of news articles to return

        Returns:
            Dict[str, Any]: News search results with snippets and URLs
        """
        try:
            # Limit the number of results to a reasonable number
            num_results = min(num_results, 10)

            logger.info(f"Searching Exa News for: {query}")

            # Check if API key is available
            if not EXA_API_KEY:
                error_msg = "Exa API key not found. Please set the EXA_API_KEY environment variable."
                logger.error(error_msg)
                return {
                    "error": True,
                    "message": error_msg
                }

            # Initialize the Exa retriever with news-specific settings
            retriever = ExaSearchRetriever(
                api_key=EXA_API_KEY,
                k=num_results,
                highlight_results=True,
                # Focus on news domains
                include_domains=[
                    "cnn.com", "bbc.com", "nytimes.com", "reuters.com",
                    "apnews.com", "bloomberg.com", "wsj.com", "ft.com",
                    "theguardian.com", "washingtonpost.com", "aljazeera.com"
                ],
                # Use recency-biased search
                use_recency_bias=True,
                # Limit to recent content
                max_age_days=30
            )

            # Perform the search using the new invoke method instead of get_relevant_documents
            search_results = retriever.invoke(query)

            # Format the results
            formatted_results = []
            for doc in search_results:
                # Extract metadata
                metadata = doc.metadata

                # Format the result
                formatted_result = {
                    "title": metadata.get("title", "No title"),
                    "url": metadata.get("url", ""),
                    "published_date": metadata.get("published_date", ""),
                    "author": metadata.get("author", ""),
                    "snippet": doc.page_content,
                }

                formatted_results.append(formatted_result)

            logger.info(f"Successfully retrieved {len(formatted_results)} news results from Exa")

            return {
                "error": False,
                "query": query,
                "results": formatted_results
            }

        except Exception as e:
            logger.error(f"Error in ExaNewsSearchTool: {str(e)}")
            return {
                "error": True,
                "message": f"Error searching news with Exa: {str(e)}",
                "query": query
            }

    def _arun(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Async implementation of the Exa news search tool."""
        # This is just a placeholder - for actual async implementation,
        # we would use aiohttp or similar library
        return self._run(query, num_results)
