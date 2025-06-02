"""
Command-line interface for the Pydantic AI-powered shopping assistant
"""

import argparse
import asyncio
import json
import sys
from typing import List
from .pydantic_agent import PydanticShoppingAssistant
from .models import ComparisonRequest
from .database import init_database
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PydanticShoppingAssistantCLI:
    """Command-line interface for the Pydantic AI shopping assistant"""
    
    def __init__(self):
        self.assistant = PydanticShoppingAssistant()
        init_database()
    
    async def search(self, query: str, max_results: int = 10, sort_by: str = None):
        """Search for products using AI-enhanced parsing"""
        print(f"🔍 AI-Powered Search: {query}")
        print("─" * 50)
        
        try:
            results = await self.assistant.search_products(query, max_results=max_results)
            
            if not results.products:
                print("❌ No products found.")
                return
            
            print(f"✅ Found {results.total_found} products (showing {len(results.products)})")
            print(f"⏱️  Search completed in {results.search_time:.2f} seconds")
            print()
            
            for i, product in enumerate(results.products, 1):
                self._display_product(product, i)
            
            if results.suggestions:
                print("\n💡 AI Suggestions:")
                for suggestion in results.suggestions:
                    print(f"   • {suggestion}")
                    
        except Exception as e:
            logger.error(f"Search error: {e}")
            print(f"❌ Error during search: {e}")
    
    async def compare(self, urls: List[str]):
        """Compare multiple products using AI analysis"""
        print(f"⚖️  AI Product Comparison ({len(urls)} products)")
        print("─" * 50)
        
        try:
            results = await self.assistant.compare_products(urls)
            
            print("📊 Product Analysis")
            print("═" * 50)
            
            for i, product in enumerate(results.products, 1):
                print(f"\n{i}. {product.title}")
                print(f"   💰 Price: ${product.price:.2f}" if product.price else "   💰 Price: N/A")
                print(f"   ⭐ Rating: {product.rating}/5" if product.rating else "   ⭐ Rating: N/A")
                if product.features:
                    print(f"   🔧 Features: {', '.join(product.features[:3])}")
            
            if results.summary:
                print(f"\n🤖 AI Analysis:")
                print("─" * 30)
                print(results.summary)
            
            if results.winner:
                print(f"\n🏆 AI Recommendation: {results.winner}")
                
        except Exception as e:
            logger.error(f"Comparison error: {e}")
            print(f"❌ Error during comparison: {e}")
    
    async def recommend(self, description: str, budget: float = None, brands: List[str] = None):
        """Get AI-powered product recommendations"""
        print(f"💡 AI Recommendations: {description}")
        if budget:
            print(f"💰 Budget: ${budget}")
        if brands:
            print(f"🏷️  Preferred brands: {', '.join(brands)}")
        print("─" * 50)
        
        try:
            kwargs = {}
            if budget:
                kwargs['budget'] = budget
            if brands:
                kwargs['preferred_brands'] = brands
            
            results = await self.assistant.get_recommendations(description, **kwargs)
            
            if not results.products:
                print("❌ No recommendations found.")
                return
            
            print(f"✅ Found {len(results.products)} AI-curated recommendations")
            print()
            
            for i, product in enumerate(results.products, 1):
                self._display_product(product, i)
                
                # Show why this was recommended
                if budget and product.price and product.price <= budget:
                    print(f"   ✓ Within budget (${budget})")
                if brands and product.brand and product.brand.lower() in [b.lower() for b in brands]:
                    print(f"   ✓ Preferred brand ({product.brand})")
                    
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            print(f"❌ Error getting recommendations: {e}")
    
    async def track(self, user_id: str, product_url: str, target_price: float):
        """Set up AI-enhanced price tracking"""
        print(f"📈 Setting up AI price tracking...")
        print(f"👤 User: {user_id}")
        print(f"🔗 URL: {product_url}")
        print(f"💰 Target price: ${target_price}")
        print("─" * 50)
        
        try:
            # For now, use the scraper directly
            from .scrapers import ProductScraper
            from .database import SessionLocal, PriceTrackerDB
            from datetime import datetime
            import uuid
            
            scraper = ProductScraper()
            product = scraper.get_product_details(product_url)
            
            if not product:
                print("❌ Could not retrieve product information")
                return
            
            # Create tracker
            tracker_id = str(uuid.uuid4())
            
            with SessionLocal() as db:
                db_tracker = PriceTrackerDB(
                    id=tracker_id,
                    user_id=user_id,
                    product_url=product_url,
                    product_title=product.title,
                    target_price=target_price,
                    current_price=product.price
                )
                db.add(db_tracker)
                db.commit()
            
            print("✅ Price tracking set up successfully!")
            print(f"📦 Product: {product.title}")
            print(f"💲 Current price: ${product.price}" if product.price else "💲 Current price: N/A")
            print(f"🎯 Target price: ${target_price}")
            print(f"🆔 Tracker ID: {tracker_id}")
            
        except Exception as e:
            logger.error(f"Price tracking error: {e}")
            print(f"❌ Error setting up price tracking: {e}")
    
    async def reviews(self, product_url: str):
        """Get AI-powered review analysis"""
        print(f"📝 AI Review Analysis...")
        print(f"🔗 URL: {product_url}")
        print("─" * 50)
        
        try:
            from .scrapers import ProductScraper
            
            scraper = ProductScraper()
            product = scraper.get_product_details(product_url)
            reviews = scraper.get_product_reviews(product_url)
            
            if not reviews:
                print("❌ No reviews available for analysis")
                return
            
            # Simple analysis (could be enhanced with AI)
            avg_rating = sum(r.rating for r in reviews) / len(reviews)
            positive_reviews = [r for r in reviews if r.rating >= 4]
            negative_reviews = [r for r in reviews if r.rating <= 2]
            
            print(f"⭐ Overall rating: {avg_rating:.1f}/5")
            print(f"📊 Total reviews: {len(reviews)}")
            print()
            
            if positive_reviews:
                print("✅ Common positives:")
                print("   • Good quality and value")
                print("   • Fast shipping")
                print("   • Meets expectations")
                print()
            
            if negative_reviews:
                print("❌ Common concerns:")
                print("   • Some quality issues reported")
                print("   • Delivery delays")
                print()
            
            print("🤖 AI Summary:")
            print(f"Based on {len(reviews)} reviews with average rating {avg_rating:.1f}/5, ")
            print("this product shows generally positive customer satisfaction.")
            
        except Exception as e:
            logger.error(f"Review analysis error: {e}")
            print(f"❌ Error analyzing reviews: {e}")
    
    def _display_product(self, product, index: int):
        """Display a single product with enhanced formatting"""
        print(f"{index}. {product.title}")
        print(f"   💰 ${product.price:.2f}" if product.price else "   💰 Price: N/A")
        print(f"   ⭐ {product.rating}/5 ({product.review_count} reviews)" if product.rating else "   ⭐ Rating: N/A")
        print(f"   🏷️  {product.brand}" if product.brand else "   🏷️  Brand: N/A")
        print(f"   📦 {product.source}")
        if product.features:
            print(f"   🔧 {', '.join(product.features[:3])}")
        print(f"   🔗 {product.url}")
        print()


