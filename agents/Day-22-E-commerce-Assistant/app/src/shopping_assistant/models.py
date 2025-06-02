"""
Data models for the shopping assistant
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class QueryType(str, Enum):
    SEARCH = "search"
    COMPARE = "compare"
    RECOMMEND = "recommend"
    TRACK = "track"
    SUMMARIZE = "summarize"


class Product(BaseModel):
    """Product information model"""
    id: Optional[str] = None
    title: str
    price: Optional[float] = None
    currency: str = "USD"
    url: str
    image_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    description: Optional[str] = None
    features: List[str] = Field(default_factory=list)
    brand: Optional[str] = None
    category: Optional[str] = None
    availability: Optional[str] = None
    source: str  # e.g., "amazon", "ebay", "scraped"


class Review(BaseModel):
    """Product review model"""
    product_id: str
    rating: float
    title: Optional[str] = None
    content: str
    author: Optional[str] = None
    date: Optional[datetime] = None
    verified: bool = False


class ReviewSummary(BaseModel):
    """Summarized reviews for a product"""
    product_id: str
    overall_rating: float
    total_reviews: int
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    common_themes: List[str] = Field(default_factory=list)
    summary: str


class UserPreferences(BaseModel):
    """User preference model"""
    user_id: str
    preferred_brands: List[str] = Field(default_factory=list)
    preferred_categories: List[str] = Field(default_factory=list)
    price_range: Optional[Dict[str, float]] = None  # {"min": 0, "max": 1000}
    favorite_stores: List[str] = Field(default_factory=list)
    preferred_features: List[str] = Field(default_factory=list)


class SearchQuery(BaseModel):
    """Search query model"""
    query: str
    query_type: QueryType
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    sort_by: Optional[str] = None  # "price", "rating", "relevance"
    sort_order: str = "asc"  # "asc" or "desc"
    max_results: int = 10
    user_id: Optional[str] = None


class PriceTracker(BaseModel):
    """Price tracking model"""
    id: Optional[str] = None
    user_id: str
    product_url: str
    product_title: str
    target_price: float
    current_price: Optional[float] = None
    last_checked: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True


class ComparisonRequest(BaseModel):
    """Product comparison request"""
    product_urls: List[str]
    comparison_criteria: List[str] = Field(default_factory=lambda: ["price", "rating", "features"])


class RecommendationRequest(BaseModel):
    """Product recommendation request"""
    description: str
    user_id: Optional[str] = None
    budget: Optional[float] = None
    preferred_brands: List[str] = Field(default_factory=list)
    must_have_features: List[str] = Field(default_factory=list)
    exclude_categories: List[str] = Field(default_factory=list)


class SearchResult(BaseModel):
    """Search result container"""
    query: str
    products: List[Product]
    total_found: int
    search_time: float
    suggestions: List[str] = Field(default_factory=list)


class ComparisonResult(BaseModel):
    """Product comparison result"""
    products: List[Product]
    comparison_table: Dict[str, Dict[str, Any]]
    winner: Optional[str] = None  # Product ID of the best match
    summary: str 