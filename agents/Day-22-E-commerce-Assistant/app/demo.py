#!/usr/bin/env python3
"""
Demo script for the Shopping Assistant
Shows off key features without requiring API keys
"""

import os
import sys
import time

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from shopping_assistant.agent import ShoppingAssistant
from shopping_assistant.models import SearchQuery, RecommendationRequest, QueryType
from shopping_assistant.database import init_database


def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_products(products, title="Products"):
    """Print products in a formatted way"""
    print(f"\n📦 {title} ({len(products)} found):")
    print("-" * 40)
    
    for i, product in enumerate(products, 1):
        print(f"\n{i}. {product.title}")
        print(f"   💰 ${product.price:.2f}" if product.price else "   💰 Price: N/A")
        print(f"   ⭐ {product.rating}/5 ({product.review_count} reviews)" if product.rating else "   ⭐ Rating: N/A")
        print(f"   🏷️  {product.brand}" if product.brand else "   🏷️  Brand: N/A")
        if product.features:
            print(f"   🔧 {', '.join(product.features[:3])}")
        print(f"   📦 Source: {product.source}")


def demo_search():
    """Demo product search functionality"""
    print_header("🔍 PRODUCT SEARCH DEMO")
    
    assistant = ShoppingAssistant()
    
    # Example searches
    queries = [
        "wireless headphones under $200",
        "gaming laptop for programming",
        "running shoes with good cushioning"
    ]
    
    for query in queries:
        print(f"\n🔍 Searching for: '{query}'")
        
        search_query = SearchQuery(
            query=query,
            query_type=QueryType.SEARCH,
            max_results=3
        )
        
        results = assistant.search_products(search_query)
        print_products(results.products)
        
        if results.suggestions:
            print(f"\n💡 Related searches: {', '.join(results.suggestions[:2])}")


def demo_recommendations():
    """Demo recommendation functionality"""
    print_header("💡 RECOMMENDATION DEMO")
    
    assistant = ShoppingAssistant()
    
    # Example recommendation requests
    requests = [
        {
            "description": "laptop for programming and gaming",
            "budget": 1500,
            "brands": ["Dell", "HP", "ASUS"]
        },
        {
            "description": "wireless earbuds for workouts",
            "budget": 150,
            "brands": ["Apple", "Sony"]
        }
    ]
    
    for req_data in requests:
        print(f"\n💡 Getting recommendations for: '{req_data['description']}'")
        print(f"💰 Budget: ${req_data['budget']}")
        print(f"🏷️  Preferred brands: {', '.join(req_data['brands'])}")
        
        request = RecommendationRequest(
            description=req_data["description"],
            budget=req_data["budget"],
            preferred_brands=req_data["brands"]
        )
        
        results = assistant.get_recommendations(request)
        print_products(results.products, "Recommendations")


def demo_price_tracking():
    """Demo price tracking functionality"""
    print_header("📈 PRICE TRACKING DEMO")
    
    assistant = ShoppingAssistant()
    
    print("\n📈 Setting up price tracking...")
    
    # Example price tracking
    try:
        tracker = assistant.track_price(
            user_id="demo@example.com",
            product_url="https://example-store.com/product/demo-headphones",
            target_price=150.0
        )
        
        print("✅ Price tracking set up successfully!")
        print(f"📦 Product: {tracker.product_title}")
        print(f"💲 Current price: ${tracker.current_price}" if tracker.current_price else "💲 Current price: N/A")
        print(f"🎯 Target price: ${tracker.target_price}")
        print(f"🆔 Tracker ID: {tracker.id}")
        print("\n💬 You'll be notified when the price drops below your target!")
        
    except Exception as e:
        print(f"❌ Error setting up price tracking: {e}")


def demo_comparison():
    """Demo product comparison functionality"""
    print_header("⚖️  PRODUCT COMPARISON DEMO")
    
    print("\n⚖️  Product comparison would analyze multiple products")
    print("   and provide AI-powered recommendations based on:")
    print("   • Value for money")
    print("   • Features and specifications")
    print("   • User ratings and reviews")
    print("   • Brand reputation")
    print("\n💡 In a real scenario, you would provide actual product URLs")
    print("   and get detailed comparison analysis with winner selection.")


def main():
    """Run the complete demo"""
    print("🛍️  Welcome to the Shopping Assistant Demo!")
    print("This demo showcases the key features using simulated data.")
    print("For full functionality, set up OpenAI API key and run the web interface.")
    
    # Initialize database
    init_database()
    
    try:
        # Run demos
        demo_search()
        time.sleep(2)
        
        demo_recommendations()
        time.sleep(2)
        
        demo_price_tracking()
        time.sleep(2)
        
        demo_comparison()
        
        print_header("🎉 DEMO COMPLETE")
        print("\n✨ Key Features Demonstrated:")
        print("   ✅ Smart product search with natural language")
        print("   ✅ AI-powered personalized recommendations")
        print("   ✅ Price tracking and alerts")
        print("   ✅ Product comparison capabilities")
        
        print("\n🚀 Next Steps:")
        print("   1. Set up OpenAI API key in .env file")
        print("   2. Run 'python main.py' for the web interface")
        print("   3. Visit http://localhost:8000 to try it live")
        print("   4. Or use 'python main.py --mode cli' for command line")
        
        print("\n📖 Full documentation available in README.md")
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for trying the Shopping Assistant!")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("This is normal if OpenAI API key is not configured.")
        print("The demo uses simulated data for core functionality.")


if __name__ == "__main__":
    main() 