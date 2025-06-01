"""
API routes for meeting management functionality.

This module provides FastAPI routes for meeting CRUD operations:
- Create meetings
- List meetings
- Get meeting details
- Delete meetings
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from loguru import logger

from src.database import get_database_session
from src.models import Meeting, MeetingType, ProcessingStatus
from src.models import Transcript, Speaker, MeetingSummary, ActionItem


# Create router
router = APIRouter(prefix="/api/meetings", tags=["meetings"])


# Pydantic models for request/response validation
class MeetingCreateRequest(BaseModel):
    """Request model for creating a new meeting."""
    title: str = Field(..., min_length=1, max_length=255, description="Meeting title")
    description: Optional[str] = Field(None, description="Meeting description")
    meeting_type: MeetingType = Field(default=MeetingType.VIRTUAL, description="Type of meeting")
    meeting_date: Optional[datetime] = Field(None, description="Scheduled meeting date")
    participant_count: Optional[int] = Field(None, ge=1, description="Number of participants")
    platform: Optional[str] = Field(None, max_length=100, description="Meeting platform (zoom, teams, etc.)")
    meeting_url: Optional[str] = Field(None, max_length=500, description="Meeting URL")


class MeetingUpdateRequest(BaseModel):
    """Request model for updating an existing meeting."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Meeting title")
    description: Optional[str] = Field(None, description="Meeting description")
    meeting_type: Optional[MeetingType] = Field(None, description="Type of meeting")
    meeting_date: Optional[datetime] = Field(None, description="Scheduled meeting date")
    participant_count: Optional[int] = Field(None, ge=1, description="Number of participants")
    platform: Optional[str] = Field(None, max_length=100, description="Meeting platform")
    meeting_url: Optional[str] = Field(None, max_length=500, description="Meeting URL")
    processing_status: Optional[ProcessingStatus] = Field(None, description="Processing status")


class MeetingResponse(BaseModel):
    """Response model for meeting data."""
    id: int
    title: str
    description: Optional[str]
    meeting_type: MeetingType
    created_at: datetime
    updated_at: datetime
    meeting_date: Optional[datetime]
    processing_status: ProcessingStatus
    duration_seconds: Optional[int]
    participant_count: Optional[int]
    platform: Optional[str]
    meeting_url: Optional[str]

    class Config:
        from_attributes = True


class MeetingDetailResponse(BaseModel):
    """Detailed response model for meeting with related data."""
    id: int
    title: str
    description: Optional[str]
    meeting_type: MeetingType
    created_at: datetime
    updated_at: datetime
    meeting_date: Optional[datetime]
    processing_status: ProcessingStatus
    duration_seconds: Optional[int]
    participant_count: Optional[int]
    platform: Optional[str]
    meeting_url: Optional[str]
    
    # Related data counts
    transcript_count: int
    speaker_count: int
    summary_count: int
    action_item_count: int

    class Config:
        from_attributes = True


