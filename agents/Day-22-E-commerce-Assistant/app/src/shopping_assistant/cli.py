"""
Command-line interface for the shopping assistant
"""

import argparse
import json
import sys
from typing import List
from .agent import ShoppingAssistant
from .models import SearchQuery, ComparisonRequest, RecommendationRequest, QueryType
from .database import init_database


class ShoppingAssistantCLI:
    """Command-line interface for the shopping assistant"""
    
    def __init__(self):
        self.assistant = ShoppingAssistant()
        init_database()
    
    def search(self, query: str, max_results: int = 10, sort_by: str = None):
        """Search for products"""
        print(f"🔍 Searching for: {query}")
        print("─" * 50)
        
        # Use the agent's parse_query method to get AI-enhanced parsing
        search_query = self.assistant.parse_query(query)
        
        # Override with CLI-specific parameters
        search_query.max_results = max_results
        if sort_by:
            search_query.sort_by = sort_by
        
        results = self.assistant.search_products(search_query)
        
        if not results.products:
            print("❌ No products found.")
            return
        
        print(f"✅ Found {results.total_found} products (showing {len(results.products)})")
        print(f"⏱️  Search completed in {results.search_time:.2f} seconds")
        print()
        
        for i, product in enumerate(results.products, 1):
            self._display_product(product, i)
        
        if results.suggestions:
            print("\n💡 Related searches:")
            for suggestion in results.suggestions:
                print(f"   • {suggestion}")
    
    def compare(self, urls: List[str]):
        """Compare multiple products"""
        print(f"⚖️  Comparing {len(urls)} products...")
        print("─" * 50)
        
        request = ComparisonRequest(product_urls=urls)
        results = self.assistant.compare_products(request)
        
        print("📊 Product Comparison")
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
            print(f"\n🏆 Recommended: {results.winner}")
    
    def recommend(self, description: str, budget: float = None, brands: List[str] = None):
        """Get product recommendations"""
        print(f"💡 Getting recommendations for: {description}")
        if budget:
            print(f"💰 Budget: ${budget}")
        if brands:
            print(f"🏷️  Preferred brands: {', '.join(brands)}")
        print("─" * 50)
        
        request = RecommendationRequest(
            description=description,
            budget=budget,
            preferred_brands=brands or []
        )
        
        results = self.assistant.get_recommendations(request)
        
        if not results.products:
            print("❌ No recommendations found.")
            return
        
        print(f"✅ Found {len(results.products)} recommendations")
        print()
        
        for i, product in enumerate(results.products, 1):
            self._display_product(product, i)
            
            # Show why this was recommended
            if budget and product.price and product.price <= budget:
                print(f"   ✓ Within budget (${budget})")
            if brands and product.brand and product.brand.lower() in [b.lower() for b in brands]:
                print(f"   ✓ Preferred brand ({product.brand})")
    
    def track(self, user_id: str, product_url: str, target_price: float):
        """Set up price tracking"""
        print(f"📈 Setting up price tracking...")
        print(f"👤 User: {user_id}")
        print(f"🔗 URL: {product_url}")
        print(f"💰 Target price: ${target_price}")
        print("─" * 50)
        
        try:
            tracker = self.assistant.track_price(user_id, product_url, target_price)
            print("✅ Price tracking set up successfully!")
            print(f"📦 Product: {tracker.product_title}")
            print(f"💲 Current price: ${tracker.current_price}" if tracker.current_price else "💲 Current price: N/A")
            print(f"🎯 Target price: ${tracker.target_price}")
            print(f"🆔 Tracker ID: {tracker.id}")
        except Exception as e:
            print(f"❌ Error setting up price tracking: {e}")
    
    def reviews(self, product_url: str):
        """Get review summary for a product"""
        print(f"📝 Analyzing reviews for product...")
        print(f"🔗 URL: {product_url}")
        print("─" * 50)
        
        try:
            summary = self.assistant.summarize_reviews(product_url)
            
            print(f"⭐ Overall rating: {summary.overall_rating}/5")
            print(f"📊 Total reviews: {summary.total_reviews}")
            print()
            
            if summary.pros:
                print("✅ Pros:")
                for pro in summary.pros:
                    print(f"   • {pro}")
                print()
            
            if summary.cons:
                print("❌ Cons:")
                for con in summary.cons:
                    print(f"   • {con}")
                print()
            
            if summary.common_themes:
                print("🔍 Common themes:")
                for theme in summary.common_themes:
                    print(f"   • {theme}")
                print()
            
            print("📝 Summary:")
            print(summary.summary)
            
        except Exception as e:
            print(f"❌ Error analyzing reviews: {e}")
    
    def _display_product(self, product, index: int):
        """Display a single product"""
        print(f"{index}. {product.title}")
        print(f"   💰 ${product.price:.2f}" if product.price else "   💰 Price: N/A")
        print(f"   ⭐ {product.rating}/5 ({product.review_count} reviews)" if product.rating else "   ⭐ Rating: N/A")
        print(f"   🏷️  {product.brand}" if product.brand else "   🏷️  Brand: N/A")
        print(f"   📦 {product.source}")
        if product.features:
            print(f"   🔧 {', '.join(product.features[:3])}")
        print(f"   🔗 {product.url}")
        print()


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="AI Shopping Assistant")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for products")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--max-results", type=int, default=10, help="Maximum number of results")
    search_parser.add_argument("--sort-by", choices=["price", "rating", "review_count"], help="Sort results by")
    
    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare products")
    compare_parser.add_argument("urls", nargs="+", help="Product URLs to compare")
    
    # Recommend command
    recommend_parser = subparsers.add_parser("recommend", help="Get recommendations")
    recommend_parser.add_argument("description", help="Product description")
    recommend_parser.add_argument("--budget", type=float, help="Budget limit")
    recommend_parser.add_argument("--brands", nargs="+", help="Preferred brands")
    
    # Track command
    track_parser = subparsers.add_parser("track", help="Track product price")
    track_parser.add_argument("user_id", help="User identifier")
    track_parser.add_argument("product_url", help="Product URL to track")
    track_parser.add_argument("target_price", type=float, help="Target price")
    
    # Reviews command
    reviews_parser = subparsers.add_parser("reviews", help="Analyze product reviews")
    reviews_parser.add_argument("product_url", help="Product URL")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = ShoppingAssistantCLI()
    
    try:
        if args.command == "search":
            cli.search(args.query, args.max_results, args.sort_by)
        elif args.command == "compare":
            cli.compare(args.urls)
        elif args.command == "recommend":
            cli.recommend(args.description, args.budget, args.brands)
        elif args.command == "track":
            cli.track(args.user_id, args.product_url, args.target_price)
        elif args.command == "reviews":
            cli.reviews(args.product_url)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 