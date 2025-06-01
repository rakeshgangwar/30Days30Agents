"""
Database utility functions for Meeting Assistant
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database import SessionLocal, get_database_session
from src.models import Meeting, Speaker, Transcript, AudioChunk, MeetingSummary, ActionItem


class DatabaseUtils:
    """Utility class for common database operations"""
    
    @staticmethod
    def get_db_session() -> Session:
        """Get a new database session"""
        return SessionLocal()
    
    @staticmethod
    def get_meeting_by_id(db: Session, meeting_id: int) -> Optional[Meeting]:
        """Get a meeting by ID"""
        return db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    @staticmethod
    def get_meetings(db: Session, skip: int = 0, limit: int = 100) -> List[Meeting]:
        """Get a list of meetings with pagination"""
        return db.query(Meeting).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_meeting(db: Session, meeting_data: Dict[str, Any]) -> Meeting:
        """Create a new meeting"""
        meeting = Meeting(**meeting_data)
        db.add(meeting)
        db.commit()
        db.refresh(meeting)
        return meeting
    
    @staticmethod
    def update_meeting(db: Session, meeting_id: int, update_data: Dict[str, Any]) -> Optional[Meeting]:
        """Update a meeting"""
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            for key, value in update_data.items():
                if hasattr(meeting, key):
                    setattr(meeting, key, value)
            db.commit()
            db.refresh(meeting)
        return meeting
    
    @staticmethod
    def delete_meeting(db: Session, meeting_id: int) -> bool:
        """Delete a meeting and all related data"""
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            db.delete(meeting)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_speakers_for_meeting(db: Session, meeting_id: int) -> List[Speaker]:
        """Get all speakers for a meeting"""
        return db.query(Speaker).filter(Speaker.meeting_id == meeting_id).all()
    
    @staticmethod
    def get_transcripts_for_meeting(db: Session, meeting_id: int) -> List[Transcript]:
        """Get all transcripts for a meeting, ordered by start time"""
        return (
            db.query(Transcript)
            .filter(Transcript.meeting_id == meeting_id)
            .order_by(Transcript.start_time)
            .all()
        )
    
    @staticmethod
    def get_audio_chunks_for_meeting(db: Session, meeting_id: int) -> List[AudioChunk]:
        """Get all audio chunks for a meeting, ordered by chunk index"""
        return (
            db.query(AudioChunk)
            .filter(AudioChunk.meeting_id == meeting_id)
            .order_by(AudioChunk.chunk_index)
            .all()
        )
    
    @staticmethod
    def get_summaries_for_meeting(db: Session, meeting_id: int) -> List[MeetingSummary]:
        """Get all summaries for a meeting"""
        return db.query(MeetingSummary).filter(MeetingSummary.meeting_id == meeting_id).all()
    
    @staticmethod
    def get_action_items_for_meeting(db: Session, meeting_id: int) -> List[ActionItem]:
        """Get all action items for a meeting"""
        return db.query(ActionItem).filter(ActionItem.meeting_id == meeting_id).all()
    
    @staticmethod
    def check_database_health(db: Session) -> Dict[str, Any]:
        """Check database health and return status information"""
        try:
            # Test basic query
            result = db.execute(text("SELECT 1"))
            result.fetchone()
            
            # Get table counts
            meeting_count = db.query(Meeting).count()
            
            return {
                "status": "healthy",
                "connection": "active",
                "meeting_count": meeting_count,
                "database_type": "SQLite" if "sqlite" in str(db.bind.url) else "PostgreSQL"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "connection": "failed",
                "error": str(e)
            }
    
    @staticmethod
    def get_database_info(db: Session) -> Dict[str, Any]:
        """Get detailed database information"""
        try:
            info = {
                "database_url": str(db.bind.url),
                "tables": {}
            }
            
            # Count records in each table
            table_models = [Meeting, Speaker, Transcript, AudioChunk, MeetingSummary, ActionItem]
            for model in table_models:
                table_name = model.__tablename__
                count = db.query(model).count()
                info["tables"][table_name] = count
            
            return info
        except Exception as e:
            return {"error": str(e)}


# Convenience functions for direct use
def create_meeting_with_session(meeting_data: Dict[str, Any]) -> Meeting:
    """Create a meeting with automatic session management"""
    with SessionLocal() as db:
        return DatabaseUtils.create_meeting(db, meeting_data)


def get_meeting_with_session(meeting_id: int) -> Optional[Meeting]:
    """Get a meeting with automatic session management"""
    with SessionLocal() as db:
        return DatabaseUtils.get_meeting_by_id(db, meeting_id)


def get_database_status() -> Dict[str, Any]:
    """Get database status with automatic session management"""
    try:
        with SessionLocal() as db:
            return DatabaseUtils.check_database_health(db)
    except Exception as e:
        return {
            "status": "unhealthy",
            "connection": "failed",
            "error": str(e)
        }