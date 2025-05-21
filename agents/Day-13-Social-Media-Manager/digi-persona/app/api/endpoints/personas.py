"""
Personas API Endpoints Module

This module provides API endpoints for managing personas.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.core.personas.manager import PersonaManager, get_persona_manager
from app.db.session import get_db
from app.api.endpoints.metrics import update_persona_count
from app.schemas.persona import PersonaCreate, PersonaUpdate, PersonaResponse, PersonaList

router = APIRouter()


@router.post("/", response_model=PersonaResponse, status_code=201)
def create_persona(
    persona: PersonaCreate,
    db: Session = Depends(get_db),
    persona_manager: PersonaManager = Depends(lambda: get_persona_manager(next(get_db()))),
) -> PersonaResponse:
    """
    Create a new persona.

    Args:
        persona: The persona data.
        db: The database session.
        persona_manager: The persona manager.

    Returns:
        The created persona.
    """
    created_persona = persona_manager.create_persona(persona.model_dump())

    # Update persona count in metrics
    persona_count = db.query(persona_manager.model).count()
    update_persona_count(persona_count)

    return created_persona


@router.get("/{persona_id}", response_model=PersonaResponse)
def get_persona(
    persona_id: int = Path(..., description="The ID of the persona to get"),
    db: Session = Depends(get_db),
    persona_manager: PersonaManager = Depends(lambda: get_persona_manager(next(get_db()))),
) -> PersonaResponse:
    """
    Get a persona by ID.

    Args:
        persona_id: The ID of the persona to get.
        db: The database session.
        persona_manager: The persona manager.

    Returns:
        The persona.

    Raises:
        HTTPException: If the persona is not found.
    """
    persona = persona_manager.get_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona


@router.get("/", response_model=PersonaList)
def get_personas(
    skip: int = Query(0, description="Number of personas to skip"),
    limit: int = Query(100, description="Maximum number of personas to return"),
    active_only: bool = Query(True, description="Whether to return only active personas"),
    db: Session = Depends(get_db),
    persona_manager: PersonaManager = Depends(lambda: get_persona_manager(next(get_db()))),
) -> PersonaList:
    """
    Get a list of personas.

    Args:
        skip: Number of personas to skip.
        limit: Maximum number of personas to return.
        active_only: Whether to return only active personas.
        db: The database session.
        persona_manager: The persona manager.

    Returns:
        List of personas.
    """
    personas = persona_manager.get_personas(skip=skip, limit=limit, active_only=active_only)
    total = len(personas)  # In a real implementation, this would be a separate count query
    return PersonaList(items=personas, total=total, skip=skip, limit=limit)


@router.put("/{persona_id}", response_model=PersonaResponse)
def update_persona(
    persona: PersonaUpdate,
    persona_id: int = Path(..., description="The ID of the persona to update"),
    db: Session = Depends(get_db),
    persona_manager: PersonaManager = Depends(lambda: get_persona_manager(next(get_db()))),
) -> PersonaResponse:
    """
    Update a persona.

    Args:
        persona: The updated persona data.
        persona_id: The ID of the persona to update.
        db: The database session.
        persona_manager: The persona manager.

    Returns:
        The updated persona.

    Raises:
        HTTPException: If the persona is not found.
    """
    updated_persona = persona_manager.update_persona(persona_id, persona.model_dump(exclude_unset=True))
    if not updated_persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return updated_persona


@router.delete("/{persona_id}", status_code=204)
def delete_persona(
    persona_id: int = Path(..., description="The ID of the persona to delete"),
    db: Session = Depends(get_db),
    persona_manager: PersonaManager = Depends(lambda: get_persona_manager(next(get_db()))),
) -> None:
    """
    Delete a persona.

    Args:
        persona_id: The ID of the persona to delete.
        db: The database session.
        persona_manager: The persona manager.

    Raises:
        HTTPException: If the persona is not found.
    """
    success = persona_manager.delete_persona(persona_id)
    if not success:
        raise HTTPException(status_code=404, detail="Persona not found")


@router.patch("/{persona_id}/activate", response_model=PersonaResponse)
def activate_persona(
    persona_id: int = Path(..., description="The ID of the persona to activate"),
    db: Session = Depends(get_db),
    persona_manager: PersonaManager = Depends(lambda: get_persona_manager(next(get_db()))),
) -> PersonaResponse:
    """
    Activate a persona.

    Args:
        persona_id: The ID of the persona to activate.
        db: The database session.
        persona_manager: The persona manager.

    Returns:
        The activated persona.

    Raises:
        HTTPException: If the persona is not found.
    """
    persona = persona_manager.activate_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona


@router.patch("/{persona_id}/deactivate", response_model=PersonaResponse)
def deactivate_persona(
    persona_id: int = Path(..., description="The ID of the persona to deactivate"),
    db: Session = Depends(get_db),
    persona_manager: PersonaManager = Depends(lambda: get_persona_manager(next(get_db()))),
) -> PersonaResponse:
    """
    Deactivate a persona.

    Args:
        persona_id: The ID of the persona to deactivate.
        db: The database session.
        persona_manager: The persona manager.

    Returns:
        The deactivated persona.

    Raises:
        HTTPException: If the persona is not found.
    """
    persona = persona_manager.deactivate_persona(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona
