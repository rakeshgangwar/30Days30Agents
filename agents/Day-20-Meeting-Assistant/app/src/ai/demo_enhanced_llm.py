#!/usr/bin/env python3
"""
Demo script for enhanced LLM Service features.

This script demonstrates the enhanced capabilities of the LLM service
including meeting type-specific processing, sentiment analysis, topic extraction,
and comprehensive meeting analysis.
"""

import asyncio
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.ai.llm_service import LLMService, MeetingSummaryRequest, ActionItemsRequest
from src.ai.prompt_templates import MeetingType
from loguru import logger

# Sample meeting transcripts for different meeting types
STANDUP_TRANSCRIPT = """
Daily Standup - May 29, 2025
Team: Product Development

Sarah (Scrum Master): Good morning everyone. Let's go around the table for our daily standup.

Mike (Developer): Yesterday I completed the user authentication API endpoints. Today I'm working on the database migration scripts. No blockers currently.

Lisa (Frontend): I finished the login component styling yesterday. Today I'm implementing the dashboard layout. I'm blocked on the API documentation - Mike, when will that be ready?

Mike: I'll have the API docs uploaded to the wiki by 2 PM today.

John (QA): Yesterday I tested the registration flow, found two minor bugs which I've logged. Today I'm setting up the automated test suite. No blockers.

Sarah: Great progress everyone. Lisa, once you get the API docs, you should be unblocked. Mike, please prioritize those docs. Any other concerns?

Lisa: Just a heads up, I might need help with the responsive design testing on mobile devices later this week.

John: I can help with that. I have some device testing setups ready.

Sarah: Perfect. Let's connect offline about that. Meeting adjourned.
"""

PLANNING_TRANSCRIPT = """
Sprint Planning Meeting - Product Feature Development
Date: May 29, 2025
Participants: Sarah (Product Manager), Mike (Senior Dev), Lisa (Frontend), John (QA), David (Designer)

Sarah: Welcome to our sprint planning for the next two weeks. We have three major features to plan: user profiles, notification system, and search functionality.

Mike: Based on the technical analysis, the user profiles feature will take approximately 5 days. We need to consider database schema changes and API updates.

David: I've completed the user profile mockups. The design is ready for implementation, but we'll need to iterate based on user feedback.

Lisa: For the frontend implementation, I estimate 4 days including responsive design and accessibility features.

John: Testing for user profiles will require 2 days - unit tests, integration tests, and user acceptance testing.

Sarah: Great. What about the notification system?

Mike: That's more complex. We need to integrate with push notification services, implement real-time updates via WebSockets. I estimate 8 days.

Lisa: Frontend notifications will take 3 days - toast notifications, notification center, and user preferences.

John: Notification testing is critical - we need to test across different devices and browsers. I need 3 days for comprehensive testing.

Sarah: And search functionality?

Mike: Basic search implementation is 4 days, but for advanced filtering and indexing, we need an additional 3 days.

Lisa: Search UI and autocomplete features will take 3 days.

David: I need 2 days to finalize the search interface designs based on user research.

Sarah: Let's prioritize user profiles first, then notifications, then search. Mike, can you create the technical stories by tomorrow?

Mike: Yes, I'll break down the technical requirements and create stories in Jira by end of day.

John: I'll prepare test plans for each feature this week.

Sarah: Perfect. Any risks or dependencies we should consider?

Mike: The notification system depends on third-party services. We should have fallback options ready.

Lisa: I might need design clarifications for edge cases. David, can we schedule design reviews?

David: Absolutely. Let's do daily design check-ins during implementation.

Sarah: Excellent planning session everyone. Let's make this sprint successful!
"""

async def demo_enhanced_summarization():
    """Demo enhanced summarization with meeting types"""
    print("\n=== Enhanced Summarization Demo ===")
    
    async with LLMService() as llm_service:
        # Test standup summary
        print("Testing Standup Meeting Summary...")
        standup_request = MeetingSummaryRequest(
            transcript=STANDUP_TRANSCRIPT,
            meeting_title="Daily Standup",
            participants=["Sarah", "Mike", "Lisa", "John"],
            duration_minutes=10,
            summary_type="brief",
            meeting_type=MeetingType.STANDUP,
            use_enhanced_prompts=True
        )
        
        standup_summary = await llm_service.summarize_meeting(standup_request)
        print(f"Standup Summary ({standup_summary.processing_time:.2f}s):")
        print(standup_summary.content[:300] + "...")
        
        # Test planning summary
        print("\nTesting Planning Meeting Summary...")
        planning_request = MeetingSummaryRequest(
            transcript=PLANNING_TRANSCRIPT,
            meeting_title="Sprint Planning",
            participants=["Sarah", "Mike", "Lisa", "John", "David"],
            duration_minutes=45,
            summary_type="detailed",
            meeting_type=MeetingType.PLANNING,
            use_enhanced_prompts=True
        )
        
        planning_summary = await llm_service.summarize_meeting(planning_request)
        print(f"Planning Summary ({planning_summary.processing_time:.2f}s):")
        print(planning_summary.content[:400] + "...")

