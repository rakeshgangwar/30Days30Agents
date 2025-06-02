"""
Pydantic AI-based Shopping Assistant Agent
"""

import logging
from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from pydantic_ai.tools import Tool

from .models import (
    Product, SearchResult, ComparisonResult, ReviewSummary, 
    PriceTracker, UserPreferences
)
from .scrapers import ProductScraper
from .database import SessionLocal, UserPreferencesDB, PriceTrackerDB

logger = logging.getLogger(__name__)


@dataclass
class ShoppingDependencies:
    """Dependencies injected into the shopping agent"""
    scraper: ProductScraper
    user_id: Optional[str] = None


class ProductSearchQuery(BaseModel):
    """Structured search query with AI-extracted parameters"""
    query: str = Field(description="Original search query")
    category: Optional[str] = Field(description="Product category (e.g., 'headphones', 'laptop', 'shoes')")
    price_min: Optional[float] = Field(description="Minimum price constraint")
    price_max: Optional[float] = Field(description="Maximum price constraint")
    features: List[str] = Field(default_factory=list, description="Required features")
    brands: List[str] = Field(default_factory=list, description="Preferred brands")
    sort_by: Optional[str] = Field(description="Sort preference: 'price', 'rating', 'popularity'")


class ProductRecommendationQuery(BaseModel):
    """Structured recommendation request"""
    description: str = Field(description="What the user is looking for")
    budget: Optional[float] = Field(description="Budget constraint")
    use_case: Optional[str] = Field(description="How the product will be used")
    must_have_features: List[str] = Field(default_factory=list, description="Essential features")
    preferred_brands: List[str] = Field(default_factory=list, description="Preferred brands")
    exclude_categories: List[str] = Field(default_factory=list, description="Categories to avoid")


class ProductComparisonAnalysis(BaseModel):
    """AI analysis of product comparison"""
    winner_product_title: Optional[str] = Field(description="Title of the recommended product")
    reasoning: str = Field(description="Detailed explanation of the recommendation")
    pros_and_cons: Dict[str, Dict[str, List[str]]] = Field(
        description="Pros and cons for each product"
    )
    value_for_money_ranking: List[str] = Field(
        description="Product titles ranked by value for money"
    )


class ShoppingSuggestion(BaseModel):
    """Shopping suggestion or advice"""
    suggestion_type: str = Field(description="Type of suggestion: 'search', 'price_alert', 'alternative'")
    message: str = Field(description="Suggestion message")
    reasoning: str = Field(description="Why this suggestion is made")


# Create the main shopping agent
shopping_agent = Agent[ShoppingDependencies, Union[ProductSearchQuery, ProductRecommendationQuery, ProductComparisonAnalysis, ShoppingSuggestion]](
    'openai:gpt-4o',
    deps_type=ShoppingDependencies,
    system_prompt=(
        "You are an expert shopping assistant. You help users find products, "
        "compare options, and make informed purchasing decisions. Always provide "
        "detailed, helpful responses based on the user's needs and preferences."
    ),
)


