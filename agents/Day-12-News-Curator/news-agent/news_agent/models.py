"""
Models for the news curator agent.

This module defines the Pydantic models used throughout the news curator agent.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class NewsSource(BaseModel):
    """Model representing a news source."""

    id: str
    name: str
    url: HttpUrl
    category: Optional[str] = None


class UserPreferences(BaseModel):
    """Model representing user preferences for news curation."""

    sources: List[str] = Field(default_factory=list, description="Preferred news sources")
    max_articles: int = Field(20, description="Maximum articles to fetch")


class NewsArticle(BaseModel):
    """Model representing a news article."""

    id: str
    title: str
    url: HttpUrl
    source: str
    published_date: datetime
    content: Optional[str] = None


class NewsBriefing(BaseModel):
    """Model representing a curated news briefing."""

    title: str
    timestamp: datetime = Field(default_factory=datetime.now)
    articles: List[NewsArticle] = Field(default_factory=list)
