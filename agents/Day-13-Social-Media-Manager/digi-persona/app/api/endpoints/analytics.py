"""
Analytics API Endpoints Module

This module provides API endpoints for analytics data.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.content import Content
from app.db.models.interaction import Interaction
from app.db.models.persona import Persona
from app.schemas.analytics import (
    EngagementData,
    ContentTypeData,
    InteractionTypeData,
    PlatformData,
    PersonaPerformanceData,
    AnalyticsTimeRange,
    AnalyticsResponse,
)

router = APIRouter()


@router.get("/engagement", response_model=EngagementData)
async def get_engagement_data(
    persona_id: Optional[int] = Query(None, description="Filter by persona ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    time_range: AnalyticsTimeRange = Query(AnalyticsTimeRange.TWO_WEEKS, description="Time range for analytics"),
    db: Session = Depends(get_db),
) -> EngagementData:
    """
    Get engagement data over time.

    Args:
        persona_id: Optional persona ID to filter by
        platform: Optional platform to filter by
        time_range: Time range for analytics
        db: Database session

    Returns:
        Engagement data over time
    """
    # Calculate date range based on time_range
    end_date = datetime.now(timezone.utc)

    if time_range == AnalyticsTimeRange.ONE_WEEK:
        start_date = end_date - timedelta(days=7)
    elif time_range == AnalyticsTimeRange.TWO_WEEKS:
        start_date = end_date - timedelta(days=14)
    elif time_range == AnalyticsTimeRange.ONE_MONTH:
        start_date = end_date - timedelta(days=30)
    elif time_range == AnalyticsTimeRange.THREE_MONTHS:
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=14)  # Default to 2 weeks

    # Base query for interactions
    query = db.query(
        func.date(Interaction.created_at).label("date"),
        Interaction.platform,
        func.count().label("count")
    ).filter(
        Interaction.created_at >= start_date,
        Interaction.created_at <= end_date
    )

    # Apply filters if provided
    if persona_id:
        query = query.filter(Interaction.persona_id == persona_id)

    if platform:
        query = query.filter(Interaction.platform == platform)

    # Group by date and platform
    query = query.group_by(
        func.date(Interaction.created_at),
        Interaction.platform
    ).order_by(
        func.date(Interaction.created_at)
    )

    # Execute query
    results = query.all()

    # Process results into the format expected by the frontend
    data_by_date = {}
    platforms = set()

    for result in results:
        date_str = result.date.strftime("%Y-%m-%d")
        platform = result.platform
        count = result.count

        if date_str not in data_by_date:
            data_by_date[date_str] = {"date": date_str}

        data_by_date[date_str][platform] = count
        platforms.add(platform)

    # Ensure all platforms have a value for each date
    for date_str, data in data_by_date.items():
        for platform in platforms:
            if platform not in data:
                data[platform] = 0

    # Convert to list sorted by date
    engagement_data = sorted(data_by_date.values(), key=lambda x: x["date"])

    return EngagementData(data=engagement_data)


@router.get("/content-types", response_model=ContentTypeData)
async def get_content_type_data(
    persona_id: Optional[int] = Query(None, description="Filter by persona ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    time_range: AnalyticsTimeRange = Query(AnalyticsTimeRange.TWO_WEEKS, description="Time range for analytics"),
    db: Session = Depends(get_db),
) -> ContentTypeData:
    """
    Get content distribution by type.

    Args:
        persona_id: Optional persona ID to filter by
        platform: Optional platform to filter by
        time_range: Time range for analytics
        db: Database session

    Returns:
        Content distribution by type
    """
    # Calculate date range based on time_range
    end_date = datetime.now(timezone.utc)

    if time_range == AnalyticsTimeRange.ONE_WEEK:
        start_date = end_date - timedelta(days=7)
    elif time_range == AnalyticsTimeRange.TWO_WEEKS:
        start_date = end_date - timedelta(days=14)
    elif time_range == AnalyticsTimeRange.ONE_MONTH:
        start_date = end_date - timedelta(days=30)
    elif time_range == AnalyticsTimeRange.THREE_MONTHS:
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=14)  # Default to 2 weeks

    # Query for content types
    query = db.query(
        Content.content_type,
        func.count().label("count")
    ).filter(
        Content.created_at >= start_date,
        Content.created_at <= end_date
    )

    # Apply filters if provided
    if persona_id:
        query = query.filter(Content.persona_id == persona_id)

    if platform:
        query = query.filter(Content.platform == platform)

    # Group by content type
    query = query.group_by(Content.content_type)

    # Execute query
    results = query.all()

    # Process results
    content_type_data = [
        {"name": result.content_type, "value": result.count}
        for result in results
    ]

    return ContentTypeData(data=content_type_data)


@router.get("/interaction-types", response_model=InteractionTypeData)
async def get_interaction_type_data(
    persona_id: Optional[int] = Query(None, description="Filter by persona ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    time_range: AnalyticsTimeRange = Query(AnalyticsTimeRange.TWO_WEEKS, description="Time range for analytics"),
    db: Session = Depends(get_db),
) -> InteractionTypeData:
    """
    Get interaction distribution by type.

    Args:
        persona_id: Optional persona ID to filter by
        platform: Optional platform to filter by
        time_range: Time range for analytics
        db: Database session

    Returns:
        Interaction distribution by type
    """
    # Calculate date range based on time_range
    end_date = datetime.now(timezone.utc)

    if time_range == AnalyticsTimeRange.ONE_WEEK:
        start_date = end_date - timedelta(days=7)
    elif time_range == AnalyticsTimeRange.TWO_WEEKS:
        start_date = end_date - timedelta(days=14)
    elif time_range == AnalyticsTimeRange.ONE_MONTH:
        start_date = end_date - timedelta(days=30)
    elif time_range == AnalyticsTimeRange.THREE_MONTHS:
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=14)  # Default to 2 weeks

    # Query for interaction types
    query = db.query(
        Interaction.type,
        func.count().label("count")
    ).filter(
        Interaction.created_at >= start_date,
        Interaction.created_at <= end_date
    )

    # Apply filters if provided
    if persona_id:
        query = query.filter(Interaction.persona_id == persona_id)

    if platform:
        query = query.filter(Interaction.platform == platform)

    # Group by interaction type
    query = query.group_by(Interaction.type)

    # Execute query
    results = query.all()

    # Process results
    interaction_type_data = [
        {"name": result.type, "value": result.count}
        for result in results
    ]

    return InteractionTypeData(data=interaction_type_data)


@router.get("/platforms", response_model=PlatformData)
async def get_platform_data(
    persona_id: Optional[int] = Query(None, description="Filter by persona ID"),
    time_range: AnalyticsTimeRange = Query(AnalyticsTimeRange.TWO_WEEKS, description="Time range for analytics"),
    db: Session = Depends(get_db),
) -> PlatformData:
    """
    Get performance data by platform.

    Args:
        persona_id: Optional persona ID to filter by
        time_range: Time range for analytics
        db: Database session

    Returns:
        Performance data by platform
    """
    # Calculate date range based on time_range
    end_date = datetime.now(timezone.utc)

    if time_range == AnalyticsTimeRange.ONE_WEEK:
        start_date = end_date - timedelta(days=7)
    elif time_range == AnalyticsTimeRange.TWO_WEEKS:
        start_date = end_date - timedelta(days=14)
    elif time_range == AnalyticsTimeRange.ONE_MONTH:
        start_date = end_date - timedelta(days=30)
    elif time_range == AnalyticsTimeRange.THREE_MONTHS:
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=14)  # Default to 2 weeks

    # Platform data will include:
    # 1. Number of posts (from Content)
    # 2. Number of interactions (from Interaction)

    # Query for posts by platform
    posts_query = db.query(
        Content.platform,
        func.count().label("posts")
    ).filter(
        Content.created_at >= start_date,
        Content.created_at <= end_date,
        Content.status == "published"
    )

    # Apply persona filter if provided
    if persona_id:
        posts_query = posts_query.filter(Content.persona_id == persona_id)

    # Group by platform
    posts_query = posts_query.group_by(Content.platform)

    # Execute query
    posts_results = {r.platform: r.posts for r in posts_query.all()}

    # Query for interactions by platform
    interactions_query = db.query(
        Interaction.platform,
        func.count().label("interactions")
    ).filter(
        Interaction.created_at >= start_date,
        Interaction.created_at <= end_date
    )

    # Apply persona filter if provided
    if persona_id:
        interactions_query = interactions_query.filter(Interaction.persona_id == persona_id)

    # Group by platform
    interactions_query = interactions_query.group_by(Interaction.platform)

    # Execute query
    interactions_results = {r.platform: r.interactions for r in interactions_query.all()}

    # Combine results
    platforms = set(list(posts_results.keys()) + list(interactions_results.keys()))

    platform_data = [
        {
            "name": platform,
            "posts": posts_results.get(platform, 0),
            "engagement": interactions_results.get(platform, 0),
            "followers": 0  # This would need to be fetched from platform connections
        }
        for platform in platforms
    ]

    return PlatformData(data=platform_data)


@router.get("/personas", response_model=PersonaPerformanceData)
async def get_persona_performance_data(
    time_range: AnalyticsTimeRange = Query(AnalyticsTimeRange.TWO_WEEKS, description="Time range for analytics"),
    db: Session = Depends(get_db),
) -> PersonaPerformanceData:
    """
    Get performance data by persona.

    Args:
        time_range: Time range for analytics
        db: Database session

    Returns:
        Performance data by persona
    """
    # Calculate date range based on time_range
    end_date = datetime.now(timezone.utc)

    if time_range == AnalyticsTimeRange.ONE_WEEK:
        start_date = end_date - timedelta(days=7)
    elif time_range == AnalyticsTimeRange.TWO_WEEKS:
        start_date = end_date - timedelta(days=14)
    elif time_range == AnalyticsTimeRange.ONE_MONTH:
        start_date = end_date - timedelta(days=30)
    elif time_range == AnalyticsTimeRange.THREE_MONTHS:
        start_date = end_date - timedelta(days=90)
    else:
        start_date = end_date - timedelta(days=14)  # Default to 2 weeks

    # Get all personas
    personas = db.query(Persona).filter(Persona.is_active == True).all()

    # For each persona, get:
    # 1. Number of posts
    # 2. Number of interactions

    persona_data = []

    for persona in personas:
        # Count posts
        posts_count = db.query(func.count(Content.id)).filter(
            Content.persona_id == persona.id,
            Content.created_at >= start_date,
            Content.created_at <= end_date,
            Content.status == "published"
        ).scalar() or 0

        # Count interactions
        interactions_count = db.query(func.count(Interaction.id)).filter(
            Interaction.persona_id == persona.id,
            Interaction.created_at >= start_date,
            Interaction.created_at <= end_date
        ).scalar() or 0

        # Add to results
        persona_data.append({
            "id": persona.id,
            "name": persona.name,
            "avatar": persona.avatar_url,
            "posts": posts_count,
            "engagement": interactions_count,
            "followers": 0  # This would need to be fetched from platform connections
        })

    return PersonaPerformanceData(data=persona_data)


@router.get("/dashboard", response_model=AnalyticsResponse)
async def get_dashboard_data(
    persona_id: Optional[int] = Query(None, description="Filter by persona ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    time_range: AnalyticsTimeRange = Query(AnalyticsTimeRange.TWO_WEEKS, description="Time range for analytics"),
    db: Session = Depends(get_db),
) -> AnalyticsResponse:
    """
    Get all analytics data for the dashboard.

    Args:
        persona_id: Optional persona ID to filter by
        platform: Optional platform to filter by
        time_range: Time range for analytics
        db: Database session

    Returns:
        All analytics data for the dashboard
    """
    # Get all data in parallel
    engagement_data = await get_engagement_data(persona_id, platform, time_range, db)
    content_type_data = await get_content_type_data(persona_id, platform, time_range, db)
    interaction_type_data = await get_interaction_type_data(persona_id, platform, time_range, db)
    platform_data = await get_platform_data(persona_id, time_range, db)
    persona_performance_data = await get_persona_performance_data(time_range, db)

    return AnalyticsResponse(
        engagement=engagement_data.data,
        content_types=content_type_data.data,
        interaction_types=interaction_type_data.data,
        platforms=platform_data.data,
        personas=persona_performance_data.data,
    )


# WebSocket endpoint for real-time analytics updates
@router.websocket("/ws")
async def analytics_websocket(
    websocket: WebSocket,
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time analytics updates.

    Args:
        websocket: WebSocket connection
        db: Database session
    """
    await websocket.accept()

    try:
        while True:
            # Wait for client message (could be used for filtering)
            data = await websocket.receive_json()

            # Extract filter parameters
            persona_id = data.get("persona_id")
            platform = data.get("platform")
            time_range_str = data.get("time_range", "2w")

            # Convert time_range string to enum
            time_range_map = {
                "1w": AnalyticsTimeRange.ONE_WEEK,
                "2w": AnalyticsTimeRange.TWO_WEEKS,
                "1m": AnalyticsTimeRange.ONE_MONTH,
                "3m": AnalyticsTimeRange.THREE_MONTHS,
            }
            time_range = time_range_map.get(time_range_str, AnalyticsTimeRange.TWO_WEEKS)

            # Get dashboard data
            dashboard_data = await get_dashboard_data(persona_id, platform, time_range, db)

            # Send data to client
            await websocket.send_json(dashboard_data.model_dump())

            # Wait for a short period before checking for updates again
            await asyncio.sleep(5)

    except WebSocketDisconnect:
        # Handle client disconnect
        pass
