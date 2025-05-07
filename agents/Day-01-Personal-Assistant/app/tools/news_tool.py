#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
News API tool for the Personal Assistant.

This module implements a LangChain tool for retrieving news articles
using a news API service.
"""

import logging
import requests
from typing import Dict, Any, Type, Optional, List
from datetime import datetime, timedelta

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from config import NEWS_API_KEY, NEWS_API_BASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsInput(BaseModel):
    """Input schema for the news tool."""
    query: Optional[str] = Field(None, description="Search query for news articles")
    category: Optional[str] = Field(None, description="News category (e.g., business, technology, sports)")
    country: str = Field(default="us", description="Country code for news (e.g., us, gb, in)")
    page_size: int = Field(default=5, description="Number of articles to return (max 100)")

class NewsTool(BaseTool):
    """Tool for fetching news articles."""
    
    name: str = "news_tool"
    description: str = "Useful for getting recent news headlines or articles on specific topics"
    args_schema: Type[BaseModel] = NewsInput
    
    def _run(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        country: str = "us",
        page_size: int = 5
    ) -> Dict[str, Any]:
        """
        Get recent news articles.
        
        Args:
            query (Optional[str]): Search query for news articles
            category (Optional[str]): News category
            country (str): Country code for news
            page_size (int): Number of articles to return
            
        Returns:
            Dict[str, Any]: News articles
        """
        try:
            # Validate input
            valid_categories = [
                "business", "entertainment", "general", "health", 
                "science", "sports", "technology"
            ]
            
            if category and category.lower() not in valid_categories:
                return {
                    "error": True,
                    "message": f"Invalid category. Must be one of: {', '.join(valid_categories)}"
                }
            
            # Limit page size
            page_size = min(page_size, 100)
            
            # Prepare request parameters
            params = {
                "apiKey": NEWS_API_KEY,
                "pageSize": page_size,
                "country": country
            }
            
            # Add optional parameters
            if query:
                params["q"] = query
            
            if category:
                params["category"] = category.lower()
            
            # Log request details
            request_info = f"category={category}, query={query}, country={country}"
            logger.info(f"Fetching news articles: {request_info}")
            
            # Make API request
            response = requests.get(NEWS_API_BASE_URL, params=params)
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"News API error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return {
                    "error": True,
                    "message": "Failed to get news articles",
                    "status_code": response.status_code
                }
            
            # Parse response
            data = response.json()
            articles = data.get("articles", [])
            
            # Format articles
            formatted_articles = []
            for article in articles:
                formatted_article = {
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "source": article.get("source", {}).get("name"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt")
                }
                
                formatted_articles.append(formatted_article)
            
            logger.info(f"Successfully fetched {len(formatted_articles)} news articles")
            return {
                "error": False,
                "articles": formatted_articles,
                "count": len(formatted_articles),
                "query": query,
                "category": category,
                "country": country
            }
            
        except Exception as e:
            logger.error(f"Error in NewsTool: {str(e)}")
            return {
                "error": True,
                "message": f"Error getting news: {str(e)}"
            }
    
    def _arun(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        country: str = "us",
        page_size: int = 5
    ) -> Dict[str, Any]:
        """Async implementation of the news tool."""
        # This is just a placeholder - for actual async implementation,
        # we would use aiohttp or similar library
        return self._run(query, category, country, page_size)


class TopicNewsInput(BaseModel):
    """Input schema for the topic-specific news tool."""
    topic: str = Field(description="The topic to get news about")
    days: int = Field(default=7, description="Number of days to look back for news")
    page_size: int = Field(default=5, description="Number of articles to return (max 100)")

class TopicNewsTool(BaseTool):
    """Tool for fetching news articles on specific topics."""
    
    name: str = "topic_news_tool"
    description: str = "Useful for getting news articles about a specific topic"
    args_schema: Type[BaseModel] = TopicNewsInput
    
    def _run(self, topic: str, days: int = 7, page_size: int = 5) -> Dict[str, Any]:
        """
        Get news articles on a specific topic.
        
        Args:
            topic (str): The topic to get news about
            days (int): Number of days to look back for news
            page_size (int): Number of articles to return
            
        Returns:
            Dict[str, Any]: News articles
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Format dates
            from_date = start_date.strftime("%Y-%m-%d")
            to_date = end_date.strftime("%Y-%m-%d")
            
            # Limit page size
            page_size = min(page_size, 100)
            
            # Prepare request parameters
            params = {
                "apiKey": NEWS_API_KEY,
                "q": topic,
                "pageSize": page_size,
                "from": from_date,
                "to": to_date,
                "language": "en",
                "sortBy": "relevancy"
            }
            
            # Different endpoint for everything search
            everything_url = "https://newsapi.org/v2/everything"
            
            # Log request details
            logger.info(f"Fetching news articles about {topic} from {from_date} to {to_date}")
            
            # Make API request
            response = requests.get(everything_url, params=params)
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"News API error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return {
                    "error": True,
                    "message": "Failed to get topic news",
                    "status_code": response.status_code
                }
            
            # Parse response
            data = response.json()
            articles = data.get("articles", [])
            
            # Format articles
            formatted_articles = []
            for article in articles:
                formatted_article = {
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "source": article.get("source", {}).get("name"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt")
                }
                
                formatted_articles.append(formatted_article)
            
            logger.info(f"Successfully fetched {len(formatted_articles)} news articles about {topic}")
            return {
                "error": False,
                "articles": formatted_articles,
                "count": len(formatted_articles),
                "topic": topic,
                "from_date": from_date,
                "to_date": to_date
            }
            
        except Exception as e:
            logger.error(f"Error in TopicNewsTool: {str(e)}")
            return {
                "error": True,
                "message": f"Error getting topic news: {str(e)}"
            }