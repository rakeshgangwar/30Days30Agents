from contextvars import ContextVar
from typing import Optional

# Create a context variable to store the current persona ID
persona_id_var: ContextVar[Optional[int]] = ContextVar("persona_id", default=None)

class PersonaContext:
    """Manages the current active persona context."""
    
    def set_persona(self, persona_id: int) -> None:
        """Set the current persona ID in the context."""
        persona_id_var.set(persona_id)
    
    def get_persona(self) -> Optional[int]:
        """Get the current persona ID from the context."""
        return persona_id_var.get()
    
    def require_persona(self) -> int:
        """
        Ensures a persona is set in the context.
        
        Returns:
            int: The current persona ID.
            
        Raises:
            ValueError: If no persona is set in the context.
        """
        persona_id = self.get_persona()
        if persona_id is None:
            raise ValueError("No active persona in context")
        return persona_id

# Global persona context
persona_context = PersonaContext()
