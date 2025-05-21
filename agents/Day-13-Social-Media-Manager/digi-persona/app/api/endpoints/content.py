"""
Content API Endpoints Module

This module provides API endpoints for managing content.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from app.core.content.manager import ContentManager, get_content_manager
from app.core.content.scheduler import ContentScheduler, get_content_scheduler
from app.core.personas.context import persona_context
from app.db.session import get_db
from app.api.endpoints.metrics import track_content_creation
from app.schemas.content import (
    ContentCreate,
    ContentUpdate,
    ContentResponse,
    ContentList,
    ContentGenerateRequest,
    ContentGenerateResponse,
    ContentScheduleRequest,
    ContentScheduleResponse,
)

router = APIRouter()


@router.post("/", response_model=ContentResponse, status_code=201)
def create_content(
    content: ContentCreate,
    db: Session = Depends(get_db),
    content_manager: ContentManager = Depends(lambda db=Depends(get_db): get_content_manager(db)),
) -> ContentResponse:
    """
    Create a new content item.

    Args:
        content: The content data.
        db: The database session.
        content_manager: The content manager.

    Returns:
        The created content item.
    """
    created_content = content_manager.create_content(content.model_dump())

    # Track content creation in metrics
    track_content_creation(
        persona_id=created_content.persona_id,
        platform=created_content.platform,
        status=created_content.status
    )

    # Convert SQLAlchemy model to dictionary
    content_dict = {
        "id": created_content.id,
        "persona_id": created_content.persona_id,
        "content_type": created_content.content_type,
        "text": created_content.text,
        "platform": created_content.platform,
        "status": created_content.status,
        "scheduled_time": created_content.scheduled_time,
        "published_time": created_content.published_time,
        "external_id": created_content.external_id,
        "media_urls": created_content.media_urls,
        "metadata": created_content.content_metadata if hasattr(created_content, 'content_metadata') else (created_content.metadata if hasattr(created_content, 'metadata') else {}),
        "created_at": created_content.created_at,
        "updated_at": created_content.updated_at
    }

    return ContentResponse(**content_dict)


@router.get("/{content_id}", response_model=ContentResponse)
def get_content(
    content_id: int = Path(..., description="The ID of the content item to get"),
    db: Session = Depends(get_db),
    content_manager: ContentManager = Depends(lambda db=Depends(get_db): get_content_manager(db)),
) -> ContentResponse:
    """
    Get a content item by ID.

    Args:
        content_id: The ID of the content item to get.
        db: The database session.
        content_manager: The content manager.

    Returns:
        The content item.

    Raises:
        HTTPException: If the content item is not found.
    """
    content = content_manager.get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Convert SQLAlchemy model to dictionary
    content_dict = {
        "id": content.id,
        "persona_id": content.persona_id,
        "content_type": content.content_type,
        "text": content.text,
        "platform": content.platform,
        "status": content.status,
        "scheduled_time": content.scheduled_time,
        "published_time": content.published_time,
        "external_id": content.external_id,
        "media_urls": content.media_urls,
        "metadata": content.content_metadata if hasattr(content, 'content_metadata') else (content.metadata if hasattr(content, 'metadata') else {}),
        "created_at": content.created_at,
        "updated_at": content.updated_at
    }

    return ContentResponse(**content_dict)


@router.get("/", response_model=ContentList)
def get_content_items(
    persona_id: Optional[int] = Query(None, description="Filter by persona ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, description="Number of content items to skip"),
    limit: int = Query(100, description="Maximum number of content items to return"),
    db: Session = Depends(get_db),
    content_manager: ContentManager = Depends(lambda db=Depends(get_db): get_content_manager(db)),
) -> ContentList:
    """
    Get a list of content items.

    Args:
        persona_id: Filter by persona ID.
        platform: Filter by platform.
        content_type: Filter by content type.
        status: Filter by status.
        skip: Number of content items to skip.
        limit: Maximum number of content items to return.
        db: The database session.
        content_manager: The content manager.

    Returns:
        List of content items.
    """
    # Use persona ID from context if not provided
    if persona_id is None:
        persona_id = persona_context.get_persona()

    content_items = content_manager.get_content_items(
        persona_id=persona_id,
        platform=platform,
        content_type=content_type,
        status=status,
        skip=skip,
        limit=limit,
    )

    total = len(content_items)  # In a real implementation, this would be a separate count query

    # Convert SQLAlchemy models to dictionaries
    content_items_dict = []
    for item in content_items:
        item_dict = {
            "id": item.id,
            "persona_id": item.persona_id,
            "content_type": item.content_type,
            "text": item.text,
            "platform": item.platform,
            "status": item.status,
            "scheduled_time": item.scheduled_time,
            "published_time": item.published_time,
            "external_id": item.external_id,
            "media_urls": item.media_urls,
            "metadata": item.content_metadata if hasattr(item, 'content_metadata') else (item.metadata if hasattr(item, 'metadata') else {}),
            "created_at": item.created_at,
            "updated_at": item.updated_at
        }
        content_items_dict.append(item_dict)

    return ContentList(items=content_items_dict, total=total, skip=skip, limit=limit)


def safe_metadata(obj):
    val = getattr(obj, 'content_metadata', None)
    if isinstance(val, dict):
        return val
    val = getattr(obj, 'metadata', None)
    if isinstance(val, dict):
        return val
    return {}


@router.put("/{content_id}", response_model=ContentResponse)
def update_content(
    content: ContentUpdate,
    content_id: int = Path(..., description="The ID of the content item to update"),
    db: Session = Depends(get_db),
    content_manager: ContentManager = Depends(lambda db=Depends(get_db): get_content_manager(db)),
) -> ContentResponse:
    """
    Update a content item.

    Args:
        content: The updated content data.
        content_id: The ID of the content item to update.
        db: The database session.
        content_manager: The content manager.

    Returns:
        The updated content item.

    Raises:
        HTTPException: If the content item is not found.
    """
    updated_content = content_manager.update_content(content_id, content.model_dump(exclude_unset=True))
    if not updated_content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Convert SQLAlchemy model to dictionary
    content_dict = {
        "id": updated_content.id,
        "persona_id": updated_content.persona_id,
        "content_type": updated_content.content_type,
        "text": updated_content.text,
        "platform": updated_content.platform,
        "status": updated_content.status,
        "scheduled_time": updated_content.scheduled_time,
        "published_time": updated_content.published_time,
        "external_id": updated_content.external_id,
        "media_urls": updated_content.media_urls,
        "metadata": safe_metadata(updated_content),
        "created_at": updated_content.created_at,
        "updated_at": updated_content.updated_at
    }

    return ContentResponse(**content_dict)


@router.delete("/{content_id}", status_code=204)
def delete_content(
    content_id: int = Path(..., description="The ID of the content item to delete"),
    db: Session = Depends(get_db),
    content_manager: ContentManager = Depends(lambda db=Depends(get_db): get_content_manager(db)),
) -> None:
    """
    Delete a content item.

    Args:
        content_id: The ID of the content item to delete.
        db: The database session.
        content_manager: The content manager.

    Raises:
        HTTPException: If the content item is not found.
    """
    success = content_manager.delete_content(content_id)
    if not success:
        raise HTTPException(status_code=404, detail="Content not found")


@router.post("/generate", response_model=ContentGenerateResponse)
def generate_content(
    request: ContentGenerateRequest,
    db: Session = Depends(get_db),
    content_manager: ContentManager = Depends(lambda db=Depends(get_db): get_content_manager(db)),
) -> ContentGenerateResponse:
    """
    Generate content for a persona.

    Args:
        request: The content generation request.
        db: The database session.
        content_manager: The content manager.

    Returns:
        The generated content.

    Raises:
        HTTPException: If the persona is not found.
    """
    try:
        content_data = content_manager.generate_content(
            persona_id=request.persona_id,
            content_type=request.content_type,
            topic=request.topic,
            platform=request.platform,
            additional_context=request.additional_context,
            max_length=request.max_length,
            save=request.save,
        )
        return ContentGenerateResponse(**content_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{content_id}/approve")
def approve_content(
    content_id: int = Path(..., description="The ID of the content item to approve"),
    db: Session = Depends(get_db),
    content_manager: ContentManager = Depends(lambda db=Depends(get_db): get_content_manager(db)),
):
    """
    Approve a content item.

    Args:
        content_id: The ID of the content item to approve.
        db: The database session.
        content_manager: The content manager.

    Returns:
        The approved content item.

    Raises:
        HTTPException: If the content item is not found.
    """
    content = content_manager.approve_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Convert the SQLAlchemy model to a dictionary
    content_dict = {
        "id": content.id,
        "persona_id": content.persona_id,
        "content_type": content.content_type,
        "text": content.text,
        "platform": content.platform,
        "status": content.status,
        "scheduled_time": content.scheduled_time,
        "published_time": content.published_time,
        "external_id": content.external_id,
        "media_urls": content.media_urls,
        "content_metadata": content.content_metadata,
        "created_at": content.created_at,
        "updated_at": content.updated_at
    }

    return content_dict


@router.post("/{content_id}/publish")
def publish_content(
    content_id: int = Path(..., description="The ID of the content item to publish"),
    db: Session = Depends(get_db),
    content_manager: ContentManager = Depends(lambda db=Depends(get_db): get_content_manager(db)),
):
    """
    Mark a content item as published.

    Args:
        content_id: The ID of the content item to mark as published.
        db: The database session.
        content_manager: The content manager.

    Returns:
        The published content item.

    Raises:
        HTTPException: If the content item is not found.
    """
    content = content_manager.publish_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Convert the SQLAlchemy model to a dictionary
    content_dict = {
        "id": content.id,
        "persona_id": content.persona_id,
        "content_type": content.content_type,
        "text": content.text,
        "platform": content.platform,
        "status": content.status,
        "scheduled_time": content.scheduled_time,
        "published_time": content.published_time,
        "external_id": content.external_id,
        "media_urls": content.media_urls,
        "content_metadata": content.content_metadata,
        "created_at": content.created_at,
        "updated_at": content.updated_at
    }

    return content_dict


@router.post("/{content_id}/schedule")
def schedule_content(
    request: ContentScheduleRequest,
    content_id: int = Path(..., description="The ID of the content item to schedule"),
    db: Session = Depends(get_db),
    content_manager: ContentManager = Depends(lambda db=Depends(get_db): get_content_manager(db)),
):
    """
    Schedule a content item for posting.

    Args:
        request: The scheduling request.
        content_id: The ID of the content item to schedule.
        db: The database session.
        content_manager: The content manager.

    Returns:
        The scheduled content item.

    Raises:
        HTTPException: If the content item is not found.
    """
    content = content_manager.schedule_content(content_id, request.scheduled_time)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Convert the SQLAlchemy model to a dictionary
    content_dict = {
        "id": content.id,
        "persona_id": content.persona_id,
        "content_type": content.content_type,
        "text": content.text,
        "platform": content.platform,
        "status": content.status,
        "scheduled_time": content.scheduled_time,
        "published_time": content.published_time,
        "external_id": content.external_id,
        "media_urls": content.media_urls,
        "content_metadata": content.content_metadata,
        "created_at": content.created_at,
        "updated_at": content.updated_at
    }

    return content_dict


@router.get("/list/due")
def get_due_content(
    db: Session = Depends(get_db),
    content_scheduler: ContentScheduler = Depends(lambda db=Depends(get_db): get_content_scheduler(db)),
):
    """
    Get content that is due for posting.

    Args:
        db: The database session.
        content_scheduler: The content scheduler.

    Returns:
        List of content items that are due for posting.
    """
    content_items = content_scheduler.get_due_content()

    # Convert the SQLAlchemy models to dictionaries
    result = []
    for content in content_items:
        content_dict = {
            "id": content.id,
            "persona_id": content.persona_id,
            "content_type": content.content_type,
            "text": content.text,
            "platform": content.platform,
            "status": content.status,
            "scheduled_time": content.scheduled_time,
            "published_time": content.published_time,
            "external_id": content.external_id,
            "media_urls": content.media_urls,
            "content_metadata": content.content_metadata,
            "created_at": content.created_at,
            "updated_at": content.updated_at
        }
        result.append(content_dict)

    return result


@router.get("/list/upcoming")
def get_upcoming_content(
    persona_id: Optional[int] = Query(None, description="Filter by persona ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    hours_ahead: int = Query(24, description="Number of hours ahead to look"),
    db: Session = Depends(get_db),
    content_scheduler: ContentScheduler = Depends(lambda db=Depends(get_db): get_content_scheduler(db)),
):
    """
    Get content that is scheduled for posting in the near future.

    Args:
        persona_id: Filter by persona ID.
        platform: Filter by platform.
        hours_ahead: Number of hours ahead to look.
        db: The database session.
        content_scheduler: The content scheduler.

    Returns:
        List of content items scheduled for posting in the near future.
    """
    # Use persona ID from context if not provided
    if persona_id is None:
        persona_id = persona_context.get_persona()

    content_items = content_scheduler.get_upcoming_content(
        persona_id=persona_id,
        platform=platform,
        hours_ahead=hours_ahead,
    )

    # Convert the SQLAlchemy models to dictionaries
    result = []
    for content in content_items:
        content_dict = {
            "id": content.id,
            "persona_id": content.persona_id,
            "content_type": content.content_type,
            "text": content.text,
            "platform": content.platform,
            "status": content.status,
            "scheduled_time": content.scheduled_time,
            "published_time": content.published_time,
            "external_id": content.external_id,
            "media_urls": content.media_urls,
            "content_metadata": content.content_metadata,
            "created_at": content.created_at,
            "updated_at": content.updated_at
        }
        result.append(content_dict)

    return result