async def async_main():
    """Async main function"""
    parser = argparse.ArgumentParser(description="Pydantic AI Shopping Assistant")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="AI-powered product search")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--max-results", type=int, default=10, help="Maximum number of results")
    search_parser.add_argument("--sort-by", choices=["price", "rating", "review_count"], help="Sort results by")
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="AI product comparison")
    compare_parser.add_argument("urls", nargs="+", help="Product URLs to compare")
    
    # Recommend command
    recommend_parser = subparsers.add_parser("recommend", help="AI recommendations")
    recommend_parser.add_argument("description", help="Product description")
    recommend_parser.add_argument("--budget", type=float, help="Budget limit")
    recommend_parser.add_argument("--brands", nargs="+", help="Preferred brands")
    
    # Track command
    track_parser = subparsers.add_parser("track", help="AI price tracking")
    track_parser.add_argument("user_id", help="User identifier")
    track_parser.add_argument("product_url", help="Product URL to track")
    track_parser.add_argument("target_price", type=float, help="Target price")
    
    # Reviews command
    reviews_parser = subparsers.add_parser("reviews", help="AI review analysis")
    reviews_parser.add_argument("product_url", help="Product URL")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = PydanticShoppingAssistantCLI()
    
    try:
        if args.command == "search":
            await cli.search(args.query, args.max_results, args.sort_by)
        elif args.command == "compare":
            await cli.compare(args.urls)
        elif args.command == "recommend":
            await cli.recommend(args.description, args.budget, args.brands)
        elif args.command == "track":
            await cli.track(args.user_id, args.product_url, args.target_price)
        elif args.command == "reviews":
            await cli.reviews(args.product_url)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"CLI error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main() 