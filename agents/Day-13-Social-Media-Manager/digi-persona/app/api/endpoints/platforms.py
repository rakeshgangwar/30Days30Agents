"""
Platforms API Endpoints Module

This module provides API endpoints for managing platform connections.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.personas.context import persona_context
from app.core.platforms.manager import PlatformManager, get_platform_manager
from app.db.models.platform import PlatformConnection
from app.api.endpoints.metrics import update_platform_connection_count
from app.schemas.platform import (
    PlatformConnectionCreate,
    PlatformConnectionResponse,
    PlatformConnectionList,
    PlatformAccountInfo,
    PlatformPostCreate,
    PlatformPostResponse
)

router = APIRouter()

@router.get("/", response_model=PlatformConnectionList)
def get_platform_connections(
    active_only: bool = Query(True, description="Whether to only return active connections"),
    db: Session = Depends(get_db),
    platform_manager: PlatformManager = Depends(lambda: get_platform_manager(next(get_db()))),
):
    """
    Get platform connections for the current persona.

    Args:
        active_only: Whether to only return active connections.
        db: The database session.
        platform_manager: The platform manager.

    Returns:
        List of platform connections.
    """
    persona_id = persona_context.require_persona()
    connections = platform_manager.get_platform_connections(persona_id, active_only)

    # Format the response
    items = []
    for conn in connections:
        # Extract relevant metrics from platform_metadata
        metadata = conn.platform_metadata or {}
        follower_count = metadata.get('follower_count', 0)
        following_count = metadata.get('following_count', 0) or metadata.get('connection_count', 0)
        post_count = metadata.get('tweet_count', 0) or metadata.get('post_count', 0) or metadata.get('posts_count', 0)

        items.append({
            "id": conn.id,
            "persona_id": conn.persona_id,
            "platform_name": conn.platform_name,
            "platform_id": conn.platform_id,
            "username": conn.username,
            "is_active": conn.is_active,
            "created_at": conn.created_at,
            "updated_at": conn.updated_at,
            "metrics": {
                "follower_count": follower_count,
                "following_count": following_count,
                "post_count": post_count
            }
        })

    return {"items": items, "total": len(items)}

@router.get("/{platform_connection_id}", response_model=PlatformConnectionResponse)
def get_platform_connection(
    platform_connection_id: int = Path(..., description="The ID of the platform connection"),
    db: Session = Depends(get_db),
):
    """
    Get a platform connection by ID.

    Args:
        platform_connection_id: The ID of the platform connection.
        db: The database session.

    Returns:
        The platform connection.

    Raises:
        HTTPException: If the platform connection is not found.
    """
    persona_id = persona_context.require_persona()
    connection = db.query(PlatformConnection).filter(
        PlatformConnection.id == platform_connection_id,
        PlatformConnection.persona_id == persona_id
    ).first()

    if not connection:
        raise HTTPException(status_code=404, detail="Platform connection not found")

    # Extract relevant metrics from platform_metadata
    metadata = connection.platform_metadata or {}
    follower_count = metadata.get('follower_count', 0)
    following_count = metadata.get('following_count', 0) or metadata.get('connection_count', 0)
    post_count = metadata.get('tweet_count', 0) or metadata.get('post_count', 0) or metadata.get('posts_count', 0)

    return {
        "id": connection.id,
        "persona_id": connection.persona_id,
        "platform_name": connection.platform_name,
        "platform_id": connection.platform_id,
        "username": connection.username,
        "is_active": connection.is_active,
        "created_at": connection.created_at,
        "updated_at": connection.updated_at,
        "metrics": {
            "follower_count": follower_count,
            "following_count": following_count,
            "post_count": post_count
        }
    }

@router.post("/connect", response_model=PlatformConnectionResponse, status_code=201)
def connect_platform(
    platform_data: PlatformConnectionCreate,
    db: Session = Depends(get_db),
    platform_manager: PlatformManager = Depends(lambda: get_platform_manager(next(get_db()))),
):
    """
    Connect a platform for the current persona.

    Args:
        platform_data: The platform connection data.
        db: The database session.
        platform_manager: The platform manager.

    Returns:
        The created platform connection.

    Raises:
        HTTPException: If authentication fails.
    """
    persona_id = persona_context.require_persona()

    try:
        connection = platform_manager.connect_platform(
            persona_id=persona_id,
            platform_name=platform_data.platform_name,
            credentials=platform_data.credentials,
            username=platform_data.username
        )

        # Extract relevant metrics from platform_metadata
        metadata = connection.platform_metadata or {}
        follower_count = metadata.get('follower_count', 0)
        following_count = metadata.get('following_count', 0) or metadata.get('connection_count', 0)
        post_count = metadata.get('tweet_count', 0) or metadata.get('post_count', 0) or metadata.get('posts_count', 0)

        # Update platform connection count in metrics
        platform_count = db.query(PlatformConnection).filter(
            PlatformConnection.platform_name == platform_data.platform_name
        ).count()
        update_platform_connection_count(platform_data.platform_name, platform_count)

        return {
            "id": connection.id,
            "persona_id": connection.persona_id,
            "platform_name": connection.platform_name,
            "platform_id": connection.platform_id,
            "username": connection.username,
            "is_active": connection.is_active,
            "created_at": connection.created_at,
            "updated_at": connection.updated_at,
            "metrics": {
                "follower_count": follower_count,
                "following_count": following_count,
                "post_count": post_count
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{platform_connection_id}/disconnect", status_code=200)
def disconnect_platform(
    platform_connection_id: int = Path(..., description="The ID of the platform connection"),
    db: Session = Depends(get_db),
    platform_manager: PlatformManager = Depends(lambda: get_platform_manager(next(get_db()))),
):
    """
    Disconnect a platform for the current persona.

    Args:
        platform_connection_id: The ID of the platform connection.
        db: The database session.
        platform_manager: The platform manager.

    Returns:
        Success message.

    Raises:
        HTTPException: If the platform connection is not found.
    """
    persona_id = persona_context.require_persona()
    success = platform_manager.disconnect_platform(persona_id, platform_connection_id)

    if not success:
        raise HTTPException(status_code=404, detail="Platform connection not found")

    return {"message": "Platform disconnected successfully"}

@router.get("/{platform_connection_id}/account-info", response_model=PlatformAccountInfo)
def get_platform_account_info(
    platform_connection_id: int = Path(..., description="The ID of the platform connection"),
    db: Session = Depends(get_db),
):
    """
    Get account information for a platform connection.

    Args:
        platform_connection_id: The ID of the platform connection.
        db: The database session.

    Returns:
        The platform account information.

    Raises:
        HTTPException: If the platform connection is not found.
    """
    persona_id = persona_context.require_persona()
    connection = db.query(PlatformConnection).filter(
        PlatformConnection.id == platform_connection_id,
        PlatformConnection.persona_id == persona_id
    ).first()

    if not connection:
        raise HTTPException(status_code=404, detail="Platform connection not found")

    if not connection.is_active:
        raise HTTPException(status_code=400, detail="Platform connection is not active")

    platform_manager = get_platform_manager(db)

    try:
        account_info = platform_manager.get_account_info(persona_id, connection.platform_name)

        # Update platform metadata
        connection.platform_metadata = account_info
        db.commit()

        return {
            "platform_connection_id": connection.id,
            "platform_name": connection.platform_name,
            "platform_id": connection.platform_id,
            "username": connection.username,
            **account_info
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{platform_connection_id}/post", response_model=PlatformPostResponse)
def post_to_platform(
    post_data: PlatformPostCreate,
    platform_connection_id: int = Path(..., description="The ID of the platform connection"),
    db: Session = Depends(get_db),
    platform_manager: PlatformManager = Depends(lambda: get_platform_manager(next(get_db()))),
):
    """
    Post content to a platform.

    Args:
        post_data: The post data.
        platform_connection_id: The ID of the platform connection.
        db: The database session.
        platform_manager: The platform manager.

    Returns:
        Information about the created post.

    Raises:
        HTTPException: If the platform connection is not found or posting fails.
    """
    persona_id = persona_context.require_persona()
    connection = db.query(PlatformConnection).filter(
        PlatformConnection.id == platform_connection_id,
        PlatformConnection.persona_id == persona_id
    ).first()

    if not connection:
        raise HTTPException(status_code=404, detail="Platform connection not found")

    if not connection.is_active:
        raise HTTPException(status_code=400, detail="Platform connection is not active")

    try:
        post_info = platform_manager.post_content(
            persona_id=persona_id,
            platform_name=connection.platform_name,
            content=post_data.content,
            media_urls=post_data.media_urls,
            **post_data.additional_params
        )

        return {
            "platform_connection_id": connection.id,
            "platform_name": connection.platform_name,
            "created_at": post_info.get('created_at', ''),
            "external_id": post_info.get('id', ''),
            "external_url": post_info.get('url', ''),
            **post_info
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{platform_connection_id}/sync", status_code=200)
def sync_platform(
    platform_connection_id: int = Path(..., description="The ID of the platform connection"),
    db: Session = Depends(get_db),
    platform_manager: PlatformManager = Depends(lambda: get_platform_manager(next(get_db()))),
):
    """
    Sync platform data (account info, etc.).

    Args:
        platform_connection_id: The ID of the platform connection.
        db: The database session.
        platform_manager: The platform manager.

    Returns:
        Success message.

    Raises:
        HTTPException: If the platform connection is not found or sync fails.
    """
    persona_id = persona_context.require_persona()
    connection = db.query(PlatformConnection).filter(
        PlatformConnection.id == platform_connection_id,
        PlatformConnection.persona_id == persona_id
    ).first()

    if not connection:
        raise HTTPException(status_code=404, detail="Platform connection not found")

    if not connection.is_active:
        raise HTTPException(status_code=400, detail="Platform connection is not active")

    try:
        # Get and update account info
        account_info = platform_manager.get_account_info(persona_id, connection.platform_name)
        connection.platform_metadata = account_info
        db.commit()

        return {"message": "Platform data synced successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
