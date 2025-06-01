#!/usr/bin/env python3
"""
Simple test script to verify database setup and basic operations
"""

import asyncio
from datetime import datetime
from src.database import SessionLocal, init_database
from src.models import Meeting, MeetingType, ProcessingStatus


async def test_database_operations():
    """Test basic database operations"""
    
    print("🔧 Initializing database...")
    await init_database()
    
    # Create a database session
    db = SessionLocal()
    
    try:
        print("✅ Database connection successful!")
        
        # Test creating a meeting
        print("\n📅 Testing meeting creation...")
        test_meeting = Meeting(
            title="Test Meeting",
            description="This is a test meeting to verify database operations",
            meeting_type=MeetingType.VIRTUAL,
            platform="zoom",
            participant_count=5
        )
        
        db.add(test_meeting)
        db.commit()
        db.refresh(test_meeting)
        
        print(f"✅ Meeting created with ID: {test_meeting.id}")
        print(f"   Title: {test_meeting.title}")
        print(f"   Type: {test_meeting.meeting_type.value}")
        print(f"   Status: {test_meeting.processing_status.value}")
        print(f"   Created: {test_meeting.created_at}")
        
        # Test querying meetings
        print("\n🔍 Testing meeting query...")
        all_meetings = db.query(Meeting).all()
        print(f"✅ Found {len(all_meetings)} meeting(s) in database")
        
        # Test updating meeting
        print("\n📝 Testing meeting update...")
        test_meeting.processing_status = ProcessingStatus.COMPLETED
        test_meeting.duration_seconds = 1800  # 30 minutes
        db.commit()
        print(f"✅ Meeting status updated to: {test_meeting.processing_status.value}")
        
        # Test deleting meeting
        print("\n🗑️ Testing meeting deletion...")
        db.delete(test_meeting)
        db.commit()
        
        remaining_meetings = db.query(Meeting).all()
        print(f"✅ Meeting deleted. Remaining meetings: {len(remaining_meetings)}")
        
        print("\n🎉 All database operations completed successfully!")
        
    except Exception as e:
        print(f"❌ Database operation failed: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(test_database_operations())