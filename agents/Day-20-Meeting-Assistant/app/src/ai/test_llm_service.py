#!/usr/bin/env python3
"""
Test script for LLM Service implementation.

This script tests the unified LLM service for summarization and action items.
Tests both OpenRouter and Ollama backends with fallback functionality.
"""

import asyncio
import json
from loguru import logger
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.ai.llm_service import (
    LLMService,
    MeetingSummaryRequest,
    ActionItemsRequest,
    summarize_meeting_text,
    extract_meeting_action_items
)

# Sample meeting transcript for testing
SAMPLE_TRANSCRIPT = """
Meeting: Product Development Update
Date: May 29, 2025
Participants: Sarah (Product Manager), Mike (Developer), Lisa (Designer), John (QA)

Sarah: Good morning everyone. Let's review our progress on the new features.

Mike: I've completed the user authentication module. It's ready for testing. We should deploy it to staging by Friday.

Sarah: Great work, Mike. Lisa, how's the UI redesign coming along?

Lisa: I've finished the wireframes and mockups. I need feedback from the team by tomorrow to proceed with the implementation. The deadline for final designs is next Tuesday.

John: I'll start testing the authentication module tomorrow. Mike, can you provide the test cases by end of day?

Mike: Sure, I'll send them over by 5 PM today.

Sarah: Perfect. We also need to plan the user research session. Lisa, can you coordinate with the UX team to schedule it for next week?

Lisa: Absolutely. I'll reach out to them today and aim for Wednesday or Thursday.

John: One concern - we're running behind on the performance testing. This is high priority and needs immediate attention.

Sarah: Good point, John. Let's assign additional resources to that. Mike, can you help John with the performance testing starting Monday?

Mike: Yes, I can allocate time for that. We should prioritize the database queries optimization first.

Sarah: Excellent. Let's wrap up. To summarize: Mike will provide test cases today, deploy to staging by Friday, and help with performance testing. Lisa will get team feedback by tomorrow and coordinate user research. John will test authentication and lead performance testing. Any questions?

Everyone: No questions.

Sarah: Great, meeting adjourned.
"""

async def test_llm_service_initialization():
    """Test LLM service initialization"""
    print("\n=== Testing LLM Service Initialization ===")
    
    try:
        # Test with default settings
        async with LLMService() as llm_service:
            status = llm_service.get_status()
            print(f"Service status: {json.dumps(status, indent=2)}")
            
            # Test health check
            health = await llm_service.health_check()
            print(f"Health check results: {json.dumps(health, indent=2)}")
            
        print("✅ LLM Service initialization successful")
        return True
        
    except Exception as e:
        print(f"❌ LLM Service initialization failed: {e}")
        return False

async def test_meeting_summarization():
    """Test meeting summarization functionality"""
    print("\n=== Testing Meeting Summarization ===")
    
    try:
        async with LLMService() as llm_service:
            # Test different summary types
            summary_types = ["brief", "detailed", "executive"]
            
            for summary_type in summary_types:
                print(f"\nTesting {summary_type} summary...")
                
                request = MeetingSummaryRequest(
                    transcript=SAMPLE_TRANSCRIPT,
                    meeting_title="Product Development Update",
                    participants=["Sarah", "Mike", "Lisa", "John"],
                    duration_minutes=25,
                    summary_type=summary_type
                )
                
                response = await llm_service.summarize_meeting(request)
                
                print(f"Provider: {response.provider.value}")
                print(f"Model: {response.model}")
                print(f"Processing time: {response.processing_time:.2f}s")
                print(f"Tokens used: {response.tokens_used}")
                print(f"Summary length: {len(response.content)} characters")
                print(f"Summary preview: {response.content[:200]}...")
        
        print("✅ Meeting summarization test successful")
        return True
        
    except Exception as e:
        print(f"❌ Meeting summarization test failed: {e}")
        logger.exception("Summarization error details:")
        return False