class MeetingListResponse(BaseModel):
    """Response model for paginated meeting list."""
    meetings: List[MeetingResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int


# API endpoints
@router.post("/", response_model=MeetingResponse, status_code=201)
async def create_meeting(
    meeting_data: MeetingCreateRequest,
    db: Session = Depends(get_database_session)
):
    """Create a new meeting.
    
    Creates a new meeting record with the provided information.
    The meeting will initially have a status of PENDING.
    """
    try:
        # Create new meeting instance
        new_meeting = Meeting(
            title=meeting_data.title,
            description=meeting_data.description,
            meeting_type=meeting_data.meeting_type,
            meeting_date=meeting_data.meeting_date,
            participant_count=meeting_data.participant_count,
            platform=meeting_data.platform,
            meeting_url=meeting_data.meeting_url,
            processing_status=ProcessingStatus.PENDING
        )
        
        # Add to database
        db.add(new_meeting)
        db.commit()
        db.refresh(new_meeting)
        
        logger.info(f"Created new meeting: {new_meeting.id} - {new_meeting.title}")
        
        return MeetingResponse.model_validate(new_meeting)
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating meeting: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create meeting: {str(e)}")


@router.get("/", response_model=MeetingListResponse)
async def list_meetings(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of meetings per page"),
    status: Optional[ProcessingStatus] = Query(None, description="Filter by processing status"),
    meeting_type: Optional[MeetingType] = Query(None, description="Filter by meeting type"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    db: Session = Depends(get_database_session)
):
    """List meetings with optional filtering and pagination.
    
    Returns a paginated list of meetings with optional filters for:
    - Processing status
    - Meeting type
    - Platform
    """
    try:
        # Build query with filters
        query = db.query(Meeting)
        
        if status:
            query = query.filter(Meeting.processing_status == status)
        if meeting_type:
            query = query.filter(Meeting.meeting_type == meeting_type)
        if platform:
            query = query.filter(Meeting.platform == platform)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        meetings = query.order_by(Meeting.created_at.desc()).offset(offset).limit(page_size).all()
        
        # Calculate total pages
        total_pages = (total_count + page_size - 1) // page_size
        
        logger.info(f"Retrieved {len(meetings)} meetings (page {page}/{total_pages})")
        
        return MeetingListResponse(
            meetings=[MeetingResponse.model_validate(meeting) for meeting in meetings],
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error listing meetings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list meetings: {str(e)}")


@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
async def get_meeting(
    meeting_id: int,
    db: Session = Depends(get_database_session)
):
    """Get detailed information about a specific meeting.
    
    Returns complete meeting information including counts of related data
    (transcripts, speakers, summaries, action items).
    """
    try:
        # Get meeting by ID
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        
        if not meeting:
            raise HTTPException(status_code=404, detail=f"Meeting with ID {meeting_id} not found")
        
        # Get related data counts
        transcript_count = db.query(Transcript).filter(Transcript.meeting_id == meeting_id).count()
        speaker_count = db.query(Speaker).filter(Speaker.meeting_id == meeting_id).count()
        summary_count = db.query(MeetingSummary).filter(MeetingSummary.meeting_id == meeting_id).count()
        action_item_count = db.query(ActionItem).filter(ActionItem.meeting_id == meeting_id).count()
        
        logger.info(f"Retrieved meeting details: {meeting_id} - {meeting.title}")
        
        # Create response with related data counts
        meeting_dict = meeting.__dict__.copy()
        meeting_dict.update({
            "transcript_count": transcript_count,
            "speaker_count": speaker_count,
            "summary_count": summary_count,
            "action_item_count": action_item_count
        })
        
        return MeetingDetailResponse.model_validate(meeting_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving meeting {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve meeting: {str(e)}")


@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: int,
    meeting_data: MeetingUpdateRequest,
    db: Session = Depends(get_database_session)
):
    """Update an existing meeting.
    
    Updates the specified meeting with the provided data.
    Only fields that are provided will be updated.
    """
    try:
        # Get meeting by ID
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        
        if not meeting:
            raise HTTPException(status_code=404, detail=f"Meeting with ID {meeting_id} not found")
        
        # Update only provided fields
        update_data = meeting_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(meeting, field, value)
        
        # Commit changes
        db.commit()
        db.refresh(meeting)
        
        logger.info(f"Updated meeting: {meeting_id} - {meeting.title}")
        
        return MeetingResponse.model_validate(meeting)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating meeting {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update meeting: {str(e)}")


@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_database_session)
):
    """Delete a meeting and all related data.
    
    Permanently deletes the meeting and all associated data including:
    - Audio chunks
    - Transcripts
    - Speakers
    - Summaries
    - Action items
    
    This operation cannot be undone.
    """
    try:
        # Get meeting by ID
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        
        if not meeting:
            raise HTTPException(status_code=404, detail=f"Meeting with ID {meeting_id} not found")
        
        meeting_title = meeting.title
        
        # Delete meeting (cascade will handle related data)
        db.delete(meeting)
        db.commit()
        
        logger.info(f"Deleted meeting: {meeting_id} - {meeting_title}")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Meeting '{meeting_title}' and all related data deleted successfully",
                "deleted_meeting_id": meeting_id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting meeting {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete meeting: {str(e)}")


@router.get("/{meeting_id}/transcripts")
async def get_meeting_transcripts(
    meeting_id: int,
    db: Session = Depends(get_database_session)
):
    """Get all transcripts for a specific meeting."""
    try:
        # Verify meeting exists
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise HTTPException(status_code=404, detail=f"Meeting with ID {meeting_id} not found")
        
        # Get transcripts ordered by start time
        transcripts = (
            db.query(Transcript)
            .filter(Transcript.meeting_id == meeting_id)
            .order_by(Transcript.start_time)
            .all()
        )
        
        logger.info(f"Retrieved {len(transcripts)} transcripts for meeting {meeting_id}")
        
        return {
            "meeting_id": meeting_id,
            "meeting_title": meeting.title,
            "transcript_count": len(transcripts),
            "transcripts": [
                {
                    "id": t.id,
                    "text": t.text,
                    "start_time": t.start_time,
                    "end_time": t.end_time,
                    "confidence": t.confidence,
                    "speaker_id": t.speaker_id
                }
                for t in transcripts
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving transcripts for meeting {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve transcripts: {str(e)}")


@router.get("/{meeting_id}/speakers")
async def get_meeting_speakers(
    meeting_id: int,
    db: Session = Depends(get_database_session)
):
    """Get all speakers for a specific meeting."""
    try:
        # Verify meeting exists
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise HTTPException(status_code=404, detail=f"Meeting with ID {meeting_id} not found")
        
        # Get speakers
        speakers = db.query(Speaker).filter(Speaker.meeting_id == meeting_id).all()
        
        logger.info(f"Retrieved {len(speakers)} speakers for meeting {meeting_id}")
        
        return {
            "meeting_id": meeting_id,
            "meeting_title": meeting.title,
            "speaker_count": len(speakers),
            "speakers": [
                {
                    "id": s.id,
                    "speaker_label": s.speaker_label,
                    "speaker_name": s.speaker_name,
                    "total_speaking_time": s.total_speaking_time,
                    "word_count": s.word_count
                }
                for s in speakers
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving speakers for meeting {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve speakers: {str(e)}")


@router.get("/{meeting_id}/summaries")
async def get_meeting_summaries(
    meeting_id: int,
    db: Session = Depends(get_database_session)
):
    """Get all summaries for a specific meeting."""
    try:
        # Verify meeting exists
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise HTTPException(status_code=404, detail=f"Meeting with ID {meeting_id} not found")
        
        # Get summaries
        summaries = db.query(MeetingSummary).filter(MeetingSummary.meeting_id == meeting_id).all()
        
        logger.info(f"Retrieved {len(summaries)} summaries for meeting {meeting_id}")
        
        return {
            "meeting_id": meeting_id,
            "meeting_title": meeting.title,
            "summary_count": len(summaries),
            "summaries": [
                {
                    "id": s.id,
                    "summary_type": s.summary_type,
                    "summary_text": s.summary_text,
                    "key_topics": s.key_topics,
                    "insights": s.insights,
                    "model_used": s.model_used,
                    "confidence_score": s.confidence_score,
                    "created_at": s.created_at
                }
                for s in summaries
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving summaries for meeting {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve summaries: {str(e)}")


@router.get("/{meeting_id}/action-items")
async def get_meeting_action_items(
    meeting_id: int,
    db: Session = Depends(get_database_session)
):
    """Get all action items for a specific meeting."""
    try:
        # Verify meeting exists
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise HTTPException(status_code=404, detail=f"Meeting with ID {meeting_id} not found")
        
        # Get action items
        action_items = db.query(ActionItem).filter(ActionItem.meeting_id == meeting_id).all()
        
        logger.info(f"Retrieved {len(action_items)} action items for meeting {meeting_id}")
        
        return {
            "meeting_id": meeting_id,
            "meeting_title": meeting.title,
            "action_item_count": len(action_items),
            "action_items": [
                {
                    "id": ai.id,
                    "description": ai.description,
                    "assignee": ai.assignee,
                    "due_date": ai.due_date,
                    "priority": ai.priority,
                    "status": ai.status,
                    "context": ai.context,
                    "confidence_score": ai.confidence_score,
                    "extracted_by": ai.extracted_by,
                    "created_at": ai.created_at,
                    "updated_at": ai.updated_at
                }
                for ai in action_items
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving action items for meeting {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve action items: {str(e)}")