"""
Content Tasks Module

This module provides Celery tasks for content operations.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from celery import shared_task
from sqlalchemy.orm import Session

from app.core.content.scheduler import ContentScheduler
from app.db.session import SessionLocal


@shared_task
def process_due_content() -> List[Dict[str, Any]]:
    """
    Process all content that is due for posting.
    
    Returns:
        List of processed content items with status.
    """
    db = SessionLocal()
    try:
        scheduler = ContentScheduler(db)
        return scheduler.process_due_content()
    finally:
        db.close()


@shared_task
def generate_and_schedule_content(
    persona_id: int,
    content_type: str,
    topic: str,
    platform: str,
    scheduled_time_iso: str,
    additional_context: Optional[str] = None,
    max_length: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate content and schedule it for posting.
    
    Args:
        persona_id: ID of the persona to generate content for.
        content_type: Type of content to generate.
        topic: Topic to generate content about.
        platform: Platform to generate content for.
        scheduled_time_iso: When to post the content (ISO format).
        additional_context: Additional context for generation.
        max_length: Maximum length of the generated content.
        
    Returns:
        Information about the generated and scheduled content.
    """
    db = SessionLocal()
    try:
        scheduler = ContentScheduler(db)
        scheduled_time = datetime.fromisoformat(scheduled_time_iso)
        content = scheduler.generate_and_schedule(
            persona_id=persona_id,
            content_type=content_type,
            topic=topic,
            platform=platform,
            scheduled_time=scheduled_time,
            additional_context=additional_context,
            max_length=max_length,
        )
        
        return {
            "content_id": content.id,
            "persona_id": content.persona_id,
            "content_type": content.content_type,
            "platform": content.platform,
            "scheduled_time": content.scheduled_time.isoformat() if content.scheduled_time else None,
            "status": content.status,
        }
    finally:
        db.close()


@shared_task
def generate_batch_and_schedule(
    persona_id: int,
    content_type: str,
    topics: List[str],
    platform: str,
    start_time_iso: str,
    interval_minutes: int = 60,
    additional_context: Optional[str] = None,
    max_length: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Generate multiple content items and schedule them with regular intervals.
    
    Args:
        persona_id: ID of the persona to generate content for.
        content_type: Type of content to generate.
        topics: List of topics to generate content about.
        platform: Platform to generate content for.
        start_time_iso: When to post the first content (ISO format).
        interval_minutes: Minutes between each post.
        additional_context: Additional context for generation.
        max_length: Maximum length of the generated content.
        
    Returns:
        List of information about the generated and scheduled content.
    """
    db = SessionLocal()
    try:
        scheduler = ContentScheduler(db)
        start_time = datetime.fromisoformat(start_time_iso)
        contents = scheduler.generate_batch_and_schedule(
            persona_id=persona_id,
            content_type=content_type,
            topics=topics,
            platform=platform,
            start_time=start_time,
            interval_minutes=interval_minutes,
            additional_context=additional_context,
            max_length=max_length,
        )
        
        return [
            {
                "content_id": content.id,
                "persona_id": content.persona_id,
                "content_type": content.content_type,
                "platform": content.platform,
                "scheduled_time": content.scheduled_time.isoformat() if content.scheduled_time else None,
                "status": content.status,
            }
            for content in contents
        ]
    finally:
        db.close()


@shared_task
def schedule_batch(
    content_ids: List[int],
    start_time_iso: str,
    interval_minutes: int = 60,
) -> List[Dict[str, Any]]:
    """
    Schedule multiple content items with regular intervals.
    
    Args:
        content_ids: List of content IDs to schedule.
        start_time_iso: When to post the first content (ISO format).
        interval_minutes: Minutes between each post.
        
    Returns:
        List of information about the scheduled content.
    """
    db = SessionLocal()
    try:
        scheduler = ContentScheduler(db)
        start_time = datetime.fromisoformat(start_time_iso)
        contents = scheduler.schedule_batch(
            content_ids=content_ids,
            start_time=start_time,
            interval_minutes=interval_minutes,
        )
        
        return [
            {
                "content_id": content.id,
                "persona_id": content.persona_id,
                "content_type": content.content_type,
                "platform": content.platform,
                "scheduled_time": content.scheduled_time.isoformat() if content.scheduled_time else None,
                "status": content.status,
            }
            for content in contents
        ]
    finally:
        db.close()
