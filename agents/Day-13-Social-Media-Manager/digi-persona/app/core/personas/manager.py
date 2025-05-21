"""
Persona Manager Module

This module provides functionality for managing personas.
"""

from typing import Dict, List, Optional, Any

from sqlalchemy.orm import Session

from app.db.models.persona import Persona
from app.core.personas.context import persona_context


class PersonaManager:
    """
    Manager for persona operations.
    
    This class provides methods for creating, retrieving, updating, and deleting
    personas, as well as managing persona-specific data.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the persona manager.
        
        Args:
            db: The database session.
        """
        self.db = db
    
    def create_persona(self, persona_data: Dict[str, Any]) -> Persona:
        """
        Create a new persona.
        
        Args:
            persona_data: Dictionary containing persona attributes.
            
        Returns:
            The created persona.
        """
        persona = Persona(**persona_data)
        self.db.add(persona)
        self.db.commit()
        self.db.refresh(persona)
        return persona
    
    def get_persona(self, persona_id: int) -> Optional[Persona]:
        """
        Get a persona by ID.
        
        Args:
            persona_id: The ID of the persona to get.
            
        Returns:
            The persona, or None if not found.
        """
        return self.db.query(Persona).filter(Persona.id == persona_id).first()
    
    def get_personas(self, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[Persona]:
        """
        Get a list of personas.
        
        Args:
            skip: Number of personas to skip.
            limit: Maximum number of personas to return.
            active_only: Whether to return only active personas.
            
        Returns:
            List of personas.
        """
        query = self.db.query(Persona)
        if active_only:
            query = query.filter(Persona.is_active == True)  # noqa: E712
        return query.offset(skip).limit(limit).all()
    
    def update_persona(self, persona_id: int, persona_data: Dict[str, Any]) -> Optional[Persona]:
        """
        Update a persona.
        
        Args:
            persona_id: The ID of the persona to update.
            persona_data: Dictionary containing updated persona attributes.
            
        Returns:
            The updated persona, or None if not found.
        """
        persona = self.get_persona(persona_id)
        if not persona:
            return None
        
        for key, value in persona_data.items():
            if hasattr(persona, key):
                setattr(persona, key, value)
        
        self.db.commit()
        self.db.refresh(persona)
        return persona
    
    def delete_persona(self, persona_id: int) -> bool:
        """
        Delete a persona.
        
        Args:
            persona_id: The ID of the persona to delete.
            
        Returns:
            True if the persona was deleted, False if not found.
        """
        persona = self.get_persona(persona_id)
        if not persona:
            return False
        
        self.db.delete(persona)
        self.db.commit()
        return True
    
    def deactivate_persona(self, persona_id: int) -> Optional[Persona]:
        """
        Deactivate a persona.
        
        Args:
            persona_id: The ID of the persona to deactivate.
            
        Returns:
            The deactivated persona, or None if not found.
        """
        return self.update_persona(persona_id, {"is_active": False})
    
    def activate_persona(self, persona_id: int) -> Optional[Persona]:
        """
        Activate a persona.
        
        Args:
            persona_id: The ID of the persona to activate.
            
        Returns:
            The activated persona, or None if not found.
        """
        return self.update_persona(persona_id, {"is_active": True})
    
    def get_current_persona(self) -> Optional[Persona]:
        """
        Get the current persona from context.
        
        Returns:
            The current persona, or None if no persona is set in context.
        """
        persona_id = persona_context.get_persona()
        if persona_id is None:
            return None
        return self.get_persona(persona_id)
    
    def require_current_persona(self) -> Persona:
        """
        Get the current persona from context, raising an error if none is set.
        
        Returns:
            The current persona.
            
        Raises:
            ValueError: If no persona is set in context.
        """
        persona_id = persona_context.require_persona()
        persona = self.get_persona(persona_id)
        if not persona:
            raise ValueError(f"Persona with ID {persona_id} not found")
        return persona


def get_persona_manager(db: Session) -> PersonaManager:
    """
    Get a persona manager instance.
    
    Args:
        db: The database session.
        
    Returns:
        A persona manager instance.
    """
    return PersonaManager(db)