@shopping_agent.tool
async def search_products(
    ctx: RunContext[ShoppingDependencies], 
    query: str, 
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """Search for products based on a query"""
    logger.info(f"Searching for products: {query}")
    
    products = ctx.deps.scraper.search_products(query, max_results)
    
    # Convert to dict for JSON serialization
    product_dicts = []
    for product in products:
        product_dict = {
            "title": product.title,
            "price": product.price,
            "currency": product.currency,
            "url": product.url,
            "rating": product.rating,
            "review_count": product.review_count,
            "description": product.description,
            "features": product.features,
            "brand": product.brand,
            "category": product.category,
            "availability": product.availability,
            "source": product.source
        }
        product_dicts.append(product_dict)
    
    logger.info(f"Found {len(product_dicts)} products")
    return product_dicts


@shopping_agent.tool
async def get_user_preferences(
    ctx: RunContext[ShoppingDependencies]
) -> Optional[Dict[str, Any]]:
    """Get user preferences from database"""
    if not ctx.deps.user_id:
        return None
    
    with SessionLocal() as db:
        prefs = db.query(UserPreferencesDB).filter(
            UserPreferencesDB.user_id == ctx.deps.user_id
        ).first()
        
        if prefs:
            return {
                "preferred_brands": prefs.preferred_brands or [],
                "preferred_categories": prefs.preferred_categories or [],
                "price_range": prefs.price_range,
                "favorite_stores": prefs.favorite_stores or [],
                "preferred_features": prefs.preferred_features or []
            }
    
    return None


@shopping_agent.tool
async def get_product_details(
    ctx: RunContext[ShoppingDependencies], 
    product_url: str
) -> Optional[Dict[str, Any]]:
    """Get detailed information about a specific product"""
    logger.info(f"Getting product details for: {product_url}")
    
    product = ctx.deps.scraper.get_product_details(product_url)
    if not product:
        return None
    
    return {
        "title": product.title,
        "price": product.price,
        "currency": product.currency,
        "url": product.url,
        "rating": product.rating,
        "review_count": product.review_count,
        "description": product.description,
        "features": product.features,
        "brand": product.brand,
        "category": product.category,
        "availability": product.availability,
        "source": product.source
    }


@shopping_agent.tool
async def analyze_product_reviews(
    ctx: RunContext[ShoppingDependencies], 
    product_url: str
) -> Dict[str, Any]:
    """Analyze and summarize product reviews"""
    logger.info(f"Analyzing reviews for: {product_url}")
    
    reviews = ctx.deps.scraper.get_product_reviews(product_url)
    
    if not reviews:
        return {
            "total_reviews": 0,
            "average_rating": 0,
            "pros": [],
            "cons": [],
            "themes": [],
            "summary": "No reviews available for this product."
        }
    
    # Simple analysis (in real implementation, this could use another AI agent)
    avg_rating = sum(r.rating for r in reviews) / len(reviews)
    
    # Categorize reviews
    positive_reviews = [r for r in reviews if r.rating >= 4]
    negative_reviews = [r for r in reviews if r.rating <= 2]
    
    return {
        "total_reviews": len(reviews),
        "average_rating": avg_rating,
        "pros": ["Good quality", "Fast shipping", "Good value"] if positive_reviews else [],
        "cons": ["Some quality issues", "Delivery issues"] if negative_reviews else [],
        "themes": ["Quality", "Value", "Performance"],
        "summary": f"Based on {len(reviews)} reviews with average rating {avg_rating:.1f}/5"
    }


@shopping_agent.tool
async def track_product_price(
    ctx: RunContext[ShoppingDependencies],
    product_url: str,
    target_price: float
) -> Dict[str, Any]:
    """Set up price tracking for a product"""
    if not ctx.deps.user_id:
        return {"error": "User ID required for price tracking"}
    
    logger.info(f"Setting up price tracking for {product_url} at ${target_price}")
    
    # Get product details
    product = ctx.deps.scraper.get_product_details(product_url)
    if not product:
        return {"error": "Could not retrieve product information"}
    
    # Create tracker
    tracker_id = f"tracker_{datetime.now().timestamp()}"
    
    with SessionLocal() as db:
        db_tracker = PriceTrackerDB(
            id=tracker_id,
            user_id=ctx.deps.user_id,
            product_url=product_url,
            product_title=product.title,
            target_price=target_price,
            current_price=product.price
        )
        db.add(db_tracker)
        db.commit()
    
    return {
        "tracker_id": tracker_id,
        "product_title": product.title,
        "current_price": product.price,
        "target_price": target_price,
        "status": "active"
    }


class PydanticShoppingAssistant:
    """Pydantic AI-powered shopping assistant"""
    
    def __init__(self):
        self.scraper = ProductScraper()
        logger.info("PydanticShoppingAssistant initialized")
    
    async def parse_search_query(self, query: str, user_id: Optional[str] = None) -> ProductSearchQuery:
        """Parse natural language search query into structured format"""
        logger.info(f"Parsing search query: {query}")
        
        deps = ShoppingDependencies(scraper=self.scraper, user_id=user_id)
        
        # Use a specialized prompt for query parsing
        prompt = f"""
        Parse this shopping search query into structured components:
        "{query}"
        
        Extract the following information:
        - Product category (e.g., 'headphones', 'laptop', 'shoes', 'gaming laptop')
        - Price constraints (look for "under $X", "below $X", "over $X", "less than $X", "more than $X")
        - Required features (e.g., wireless, waterproof, gaming, RGB, etc.)
        - Brand preferences (e.g., Apple, Samsung, Sony, etc.)
        - Sort preferences (price, rating, popularity)
        
        Important: 
        - If the query contains words like "gaming", "wireless", "waterproof", etc., these should be extracted as features
        - Be generous in extracting features from descriptive terms
        - If no specific constraints are mentioned, leave them as None/empty
        
        Return a ProductSearchQuery object with all extracted information.
        """
        
        # Create a specialized agent for query parsing
        query_parser = Agent[ShoppingDependencies, ProductSearchQuery](
            'openai:gpt-4o',
            deps_type=ShoppingDependencies,
            output_type=ProductSearchQuery,
            system_prompt="You are a search query parser. Extract structured information from natural language shopping queries."
        )
        
        result = await query_parser.run(prompt, deps=deps)
        return result.output
    
    async def search_products(self, query: str, user_id: Optional[str] = None, max_results: int = 10) -> SearchResult:
        """Search for products using AI-enhanced query parsing"""
        logger.info(f"Searching products for: {query}")
        
        # Parse the query first
        parsed_query = await self.parse_search_query(query, user_id)
        logger.info(f"Parsed query: {parsed_query}")
        
        # Search products
        deps = ShoppingDependencies(scraper=self.scraper, user_id=user_id)
        
        prompt = f"""
        Search for products based on this request: "{query}"
        
        Parsed requirements:
        - Category: {parsed_query.category}
        - Price range: ${parsed_query.price_min or 0} - ${parsed_query.price_max or 'unlimited'}
        - Required features: {', '.join(parsed_query.features) if parsed_query.features else 'None'}
        - Preferred brands: {', '.join(parsed_query.brands) if parsed_query.brands else 'Any'}
        
        Use the search_products tool to find relevant products.
        """
        
        result = await shopping_agent.run(prompt, deps=deps)
        
        # The agent will use tools to search, so we need to extract the actual products
        # For now, let's do a direct search
        products = self.scraper.search_products(query, max_results)
        
        # Apply filters based on parsed query
        filtered_products = self._apply_filters(products, parsed_query)
        
        return SearchResult(
            query=query,
            products=filtered_products[:max_results],
            total_found=len(filtered_products),
            search_time=0.1,  # Placeholder
            suggestions=self._generate_suggestions(query, filtered_products)
        )
    
    async def get_recommendations(self, description: str, user_id: Optional[str] = None, **kwargs) -> SearchResult:
        """Get AI-powered product recommendations"""
        logger.info(f"Getting recommendations for: {description}")
        
        deps = ShoppingDependencies(scraper=self.scraper, user_id=user_id)
        
        # Create recommendation request
        prompt = f"""
        Provide product recommendations based on this request: "{description}"
        
        Additional parameters:
        - Budget: {kwargs.get('budget', 'No specific budget')}
        - Preferred brands: {kwargs.get('preferred_brands', 'Any')}
        - Must-have features: {kwargs.get('must_have_features', 'None')}
        
        Use the search_products and get_user_preferences tools to find the best recommendations.
        Consider the user's preferences and provide detailed reasoning for each recommendation.
        """
        
        # For now, use the enhanced query and search
        enhanced_query = f"{description}"
        if kwargs.get('budget'):
            enhanced_query += f" under ${kwargs['budget']}"
        if kwargs.get('preferred_brands'):
            enhanced_query += f" from {' or '.join(kwargs['preferred_brands'])}"
        
        products = self.scraper.search_products(enhanced_query, 10)
        
        # Re-rank based on preferences
        ranked_products = self._rank_recommendations(products, kwargs)
        
        return SearchResult(
            query=description,
            products=ranked_products,
            total_found=len(ranked_products),
            search_time=0.1,
            suggestions=[]
        )
    
    async def compare_products(self, product_urls: List[str]) -> ComparisonResult:
        """Compare multiple products using AI analysis"""
        logger.info(f"Comparing {len(product_urls)} products")
        
        deps = ShoppingDependencies(scraper=self.scraper)
        
        # Get product details
        products = []
        for url in product_urls:
            product = self.scraper.get_product_details(url)
            if product:
                products.append(product)
        
        if not products:
            raise ValueError("No valid products found for comparison")
        
        # Create comparison prompt
        product_info = []
        for i, product in enumerate(products, 1):
            product_info.append(f"""
            Product {i}: {product.title}
            - Price: ${product.price}
            - Rating: {product.rating}/5 ({product.review_count} reviews)
            - Brand: {product.brand}
            - Features: {', '.join(product.features) if product.features else 'None listed'}
            """)
        
        prompt = f"""
        Compare these products and determine which is the best choice:
        
        {chr(10).join(product_info)}
        
        Consider:
        1. Value for money (price vs features)
        2. User ratings and reviews
        3. Feature completeness
        4. Brand reputation
        
        Provide a detailed analysis including the winner and reasoning.
        """
        
        # Create comparison agent
        comparison_agent = Agent[ShoppingDependencies, ProductComparisonAnalysis](
            'openai:gpt-4o',
            deps_type=ShoppingDependencies,
            output_type=ProductComparisonAnalysis,
            system_prompt="You are a product comparison expert. Analyze products objectively and provide detailed recommendations."
        )
        
        result = await comparison_agent.run(prompt, deps=deps)
        analysis = result.output
        
        # Create comparison table
        comparison_table = {}
        for criterion in ["price", "rating", "features"]:
            comparison_table[criterion] = {}
            for product in products:
                if criterion == "price":
                    comparison_table[criterion][product.title] = product.price
                elif criterion == "rating":
                    comparison_table[criterion][product.title] = product.rating
                elif criterion == "features":
                    comparison_table[criterion][product.title] = product.features
        
        return ComparisonResult(
            products=products,
            comparison_table=comparison_table,
            winner=analysis.winner_product_title,
            summary=analysis.reasoning
        )
    
    def _apply_filters(self, products: List[Product], query: ProductSearchQuery) -> List[Product]:
        """Apply filters based on parsed query"""
        logger.info(f"Applying filters to {len(products)} products")
        logger.info(f"Query filters - price_min: {query.price_min}, price_max: {query.price_max}, brands: {query.brands}, features: {query.features}")
        
        filtered = products
        
        if query.price_min:
            before_count = len(filtered)
            filtered = [p for p in filtered if p.price and p.price >= query.price_min]
            logger.info(f"Price min filter: {before_count} -> {len(filtered)} products")
        
        if query.price_max:
            before_count = len(filtered)
            filtered = [p for p in filtered if p.price and p.price <= query.price_max]
            logger.info(f"Price max filter: {before_count} -> {len(filtered)} products")
        
        if query.brands:
            before_count = len(filtered)
            filtered = [p for p in filtered if p.brand and p.brand.lower() in [b.lower() for b in query.brands]]
            logger.info(f"Brand filter: {before_count} -> {len(filtered)} products")
        
        # More lenient feature filtering - check title, description, and features
        if query.features:
            before_count = len(filtered)
            feature_filtered = []
            for product in filtered:
                has_feature = False
                
                # Check if any required feature appears in title, description, or features
                for feature in query.features:
                    feature_lower = feature.lower()
                    
                    # Check title
                    if product.title and feature_lower in product.title.lower():
                        has_feature = True
                        logger.debug(f"Feature '{feature}' found in title: {product.title}")
                        break
                    
                    # Check description  
                    if product.description and feature_lower in product.description.lower():
                        has_feature = True
                        logger.debug(f"Feature '{feature}' found in description")
                        break
                    
                    # Check explicit features list
                    if product.features and any(feature_lower in pf.lower() for pf in product.features):
                        has_feature = True
                        logger.debug(f"Feature '{feature}' found in features list")
                        break
                
                # If no explicit features required, or if feature found, include the product
                if not query.features or has_feature:
                    feature_filtered.append(product)
            
            filtered = feature_filtered
            logger.info(f"Feature filter: {before_count} -> {len(filtered)} products")
        
        logger.info(f"Final filtered result: {len(filtered)} products")
        return filtered
    
    def _rank_recommendations(self, products: List[Product], criteria: Dict[str, Any]) -> List[Product]:
        """Rank products based on recommendation criteria"""
        scored_products = []
        
        for product in products:
            score = 0
            
            # Budget compliance
            if criteria.get('budget') and product.price:
                if product.price <= criteria['budget']:
                    score += 10
                else:
                    score -= 5
            
            # Brand preference
            if criteria.get('preferred_brands') and product.brand:
                if product.brand.lower() in [b.lower() for b in criteria['preferred_brands']]:
                    score += 8
            
            # Rating bonus
            if product.rating:
                score += product.rating * 2
            
            # Must-have features
            if criteria.get('must_have_features') and product.features:
                feature_matches = sum(1 for feature in criteria['must_have_features']
                                    if any(feature.lower() in pf.lower() for pf in product.features))
                score += feature_matches * 5
            
            scored_products.append((score, product))
        
        # Sort by score descending
        scored_products.sort(key=lambda x: x[0], reverse=True)
        return [product for score, product in scored_products]
    
    def _generate_suggestions(self, query: str, products: List[Product]) -> List[str]:
        """Generate search suggestions"""
        suggestions = []
        
        # Category suggestions
        categories = set(p.category for p in products if p.category)
        for category in list(categories)[:2]:
            suggestions.append(f"More {category} options")
        
        # Brand suggestions
        brands = set(p.brand for p in products if p.brand)
        for brand in list(brands)[:2]:
            suggestions.append(f"{brand} products")
        
        return suggestions 