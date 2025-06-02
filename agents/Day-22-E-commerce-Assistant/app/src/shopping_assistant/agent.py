"""
Main Shopping Assistant Agent
"""

import re
import time
import uuid
from typing import List, Optional, Dict, Any
from openai import OpenAI
from .models import (
    Product, SearchQuery, SearchResult, ComparisonRequest, ComparisonResult,
    RecommendationRequest, ReviewSummary, QueryType, UserPreferences, PriceTracker
)
from .scrapers import ProductScraper
from .llm_service import LLMService
from .database import SessionLocal, UserPreferencesDB, PriceTrackerDB, SearchHistoryDB
import os
import logging

logger = logging.getLogger(__name__)


class ShoppingAssistant:
    """Main shopping assistant agent"""
    
    def __init__(self):
        self.scraper = ProductScraper()
        self.llm = LLMService()
        
    def parse_query(self, query: str, user_id: Optional[str] = None) -> SearchQuery:
        """Parse natural language query into structured search"""
        logger.info(f"Parsing query: {query}")
        
        # Use LLM to understand the intent and extract parameters
        prompt = f"""
        Parse this shopping query and extract the following information:
        Query: "{query}"
        
        Extract:
        1. Query type: "search", "compare", "recommend", "track", or "summarize"
        2. Product category: What type of product (e.g., "headphones", "laptop", "shoes")
        3. Price constraints: Look for phrases like "under $X", "below $X", "less than $X" (price_max) or "over $X", "above $X", "more than $X" (price_min)
        4. Required features: Specific features mentioned (e.g., "wireless", "noise cancelling", "waterproof")
        5. Brand preferences: Specific brands mentioned
        6. Sort preference: "price", "rating", "popularity", or null
        
        Examples:
        - "wireless headphones under $200" → price_max: 200
        - "gaming laptop over $1000" → price_min: 1000
        - "Nike running shoes" → brands: ["Nike"]
        
        Return as JSON with keys: query_type, category, price_min, price_max, features, brands, sort_by
        Make sure to extract numeric values from price phrases.
        """
        
        parsed = self.llm.parse_query(prompt)
        logger.info(f"LLM parsing result: {parsed}")
        
        # Start with LLM results if available, otherwise use basic parsing
        if parsed and self.llm._is_available():
            logger.info("Using AI-enhanced query parsing")
            
            # Extract query type from LLM or fallback to keyword detection
            query_type = QueryType.SEARCH
            if parsed.get('query_type'):
                try:
                    query_type = QueryType(parsed['query_type'].lower())
                except ValueError:
                    # Fallback to keyword detection
                    if any(word in query.lower() for word in ['compare', 'vs', 'versus']):
                        query_type = QueryType.COMPARE
                    elif any(word in query.lower() for word in ['recommend', 'suggest', 'best']):
                        query_type = QueryType.RECOMMEND
                    elif any(word in query.lower() for word in ['track', 'alert', 'notify']):
                        query_type = QueryType.TRACK
                    elif any(word in query.lower() for word in ['review', 'summarize']):
                        query_type = QueryType.SUMMARIZE
            
            # Build filters from LLM results
            filters = {}
            if parsed.get('price_min'):
                filters['min_price'] = float(parsed['price_min'])
            if parsed.get('price_max'):
                filters['max_price'] = float(parsed['price_max'])
            if parsed.get('brands'):
                filters['brands'] = parsed['brands'] if isinstance(parsed['brands'], list) else [parsed['brands']]
            if parsed.get('features'):
                filters['features'] = parsed['features'] if isinstance(parsed['features'], list) else [parsed['features']]
            
            # Extract sort preference from LLM
            sort_by = parsed.get('sort_by', 'relevance')
            if sort_by == 'relevance':
                sort_by = None
                
        else:
            logger.info("Using basic regex-based query parsing")
            
            # Fallback to basic parsing
            # Extract query type
            query_type = QueryType.SEARCH
            if any(word in query.lower() for word in ['compare', 'vs', 'versus']):
                query_type = QueryType.COMPARE
            elif any(word in query.lower() for word in ['recommend', 'suggest', 'best']):
                query_type = QueryType.RECOMMEND
            elif any(word in query.lower() for word in ['track', 'alert', 'notify']):
                query_type = QueryType.TRACK
            elif any(word in query.lower() for word in ['review', 'summarize']):
                query_type = QueryType.SUMMARIZE
            
            # Extract price constraints
            price_pattern = r'\$?(\d+(?:\.\d{2})?)'
            prices = re.findall(price_pattern, query)
            
            filters = {}
            if prices:
                if 'under' in query.lower() or 'below' in query.lower():
                    filters['max_price'] = float(prices[0])
                elif 'over' in query.lower() or 'above' in query.lower():
                    filters['min_price'] = float(prices[0])
            
            # Extract sort preference
            sort_by = None
            if 'cheapest' in query.lower() or 'price' in query.lower():
                sort_by = 'price'
            elif 'best rated' in query.lower() or 'rating' in query.lower():
                sort_by = 'rating'
        
        search_query = SearchQuery(
            query=query,
            query_type=query_type,
            filters=filters,
            sort_by=sort_by,
            user_id=user_id
        )
        
        logger.info(f"Final parsed search query: query_type={query_type}, filters={filters}, sort_by={sort_by}")
        return search_query
    
    def search_products(self, search_query: SearchQuery) -> SearchResult:
        """Search for products based on query"""
        start_time = time.time()
        
        # Get products from multiple sources
        products = []
        
        # Search using web scraping
        scraped_products = self.scraper.search_products(
            search_query.query,
            max_results=search_query.max_results
        )
        products.extend(scraped_products)
        
        # Apply filters
        filtered_products = self._apply_filters(products, search_query.filters)
        
        # Sort results
        if search_query.sort_by:
            filtered_products = self._sort_products(filtered_products, search_query.sort_by, search_query.sort_order)
        
        # Limit results
        limited_products = filtered_products[:search_query.max_results]
        
        search_time = time.time() - start_time
        
        # Save search history
        self._save_search_history(search_query, len(limited_products))
        
        # Generate suggestions
        suggestions = self._generate_suggestions(search_query.query, limited_products)
        
        return SearchResult(
            query=search_query.query,
            products=limited_products,
            total_found=len(filtered_products),
            search_time=search_time,
            suggestions=suggestions
        )
    
    def compare_products(self, request: ComparisonRequest) -> ComparisonResult:
        """Compare multiple products"""
        products = []
        
        # Get detailed info for each product
        for url in request.product_urls:
            product = self.scraper.get_product_details(url)
            if product:
                products.append(product)
        
        if not products:
            raise ValueError("No valid products found for comparison")
        
        # Create comparison table
        comparison_table = {}
        for criterion in request.comparison_criteria:
            comparison_table[criterion] = {}
            for product in products:
                if criterion == "price":
                    comparison_table[criterion][product.id or product.title] = product.price
                elif criterion == "rating":
                    comparison_table[criterion][product.id or product.title] = product.rating
                elif criterion == "features":
                    comparison_table[criterion][product.id or product.title] = product.features
                # Add more criteria as needed
        
        # Use LLM to determine winner and generate summary
        winner, summary = self.llm.analyze_comparison(products, comparison_table)
        
        return ComparisonResult(
            products=products,
            comparison_table=comparison_table,
            winner=winner,
            summary=summary
        )
    
    def get_recommendations(self, request: RecommendationRequest) -> SearchResult:
        """Get personalized product recommendations"""
        # Get user preferences if user_id provided
        user_prefs = None
        if request.user_id:
            user_prefs = self._get_user_preferences(request.user_id)
        
        # Build enhanced search query using LLM
        enhanced_query = self.llm.enhance_recommendation_query(request, user_prefs)
        
        # Search for products
        search_query = SearchQuery(
            query=enhanced_query,
            query_type=QueryType.RECOMMEND,
            user_id=request.user_id,
            max_results=10
        )
        
        results = self.search_products(search_query)
        
        # Re-rank results based on user preferences and requirements
        if user_prefs or request.preferred_brands or request.must_have_features:
            results.products = self._rerank_recommendations(
                results.products, request, user_prefs
            )
        
        return results
    
    def track_price(self, user_id: str, product_url: str, target_price: float) -> PriceTracker:
        """Set up price tracking for a product"""
        # Get product details
        product = self.scraper.get_product_details(product_url)
        if not product:
            raise ValueError("Could not retrieve product information")
        
        # Create price tracker
        tracker = PriceTracker(
            id=str(uuid.uuid4()),
            user_id=user_id,
            product_url=product_url,
            product_title=product.title,
            target_price=target_price,
            current_price=product.price
        )
        
        # Save to database
        with SessionLocal() as db:
            db_tracker = PriceTrackerDB(
                id=tracker.id,
                user_id=tracker.user_id,
                product_url=tracker.product_url,
                product_title=tracker.product_title,
                target_price=tracker.target_price,
                current_price=tracker.current_price
            )
            db.add(db_tracker)
            db.commit()
        
        return tracker
    
    def summarize_reviews(self, product_url: str) -> ReviewSummary:
        """Summarize product reviews"""
        # Get product and reviews
        product = self.scraper.get_product_details(product_url)
        reviews = self.scraper.get_product_reviews(product_url)
        
        if not reviews:
            return ReviewSummary(
                product_id=product.id or product_url,
                overall_rating=product.rating or 0,
                total_reviews=0,
                summary="No reviews available for this product."
            )
        
        # Use LLM to summarize reviews
        summary = self.llm.summarize_reviews(reviews)
        
        return ReviewSummary(
            product_id=product.id or product_url,
            overall_rating=product.rating or 0,
            total_reviews=len(reviews),
            pros=summary.get('pros', []),
            cons=summary.get('cons', []),
            common_themes=summary.get('themes', []),
            summary=summary.get('summary', '')
        )
    
    def _apply_filters(self, products: List[Product], filters: Dict[str, Any]) -> List[Product]:
        """Apply filters to product list"""
        filtered = products
        
        if 'min_price' in filters:
            filtered = [p for p in filtered if p.price and p.price >= filters['min_price']]
        
        if 'max_price' in filters:
            filtered = [p for p in filtered if p.price and p.price <= filters['max_price']]
        
        if 'min_rating' in filters:
            filtered = [p for p in filtered if p.rating and p.rating >= filters['min_rating']]
        
        if 'brand' in filters:
            filtered = [p for p in filtered if p.brand and p.brand.lower() == filters['brand'].lower()]
        
        return filtered
    
    def _sort_products(self, products: List[Product], sort_by: str, sort_order: str = "asc") -> List[Product]:
        """Sort products by specified criteria"""
        reverse = sort_order == "desc"
        
        if sort_by == "price":
            return sorted(products, key=lambda p: p.price or float('inf'), reverse=reverse)
        elif sort_by == "rating":
            return sorted(products, key=lambda p: p.rating or 0, reverse=not reverse)  # Higher rating first
        elif sort_by == "review_count":
            return sorted(products, key=lambda p: p.review_count or 0, reverse=not reverse)
        
        return products
    
    def _generate_suggestions(self, query: str, products: List[Product]) -> List[str]:
        """Generate search suggestions based on results"""
        suggestions = []
        
        # Add category-based suggestions
        categories = set(p.category for p in products if p.category)
        for category in list(categories)[:3]:
            suggestions.append(f"{query} in {category}")
        
        # Add brand-based suggestions  
        brands = set(p.brand for p in products if p.brand)
        for brand in list(brands)[:2]:
            suggestions.append(f"{brand} {query}")
        
        return suggestions
    
    def _save_search_history(self, search_query: SearchQuery, result_count: int):
        """Save search to history"""
        with SessionLocal() as db:
            history = SearchHistoryDB(
                id=str(uuid.uuid4()),
                user_id=search_query.user_id,
                query=search_query.query,
                query_type=search_query.query_type.value,
                filters=search_query.filters,
                results_count=result_count
            )
            db.add(history)
            db.commit()
    
    def _get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences from database"""
        with SessionLocal() as db:
            prefs = db.query(UserPreferencesDB).filter(UserPreferencesDB.user_id == user_id).first()
            if prefs:
                return UserPreferences(
                    user_id=prefs.user_id,
                    preferred_brands=prefs.preferred_brands or [],
                    preferred_categories=prefs.preferred_categories or [],
                    price_range=prefs.price_range,
                    favorite_stores=prefs.favorite_stores or [],
                    preferred_features=prefs.preferred_features or []
                )
        return None
    
    def _rerank_recommendations(self, products: List[Product], request: RecommendationRequest, 
                              user_prefs: Optional[UserPreferences]) -> List[Product]:
        """Re-rank recommendations based on user preferences"""
        # Simple scoring system - could be enhanced with ML
        scored_products = []
        
        for product in products:
            score = 0
            
            # Brand preference bonus
            if request.preferred_brands and product.brand:
                if product.brand.lower() in [b.lower() for b in request.preferred_brands]:
                    score += 10
            
            if user_prefs and user_prefs.preferred_brands and product.brand:
                if product.brand.lower() in [b.lower() for b in user_prefs.preferred_brands]:
                    score += 5
            
            # Budget compliance
            if request.budget and product.price:
                if product.price <= request.budget:
                    score += 5
                else:
                    score -= 10  # Penalty for over budget
            
            # Must-have features
            if request.must_have_features and product.features:
                feature_matches = sum(1 for feature in request.must_have_features 
                                    if any(feature.lower() in pf.lower() for pf in product.features))
                score += feature_matches * 3
            
            # Rating bonus
            if product.rating:
                score += product.rating * 2
            
            scored_products.append((score, product))
        
        # Sort by score (descending)
        scored_products.sort(key=lambda x: x[0], reverse=True)
        
        return [product for score, product in scored_products] 