async def demo_enhanced_action_items():
    """Demo enhanced action item extraction"""
    print("\n=== Enhanced Action Items Demo ===")
    
    async with LLMService() as llm_service:
        # Test standup action items
        print("Extracting Standup Action Items...")
        standup_request = ActionItemsRequest(
            transcript=STANDUP_TRANSCRIPT,
            participants=["Sarah", "Mike", "Lisa", "John"],
            meeting_type=MeetingType.STANDUP,
            use_enhanced_prompts=True
        )
        
        standup_response = await llm_service.extract_action_items(standup_request)
        standup_items = llm_service.parse_action_items(standup_response)
        
        print(f"Found {len(standup_items)} action items:")
        for i, item in enumerate(standup_items, 1):
            print(f"{i}. {item['action']}")
            print(f"   Assignee: {item['assignee']}, Priority: {item['priority']}, Category: {item['category']}")
        
        # Test planning action items
        print("\nExtracting Planning Action Items...")
        planning_request = ActionItemsRequest(
            transcript=PLANNING_TRANSCRIPT,
            participants=["Sarah", "Mike", "Lisa", "John", "David"],
            meeting_type=MeetingType.PLANNING,
            use_enhanced_prompts=True
        )
        
        planning_response = await llm_service.extract_action_items(planning_request)
        planning_items = llm_service.parse_action_items(planning_response)
        
        print(f"Found {len(planning_items)} action items:")
        for i, item in enumerate(planning_items[:5], 1):  # Show first 5
            print(f"{i}. {item['action']}")
            print(f"   Assignee: {item['assignee']}, Priority: {item['priority']}, Category: {item['category']}")

async def demo_topic_extraction():
    """Demo topic extraction"""
    print("\n=== Topic Extraction Demo ===")
    
    async with LLMService() as llm_service:
        print("Extracting topics from planning meeting...")
        topics = await llm_service.extract_topics(PLANNING_TRANSCRIPT)
        
        print(f"Found {len(topics)} topics:")
        for topic in topics:
            print(f"• {topic.get('topic', 'Unknown')}: {topic.get('description', 'No description')}")
            print(f"  Duration: {topic.get('duration_discussed', 'Unknown')} min, "
                  f"Importance: {topic.get('importance', 'Unknown')}")

async def demo_sentiment_analysis():
    """Demo sentiment analysis"""
    print("\n=== Sentiment Analysis Demo ===")
    
    async with LLMService() as llm_service:
        print("Analyzing sentiment of planning meeting...")
        sentiment = await llm_service.analyze_sentiment(PLANNING_TRANSCRIPT)
        
        print("Sentiment Analysis Results:")
        print(f"• Overall Sentiment: {sentiment.get('overall_sentiment', 'Unknown')}")
        print(f"• Engagement Level: {sentiment.get('engagement_level', 'Unknown')}")
        print(f"• Collaboration Quality: {sentiment.get('collaboration_quality', 'Unknown')}")
        print(f"• Energy Level: {sentiment.get('energy_level', 'Unknown')}")
        print(f"• Conflict Indicators: {sentiment.get('conflict_indicators', False)}")
        print(f"• Concerns Raised: {sentiment.get('concerns_raised', 0)}")
        print(f"• Positive Moments: {sentiment.get('positive_moments', 0)}")

async def demo_comprehensive_analysis():
    """Demo comprehensive analysis"""
    print("\n=== Comprehensive Analysis Demo ===")
    
    async with LLMService() as llm_service:
        print("Running comprehensive analysis on planning meeting...")
        start_time = asyncio.get_event_loop().time()
        
        analysis = await llm_service.comprehensive_analysis(
            transcript=PLANNING_TRANSCRIPT,
            meeting_title="Sprint Planning Meeting",
            participants=["Sarah", "Mike", "Lisa", "John", "David"],
            duration_minutes=45,
            meeting_type=MeetingType.PLANNING
        )
        
        end_time = asyncio.get_event_loop().time()
        total_time = end_time - start_time
        
        print(f"Analysis completed in {total_time:.2f} seconds")
        print(f"Summary length: {len(analysis['summary']['content'])} characters")
        print(f"Action items found: {analysis['metadata']['total_action_items']}")
        print(f"Topics identified: {analysis['metadata']['total_topics']}")
        print(f"Overall sentiment: {analysis['sentiment'].get('overall_sentiment', 'Unknown')}")
        
        # Show sample action items
        print("\nSample Action Items:")
        for item in analysis['action_items'][:3]:
            print(f"• {item['action']} (Assignee: {item['assignee']}, Priority: {item['priority']})")

async def demo_error_handling():
    """Demo error handling with malformed inputs"""
    print("\n=== Error Handling Demo ===")
    
    async with LLMService() as llm_service:
        # Test with empty transcript
        print("Testing with empty transcript...")
        try:
            request = MeetingSummaryRequest(transcript="")
            response = await llm_service.summarize_meeting(request)
            print(f"Empty transcript handled: {len(response.content)} characters generated")
        except Exception as e:
            print(f"Error with empty transcript: {e}")
        
        # Test with very short transcript
        print("Testing with minimal transcript...")
        try:
            short_transcript = "Meeting started. No agenda. Meeting ended."
            topics = await llm_service.extract_topics(short_transcript)
            print(f"Short transcript topics: {len(topics)} topics found")
        except Exception as e:
            print(f"Error with short transcript: {e}")

async def main():
    """Run all demos"""
    print("Enhanced LLM Service Demo")
    print("=" * 50)
    
    demos = [
        demo_enhanced_summarization,
        demo_enhanced_action_items,
        demo_topic_extraction,
        demo_sentiment_analysis,
        demo_comprehensive_analysis,
        demo_error_handling
    ]
    
    for demo in demos:
        try:
            await demo()
        except Exception as e:
            print(f"Demo {demo.__name__} failed: {e}")
            logger.exception(f"Demo error in {demo.__name__}")
    
    print("\n" + "=" * 50)
    print("Enhanced LLM Service Demo Completed!")

if __name__ == "__main__":
    # Configure logging
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=''),
        format="{time:HH:mm:ss} | {level} | {message}",
        level="INFO"
    )
    
    # Run demos
    asyncio.run(main())