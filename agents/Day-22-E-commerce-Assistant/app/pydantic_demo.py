"""
Demo script for Pydantic AI Shopping Assistant
"""

import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.shopping_assistant.pydantic_agent import PydanticShoppingAssistant
from src.shopping_assistant.database import init_database

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Demonstrate Pydantic AI Shopping Assistant features"""
    print("🤖 Pydantic AI Shopping Assistant Demo")
    print("=" * 50)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please add your OpenAI API key to the .env file")
        return
    
    print("✅ OpenAI API key loaded")
    
    # Initialize database
    init_database()
    
    # Create assistant
    assistant = PydanticShoppingAssistant()
    
    print("\n1. 🔍 AI-Enhanced Product Search")
    print("-" * 30)
    
    try:
        # Test search with AI parsing
        query = "wireless noise cancelling headphones under $200"
        print(f"Search: '{query}'")
        
        results = await assistant.search_products(query, max_results=3)
        
        print(f"✅ Found {len(results.products)} products:")
        for i, product in enumerate(results.products, 1):
            print(f"\n{i}. {product.title}")
            print(f"   💰 ${product.price:.2f}")
            print(f"   ⭐ {product.rating}/5 ({product.review_count} reviews)")
            print(f"   🏷️  {product.brand}")
            if product.features:
                print(f"   🔧 {', '.join(product.features[:3])}")
    
    except Exception as e:
        logger.error(f"Search demo error: {e}")
        print(f"❌ Search demo failed: {e}")
    
    print("\n" + "=" * 50)
    print("\n2. 💡 AI-Powered Recommendations")
    print("-" * 30)
    
    try:
        # Test recommendations
        description = "laptop for programming and gaming"
        print(f"Request: '{description}' with budget $1500")
        
        results = await assistant.get_recommendations(
            description, 
            budget=1500,
            preferred_brands=["Dell", "HP", "ASUS"]
        )
        
        print(f"✅ Found {len(results.products)} recommendations:")
        for i, product in enumerate(results.products, 1):
            print(f"\n{i}. {product.title}")
            print(f"   💰 ${product.price:.2f}")
            print(f"   ⭐ {product.rating}/5")
            print(f"   🏷️  {product.brand}")
            if product.price and product.price <= 1500:
                print("   ✓ Within budget")
    
    except Exception as e:
        logger.error(f"Recommendations demo error: {e}")
        print(f"❌ Recommendations demo failed: {e}")
    
    print("\n" + "=" * 50)
    print("\n3. ⚖️  AI Product Comparison")
    print("-" * 30)
    
    try:
        # Test comparison with demo URLs
        demo_urls = [
            "https://example-store.com/product/1",
            "https://example-store.com/product/2",
            "https://example-store.com/product/3"
        ]
        
        print(f"Comparing {len(demo_urls)} products...")
        
        comparison = await assistant.compare_products(demo_urls)
        
        print("📊 Comparison Results:")
        for i, product in enumerate(comparison.products, 1):
            print(f"\n{i}. {product.title}")
            print(f"   💰 ${product.price:.2f}")
            print(f"   ⭐ {product.rating}/5")
        
        if comparison.winner:
            print(f"\n🏆 AI Recommendation: {comparison.winner}")
        
        if comparison.summary:
            print(f"\n🤖 AI Analysis:")
            print(f"   {comparison.summary[:200]}...")
    
    except Exception as e:
        logger.error(f"Comparison demo error: {e}")
        print(f"❌ Comparison demo failed: {e}")
    
    print("\n" + "=" * 50)
    print("\n✨ Pydantic AI Features Demonstrated:")
    print("• Structured query parsing with AI")
    print("• Type-safe tool integration") 
    print("• Dependency injection for context")
    print("• Comprehensive error handling")
    print("• AI-powered analysis and recommendations")
    
    print("\n🎯 Key Benefits:")
    print("• More reliable than raw LLM calls")
    print("• Better structured outputs")
    print("• Type safety and validation")
    print("• Tool composition and reuse")
    print("• Enhanced debugging and logging")


if __name__ == "__main__":
    asyncio.run(main()) 