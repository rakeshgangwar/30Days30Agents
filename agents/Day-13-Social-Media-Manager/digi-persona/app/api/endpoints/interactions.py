"""
Interactions API Endpoints Module

This module provides API endpoints for managing interactions.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.personas.context import persona_context
from app.core.platforms.manager import PlatformManager, get_platform_manager
from app.db.models.interaction import Interaction
from app.db.models.persona import Persona
from app.db.models.platform import PlatformConnection
from app.api.endpoints.metrics import track_interaction
from app.schemas.interaction import (
    InteractionCreate,
    InteractionResponse,
    InteractionList,
    InteractionResponseCreate,
    InteractionResponseResponse,
    InteractionFilter
)

router = APIRouter()

@router.get("/", response_model=InteractionList)
def get_interactions(
    persona_id: Optional[int] = Query(None, description="Filter by persona ID"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    status: Optional[str] = Query(None, description="Filter by status (pending, responded)"),
    type: Optional[str] = Query(None, description="Filter by type (mention, reply, comment, etc.)"),
    skip: int = Query(0, description="Number of interactions to skip"),
    limit: int = Query(100, description="Maximum number of interactions to return"),
    db: Session = Depends(get_db),
):
    """
    Get a list of interactions.

    Args:
        persona_id: Filter by persona ID.
        platform: Filter by platform.
        status: Filter by status.
        type: Filter by interaction type.
        skip: Number of interactions to skip.
        limit: Maximum number of interactions to return.
        db: The database session.

    Returns:
        List of interactions.
    """
    # Get persona ID from context if not provided
    if persona_id is None:
        persona_id = persona_context.get_persona()

    # Build the query
    query = db.query(Interaction)

    if persona_id:
        query = query.filter(Interaction.persona_id == persona_id)

    if platform:
        query = query.filter(Interaction.platform.ilike(f"%{platform}%"))

    if status:
        query = query.filter(Interaction.status == status)

    if type:
        query = query.filter(Interaction.type == type)

    # Apply pagination
    total = query.count()
    interactions = query.order_by(Interaction.created_at.desc()).offset(skip).limit(limit).all()

    # Format the response
    items = []
    for interaction in interactions:
        # Format the response
        items.append({
            "id": interaction.id,
            "persona_id": interaction.persona_id,
            "platform": interaction.platform,
            "external_id": interaction.external_id,
            "type": interaction.type,
            "content": interaction.content_text,
            "author": interaction.author_data,
            "status": interaction.status,
            "response": interaction.response,
            "created_at": interaction.created_at,
            "updated_at": interaction.updated_at,
            "responded_at": interaction.responded_at,
            "platform_data": interaction.platform_data
        })

    return {"items": items, "total": total, "skip": skip, "limit": limit}

@router.post("/sync", response_model=Dict[str, Any])
def sync_interactions(
    platform_filter: Optional[str] = Query(None, description="Filter by platform"),
    persona_id: Optional[int] = Query(None, description="Filter by persona ID"),
    count: int = Query(50, description="Maximum number of interactions to retrieve per platform"),
    db: Session = Depends(get_db),
    platform_manager: PlatformManager = Depends(lambda: get_platform_manager(next(get_db()))),
):
    """
    Synchronize interactions from connected platforms.

    Args:
        platform_filter: Filter by platform.
        persona_id: Filter by persona ID.
        count: Maximum number of interactions to retrieve per platform.
        db: The database session.
        platform_manager: The platform manager.

    Returns:
        Dictionary containing synchronization results.
    """
    # Get persona ID from context if not provided
    if persona_id is None:
        persona_id = persona_context.get_persona()

    # Get platform connections for the persona
    query = db.query(PlatformConnection).filter(PlatformConnection.is_active == True)

    if persona_id:
        query = query.filter(PlatformConnection.persona_id == persona_id)

    if platform_filter:
        query = query.filter(PlatformConnection.platform_name.ilike(f"%{platform_filter}%"))

    platform_connections = query.all()

    # Initialize results
    results = {
        "platforms": {},
        "total_new_interactions": 0
    }

    # For each platform connection, get interactions
    for connection in platform_connections:
        platform_name = connection.platform_name
        persona_id = connection.persona_id

        try:
            # Get the most recent interaction for this persona and platform
            most_recent = db.query(Interaction).filter(
                Interaction.persona_id == persona_id,
                Interaction.platform == platform_name
            ).order_by(Interaction.created_at.desc()).first()

            since_id = most_recent.external_id if most_recent else None

            # Get interactions from platform
            interactions = platform_manager.get_interactions(
                persona_id=persona_id,
                platform_name=platform_name,
                since_id=since_id,
                count=count
            )

            # Process each interaction
            new_count = 0
            for interaction_data in interactions:
                # Check if interaction already exists
                external_id = interaction_data.get('id')
                existing = db.query(Interaction).filter(
                    Interaction.persona_id == persona_id,
                    Interaction.platform == platform_name,
                    Interaction.external_id == external_id
                ).first()

                if existing:
                    continue

                # Extract interaction data
                interaction_type = interaction_data.get('type', 'unknown')
                content = interaction_data.get('text', '')
                author = interaction_data.get('user', {})
                created_at_str = interaction_data.get('created_at')

                # Create new interaction
                new_interaction = Interaction(
                    persona_id=persona_id,
                    platform=platform_name,
                    external_id=external_id,
                    type=interaction_type,
                    content_text=content,
                    author_data=author,
                    status="pending",
                    response=None,
                    platform_data=interaction_data
                )

                db.add(new_interaction)
                new_count += 1

                # Track interaction in metrics
                track_interaction(
                    persona_id=persona_id,
                    platform=platform_name,
                    interaction_type=interaction_type
                )

            # Commit changes
            db.commit()

            # Update results
            results["platforms"][platform_name] = {
                "persona_id": persona_id,
                "new_interactions": new_count
            }
            results["total_new_interactions"] += new_count

        except Exception as e:
            # Log error but continue with other platforms
            results["platforms"][platform_name] = {
                "persona_id": persona_id,
                "error": str(e)
            }

    return results

@router.get("/{interaction_id}", response_model=InteractionResponse)
def get_interaction(
    interaction_id: int = Path(..., description="The ID of the interaction"),
    db: Session = Depends(get_db),
):
    """
    Get an interaction by ID.

    Args:
        interaction_id: The ID of the interaction.
        db: The database session.

    Returns:
        The interaction.

    Raises:
        HTTPException: If the interaction is not found.
    """
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()

    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    # Verify access permission (only access interactions for personas you can access)
    persona_id = persona_context.get_persona()
    if persona_id and interaction.persona_id != persona_id:
        # Verify if this user has access to this persona
        # This would require additional logic based on your application's authorization model
        pass

    # Format the response
    return {
        "id": interaction.id,
        "persona_id": interaction.persona_id,
        "platform": interaction.platform,
        "external_id": interaction.external_id,
        "type": interaction.type,
        "content": interaction.content_text,
        "author": interaction.author_data,
        "status": interaction.status,
        "response": interaction.response,
        "created_at": interaction.created_at,
        "updated_at": interaction.updated_at,
        "responded_at": interaction.responded_at,
        "platform_data": interaction.platform_data
    }

@router.post("/{interaction_id}/respond", response_model=InteractionResponseResponse)
def respond_to_interaction(
    response_data: InteractionResponseCreate,
    interaction_id: int = Path(..., description="The ID of the interaction"),
    db: Session = Depends(get_db),
    platform_manager: PlatformManager = Depends(lambda: get_platform_manager(next(get_db()))),
):
    """
    Respond to an interaction.

    Args:
        response_data: The response data.
        interaction_id: The ID of the interaction.
        db: The database session.
        platform_manager: The platform manager.

    Returns:
        The response information.

    Raises:
        HTTPException: If the interaction is not found or responding fails.
    """
    # Get the interaction
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()

    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    try:
        # Get the persona and platform
        persona_id = interaction.persona_id
        platform_name = interaction.platform

        # Respond to the interaction on the platform
        response_info = platform_manager.respond_to_interaction(
            persona_id=persona_id,
            platform_name=platform_name,
            interaction_id=interaction.external_id,
            content=response_data.content,
            **interaction.platform_data  # Pass platform-specific data
        )

        # Update the interaction
        interaction.status = "responded"
        interaction.response = response_data.content
        interaction.responded_at = response_info.get('created_at')
        db.commit()

        return {
            "interaction_id": interaction.id,
            "platform": interaction.platform,
            "content": response_data.content,
            "external_id": response_info.get('id'),
            "created_at": response_info.get('created_at'),
            "platform_data": response_info
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/generate-response", response_model=Dict[str, str])
def generate_response(
    interaction_id: int = Query(..., description="The ID of the interaction"),
    db: Session = Depends(get_db),
):
    """
    Generate a response for an interaction using AI.

    Args:
        interaction_id: The ID of the interaction.
        db: The database session.

    Returns:
        The generated response.

    Raises:
        HTTPException: If the interaction is not found or generation fails.
    """
    # Get the interaction
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()

    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    try:
        # Get the persona
        persona = db.query(Persona).filter(Persona.id == interaction.persona_id).first()

        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")

        # In a real implementation, this would use the AI generator
        # For now, we'll return a mock response

        # Different responses based on interaction type
        responses = {
            "mention": f"Thank you for mentioning me! As someone focused on {persona.purpose}, I'd be happy to engage with you on this topic.",
            "reply": f"Thank you for your reply! I appreciate your engagement. To clarify more about {persona.expertise[0] if persona.expertise else 'this topic'}, let me elaborate...",
            "comment": f"Thank you for your comment! I value your perspective. Given my background in {persona.background}, I believe...",
            "direct_message": f"Thanks for reaching out directly! I'm happy to discuss {persona.interests[0] if persona.interests else 'this topic'} further."
        }

        # Get response based on type, or use default
        generated_response = responses.get(interaction.type, f"Thank you for your interaction! As {persona.name}, I'm interested in your thoughts.")

        return {"generated_response": generated_response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate response: {str(e)}")

@router.post("/filter", response_model=InteractionList)
def filter_interactions(
    filter_params: InteractionFilter,
    skip: int = Query(0, description="Number of interactions to skip"),
    limit: int = Query(100, description="Maximum number of interactions to return"),
    db: Session = Depends(get_db),
):
    """
    Filter interactions based on various criteria.

    Args:
        filter_params: The filter parameters.
        skip: Number of interactions to skip.
        limit: Maximum number of interactions to return.
        db: The database session.

    Returns:
        List of filtered interactions.
    """
    # Get persona ID from context if not provided
    persona_id = filter_params.persona_id or persona_context.get_persona()

    # Build the query
    query = db.query(Interaction)

    if persona_id:
        query = query.filter(Interaction.persona_id == persona_id)

    if filter_params.platform:
        query = query.filter(Interaction.platform.ilike(f"%{filter_params.platform}%"))

    if filter_params.status:
        query = query.filter(Interaction.status == filter_params.status)

    if filter_params.type:
        query = query.filter(Interaction.type == filter_params.type)

    if filter_params.author_name:
        query = query.filter(Interaction.author_data['name'].astext.ilike(f"%{filter_params.author_name}%"))

    if filter_params.content_contains:
        query = query.filter(Interaction.content_text.ilike(f"%{filter_params.content_contains}%"))

    # Apply date filters
    if filter_params.created_after:
        query = query.filter(Interaction.created_at >= filter_params.created_after)

    if filter_params.created_before:
        query = query.filter(Interaction.created_at <= filter_params.created_before)

    # Apply sorting
    if filter_params.sort_by == "created_at":
        if filter_params.sort_order == "desc":
            query = query.order_by(Interaction.created_at.desc())
        else:
            query = query.order_by(Interaction.created_at.asc())
    elif filter_params.sort_by == "updated_at":
        if filter_params.sort_order == "desc":
            query = query.order_by(Interaction.updated_at.desc())
        else:
            query = query.order_by(Interaction.updated_at.asc())

    # Apply pagination
    total = query.count()
    interactions = query.offset(skip).limit(limit).all()

    # Format the response
    items = []
    for interaction in interactions:
        items.append({
            "id": interaction.id,
            "persona_id": interaction.persona_id,
            "platform": interaction.platform,
            "external_id": interaction.external_id,
            "type": interaction.type,
            "content": interaction.content_text,
            "author": interaction.author_data,
            "status": interaction.status,
            "response": interaction.response,
            "created_at": interaction.created_at,
            "updated_at": interaction.updated_at,
            "responded_at": interaction.responded_at,
            "platform_data": interaction.platform_data
        })

    return {"items": items, "total": total, "skip": skip, "limit": limit}
