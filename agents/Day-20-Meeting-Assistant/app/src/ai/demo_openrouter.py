"""
Demo script for OpenRouter integration.

This script demonstrates the OpenRouter API integration and LLM service
functionality. It can be used to test the implementation and verify
that everything is working correctly.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = str(project_root)

from src.ai.openrouter_client import OpenRouterClient, OpenRouterModel
from src.ai.llm_service import LLMService, MeetingSummaryRequest, ActionItemsRequest
from config.settings import settings


async def demo_openrouter_client():
    """Demonstrate OpenRouter client functionality"""
    print("🔍 Testing OpenRouter Client")
    print("=" * 50)
    
    # Check if API key is available
    api_key = settings.OPENROUTER_API_KEY
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment")
        print("Please set your OpenRouter API key in the .env file")
        return False
    
    try:
        async with OpenRouterClient(api_key=api_key) as client:
            print(f"✅ Client initialized with model: {client.default_model}")
            
            # Test health check
            print("\n🏥 Testing health check...")
            healthy = await client.health_check()
            print(f"Health check result: {'✅ Healthy' if healthy else '❌ Unhealthy'}")
            
            if not healthy:
                return False
            
            # Test simple completion
            print("\n💬 Testing simple completion...")
            result = await client.generate_completion(
                prompt="Say 'Hello from OpenRouter!' and nothing else.",
                max_tokens=10,
                temperature=0.0
            )
            
            if "choices" in result and result["choices"]:
                response_text = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", "unknown")
                print(f"Response: {response_text}")
                print(f"Tokens used: {tokens_used}")
                print("✅ Simple completion successful")
            else:
                print("❌ Invalid response format")
                return False
            
            # Test rate limit status
            print("\n📊 Rate limit status:")
            rate_status = client.get_rate_limit_status()
            for category, info in rate_status.items():
                used = info["used"]
                limit = info["limit"]
                remaining = info["remaining"]
                print(f"  {category}: {used}/{limit} (remaining: {remaining})")
            
        return True
    
    except Exception as e:
        print(f"❌ Error testing OpenRouter client: {e}")
        return False


async def demo_llm_service():
    """Demonstrate LLM service functionality"""
    print("\n\n🧠 Testing LLM Service")
    print("=" * 50)
    
    # Sample meeting transcript
    sample_transcript = """
    John: Good morning everyone. Welcome to our Q4 planning meeting.
    Sarah: Thanks John. I'd like to start by reviewing our Q3 performance.
    Mike: The sales numbers were strong, we hit 95% of our target.
    Sarah: That's great! For Q4, I think we should focus on customer retention.
    John: Agreed. Sarah, can you prepare a retention strategy presentation by next Friday?
    Sarah: Absolutely, I'll have that ready.
    Mike: I'll help with the customer data analysis.
    John: Perfect. Let's also schedule weekly check-ins throughout Q4.
    Sarah: Should we invite the marketing team to these check-ins?
    John: Yes, let's include them. Mike, can you set up the recurring meetings?
    Mike: Sure, I'll send out calendar invites this afternoon.
    """
    
    try:
        async with LLMService() as llm_service:
            # Test service status
            print("📋 Service status:")
            status = llm_service.get_status()
            for key, value in status.items():
                if key != "openrouter_rate_limits":
                    print(f"  {key}: {value}")
            
            # Test health check
            print("\n🏥 Testing LLM service health...")
            health = await llm_service.health_check()
            print(f"OpenRouter: {'✅ Available' if health['openrouter']['available'] else '❌ Unavailable'}")
            if health['openrouter']['available']:
                print(f"OpenRouter Health: {'✅ Healthy' if health['openrouter']['healthy'] else '❌ Unhealthy'}")
            print(f"Ollama: {'✅ Available' if health['ollama']['available'] else '❌ Unavailable'}")
            
            if not health['openrouter']['available'] or not health['openrouter']['healthy']:
                print("❌ OpenRouter not available, skipping LLM service demo")
                return False
            
            # Test meeting summarization
            print("\n📝 Testing meeting summarization...")
            summary_request = MeetingSummaryRequest(
                transcript=sample_transcript,
                meeting_title="Q4 Planning Meeting",
                participants=["John", "Sarah", "Mike"],
                duration_minutes=30,
                summary_type="detailed"
            )
            
            summary_response = await llm_service.summarize_meeting(summary_request)
            print(f"Summary (using {summary_response.provider.value}):")
            print(f"Model: {summary_response.model}")
            print(f"Tokens used: {summary_response.tokens_used}")
            print(f"Processing time: {summary_response.processing_time:.2f}s")
            print("Summary content:")
            print("-" * 40)
            print(summary_response.content)
            print("-" * 40)
            
            # Test action items extraction
            print("\n📋 Testing action items extraction...")
            action_items_request = ActionItemsRequest(
                transcript=sample_transcript,
                participants=["John", "Sarah", "Mike"],
                context="Q4 planning meeting focused on customer retention strategy"
            )
            
            action_response = await llm_service.extract_action_items(action_items_request)
            action_items = llm_service.parse_action_items(action_response)
            
            print(f"Action items extraction (using {action_response.provider.value}):")
            print(f"Model: {action_response.model}")
            print(f"Tokens used: {action_response.tokens_used}")
            print(f"Processing time: {action_response.processing_time:.2f}s")
            print(f"Found {len(action_items)} action items:")
            
            for i, item in enumerate(action_items, 1):
                print(f"\n  {i}. Action: {item['action']}")
                print(f"     Assignee: {item['assignee'] or 'Not specified'}")
                print(f"     Deadline: {item['deadline'] or 'Not specified'}")
                print(f"     Priority: {item['priority']}")
            
            # Test different summary types
            print("\n📄 Testing different summary types...")
            for summary_type in ["brief", "executive"]:
                print(f"\n{summary_type.title()} summary:")
                brief_request = MeetingSummaryRequest(
                    transcript=sample_transcript,
                    summary_type=summary_type
                )
                brief_response = await llm_service.summarize_meeting(brief_request)
                print(f"Tokens: {brief_response.tokens_used}, Time: {brief_response.processing_time:.2f}s")
                print(brief_response.content[:200] + "..." if len(brief_response.content) > 200 else brief_response.content)
        
        return True
    
    except Exception as e:
        print(f"❌ Error testing LLM service: {e}")
        import traceback
        traceback.print_exc()
        return False


async def demo_api_endpoints():
    """Demonstrate API endpoints functionality"""
    print("\n\n🌐 API Endpoints Information")
    print("=" * 50)
    
    print("The following API endpoints are now available:")
    print("📝 POST /api/llm/summarize")
    print("   - Generate meeting summaries from transcript text")
    print("   - Supports brief, detailed, and executive summaries")
    
    print("\n📋 POST /api/llm/extract-action-items")
    print("   - Extract action items from meeting transcripts")
    print("   - Identifies assignees, deadlines, and priorities")
    
    print("\n🏥 GET /api/llm/health")
    print("   - Check health status of LLM providers")
    
    print("\n📊 GET /api/llm/status")
    print("   - Get service status and rate limit information")
    
    print("\n🧪 POST /api/llm/test")
    print("   - Test LLM connection with a simple prompt")
    
    print("\nTo test these endpoints:")
    print("1. Start the FastAPI server: uvicorn src.main:app --reload")
    print("2. Visit http://localhost:8000/docs for interactive API documentation")
    print("3. Use tools like curl, Postman, or the Swagger UI to test endpoints")
    
    # Example curl commands
    print("\nExample curl commands:")
    print("# Test LLM health")
    print("curl -X GET http://localhost:8000/api/llm/health")
    
    print("\n# Get service status")
    print("curl -X GET http://localhost:8000/api/llm/status")
    
    print("\n# Test summarization")
    print('curl -X POST http://localhost:8000/api/llm/summarize \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"transcript":"Meeting transcript here","summary_type":"brief"}\'')


async def main():
    """Main demo function"""
    print("🚀 OpenRouter Integration Demo")
    print("=" * 60)
    
    # Check environment
    print("🔧 Environment check:")
    print(f"  Environment: {settings.ENVIRONMENT}")
    print(f"  Use Local LLM: {settings.USE_LOCAL_LLM}")
    print(f"  OpenRouter Model: {settings.OPENROUTER_MODEL}")
    print(f"  API Key Present: {'✅ Yes' if settings.OPENROUTER_API_KEY else '❌ No'}")
    
    if not settings.OPENROUTER_API_KEY:
        print("\n❌ Cannot proceed without OpenRouter API key")
        print("Please set OPENROUTER_API_KEY in your .env file")
        return
    
    # Run demos
    client_success = await demo_openrouter_client()
    
    if client_success:
        service_success = await demo_llm_service()
        
        if service_success:
            await demo_api_endpoints()
            
            print("\n\n🎉 All demos completed successfully!")
            print("Your OpenRouter integration is working correctly.")
        else:
            print("\n❌ LLM service demo failed")
    else:
        print("\n❌ OpenRouter client demo failed")
    
    print("\n📚 Next steps:")
    print("1. Run the test suite: python -m pytest src/ai/test_openrouter.py -v")
    print("2. Start the API server: uvicorn src.main:app --reload")
    print("3. Test API endpoints at http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(main())