"""
Scheduling API Endpoints

This module provides API endpoints for content scheduling.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.content.scheduler import ContentScheduler, get_content_scheduler
from app.core.tasks.content_tasks import (
    generate_and_schedule_content,
    generate_batch_and_schedule,
    schedule_batch,
)
from app.schemas.content import (
    ContentResponse,
    ContentScheduleRequest,
    ContentBatchScheduleRequest,
    ContentGenerateScheduleRequest,
    ContentBatchGenerateScheduleRequest,
)

router = APIRouter()


@router.post("/content/{content_id}/schedule", response_model=ContentResponse)
def schedule_content(
    content_id: int,
    schedule_data: ContentScheduleRequest,
    db: Session = Depends(get_db),
):
    """
    Schedule a content item for posting.
    """
    scheduler = get_content_scheduler(db)
    content = scheduler.reschedule_content(content_id, schedule_data.scheduled_time)
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return content


@router.post("/content/batch/schedule", response_model=List[ContentResponse])
def schedule_content_batch(
    schedule_data: ContentBatchScheduleRequest,
    db: Session = Depends(get_db),
):
    """
    Schedule multiple content items with regular intervals.
    """
    # For immediate scheduling, use the database directly
    if schedule_data.use_celery:
        # Use Celery for background processing
        task = schedule_batch.delay(
            content_ids=schedule_data.content_ids,
            start_time_iso=schedule_data.start_time.isoformat(),
            interval_minutes=schedule_data.interval_minutes,
        )
        return {"task_id": task.id, "status": "scheduled"}
    else:
        # Process immediately
        scheduler = get_content_scheduler(db)
        contents = scheduler.schedule_batch(
            content_ids=schedule_data.content_ids,
            start_time=schedule_data.start_time,
            interval_minutes=schedule_data.interval_minutes,
        )
        return contents


@router.post("/content/generate/schedule", response_model=ContentResponse)
def generate_and_schedule(
    data: ContentGenerateScheduleRequest,
    db: Session = Depends(get_db),
):
    """
    Generate content and schedule it for posting.
    """
    if data.use_celery:
        # Use Celery for background processing
        task = generate_and_schedule_content.delay(
            persona_id=data.persona_id,
            content_type=data.content_type,
            topic=data.topic,
            platform=data.platform,
            scheduled_time_iso=data.scheduled_time.isoformat(),
            additional_context=data.additional_context,
            max_length=data.max_length,
        )
        return {"task_id": task.id, "status": "scheduled"}
    else:
        # Process immediately
        scheduler = get_content_scheduler(db)
        content = scheduler.generate_and_schedule(
            persona_id=data.persona_id,
            content_type=data.content_type,
            topic=data.topic,
            platform=data.platform,
            scheduled_time=data.scheduled_time,
            additional_context=data.additional_context,
            max_length=data.max_length,
        )
        return content


@router.post("/content/generate/batch/schedule", response_model=List[ContentResponse])
def generate_batch_and_schedule_endpoint(
    data: ContentBatchGenerateScheduleRequest,
    db: Session = Depends(get_db),
):
    """
    Generate multiple content items and schedule them with regular intervals.
    """
    if data.use_celery:
        # Use Celery for background processing
        task = generate_batch_and_schedule.delay(
            persona_id=data.persona_id,
            content_type=data.content_type,
            topics=data.topics,
            platform=data.platform,
            start_time_iso=data.start_time.isoformat(),
            interval_minutes=data.interval_minutes,
            additional_context=data.additional_context,
            max_length=data.max_length,
        )
        return {"task_id": task.id, "status": "scheduled"}
    else:
        # Process immediately
        scheduler = get_content_scheduler(db)
        contents = scheduler.generate_batch_and_schedule(
            persona_id=data.persona_id,
            content_type=data.content_type,
            topics=data.topics,
            platform=data.platform,
            start_time=data.start_time,
            interval_minutes=data.interval_minutes,
            additional_context=data.additional_context,
            max_length=data.max_length,
        )
        return contents


@router.get("/content/upcoming", response_model=List[ContentResponse])
def get_upcoming_content(
    hours_ahead: int = Query(24, description="Number of hours to look ahead"),
    persona_id: Optional[int] = Query(None, description="Filter by persona ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    db: Session = Depends(get_db),
):
    """
    Get content scheduled for the next X hours.
    """
    scheduler = get_content_scheduler(db)
    return scheduler.get_upcoming_content(
        hours_ahead=hours_ahead,
        persona_id=persona_id,
        platform=platform,
    )