async def test_action_item_extraction():
    """Test action item extraction functionality"""
    print("\n=== Testing Action Item Extraction ===")
    
    try:
        async with LLMService() as llm_service:
            request = ActionItemsRequest(
                transcript=SAMPLE_TRANSCRIPT,
                participants=["Sarah", "Mike", "Lisa", "John"],
                context="Product development meeting focusing on feature delivery"
            )
            
            response = await llm_service.extract_action_items(request)
            
            print(f"Provider: {response.provider.value}")
            print(f"Model: {response.model}")
            print(f"Processing time: {response.processing_time:.2f}s")
            print(f"Raw response length: {len(response.content)} characters")
            
            # Parse action items
            action_items = llm_service.parse_action_items(response)
            
            print(f"\nExtracted {len(action_items)} action items:")
            for i, item in enumerate(action_items, 1):
                print(f"{i}. Action: {item['action']}")
                print(f"   Assignee: {item['assignee']}")
                print(f"   Deadline: {item['deadline']}")
                print(f"   Priority: {item['priority']}")
                print()
        
        print("✅ Action item extraction test successful")
        return True
        
    except Exception as e:
        print(f"❌ Action item extraction test failed: {e}")
        logger.exception("Action item extraction error details:")
        return False

async def test_convenience_functions():
    """Test convenience functions"""
    print("\n=== Testing Convenience Functions ===")
    
    try:
        # Test summarize_meeting_text
        print("Testing summarize_meeting_text...")
        summary = await summarize_meeting_text(
            transcript=SAMPLE_TRANSCRIPT,
            meeting_title="Product Development Update",
            summary_type="brief"
        )
        print(f"Brief summary: {summary[:200]}...")
        
        # Test extract_meeting_action_items
        print("\nTesting extract_meeting_action_items...")
        action_items = await extract_meeting_action_items(
            transcript=SAMPLE_TRANSCRIPT,
            participants=["Sarah", "Mike", "Lisa", "John"]
        )
        print(f"Extracted {len(action_items)} action items via convenience function")
        
        print("✅ Convenience functions test successful")
        return True
        
    except Exception as e:
        print(f"❌ Convenience functions test failed: {e}")
        logger.exception("Convenience functions error details:")
        return False

async def test_error_handling():
    """Test error handling and fallback mechanisms"""
    print("\n=== Testing Error Handling ===")
    
    try:
        # Test with invalid transcript
        async with LLMService() as llm_service:
            try:
                request = MeetingSummaryRequest(transcript="")
                response = await llm_service.summarize_meeting(request)
                print("⚠️  Empty transcript handled gracefully")
            except Exception as e:
                print(f"⚠️  Empty transcript error: {e}")
            
            # Test action item parsing with malformed JSON
            from src.ai.llm_service import LLMResponse, LLMProvider
            malformed_response = LLMResponse(
                content="This is not valid JSON for action items",
                provider=LLMProvider.OLLAMA,
                model="test"
            )
            
            action_items = llm_service.parse_action_items(malformed_response)
            print(f"Malformed JSON handled, extracted {len(action_items)} items")
        
        print("✅ Error handling test successful")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

async def test_model_configuration():
    """Test different model configurations"""
    print("\n=== Testing Model Configuration ===")
    
    try:
        # Test with local LLM preference
        print("Testing with local LLM preference...")
        async with LLMService(use_local_llm=True) as local_service:
            status = local_service.get_status()
            print(f"Local LLM status: {status['use_local_llm']}")
        
        # Test with cloud LLM preference
        print("Testing with cloud LLM preference...")
        async with LLMService(use_local_llm=False) as cloud_service:
            status = cloud_service.get_status()
            print(f"Cloud LLM status: {not status['use_local_llm']}")
        
        print("✅ Model configuration test successful")
        return True
        
    except Exception as e:
        print(f"❌ Model configuration test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("Starting LLM Service Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Run all tests
    test_functions = [
        test_llm_service_initialization,
        test_meeting_summarization,
        test_action_item_extraction,
        test_convenience_functions,
        test_error_handling,
        test_model_configuration
    ]
    
    for test_func in test_functions:
        try:
            result = await test_func()
            test_results.append(result)
        except Exception as e:
            print(f"❌ Test {test_func.__name__} crashed: {e}")
            test_results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! LLM Service is working correctly.")
    else:
        print("⚠️  Some tests failed. Review the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=''),
        format="{time:HH:mm:ss} | {level} | {message}",
        level="INFO"
    )
    
    # Run tests
    result = asyncio.run(main())
    exit(0 if result else 1)