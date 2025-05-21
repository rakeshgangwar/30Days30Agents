"""
Persona Conversation Memory

This module provides a conversation memory implementation for persona agents.
"""
from typing import Dict, List, Optional, Any
from langchain.memory import ConversationBufferMemory


class PersonaConversationMemory(ConversationBufferMemory):
    """
    Memory implementation for persona agents that extends ConversationBufferMemory.
    
    This class adds persona-specific context to the conversation memory.
    """
    
    def __init__(
        self,
        persona_id: int,
        persona_name: str,
        persona_context: Optional[str] = None,
        memory_key: str = "history",
        input_key: Optional[str] = None,
        output_key: Optional[str] = None,
        return_messages: bool = False,
        human_prefix: str = "Human",
        ai_prefix: str = "AI",
        **kwargs: Any,
    ):
        """Initialize with persona information."""
        super().__init__(
            memory_key=memory_key,
            input_key=input_key,
            output_key=output_key,
            return_messages=return_messages,
            human_prefix=human_prefix,
            ai_prefix=ai_prefix,
            **kwargs,
        )
        self.persona_id = persona_id
        self.persona_name = persona_name
        self.persona_context = persona_context
        
        # Override AI prefix with persona name if provided
        if persona_name:
            self.ai_prefix = persona_name
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load memory variables, including persona context if available."""
        memory_dict = super().load_memory_variables(inputs)
        
        # If persona context is available, add it to the memory variables
        if self.persona_context and self.memory_key in memory_dict:
            # Add persona context as a system message or in the format expected by the agent
            if self.return_messages:
                # For message-based memory
                context_message = f"Persona Context: {self.persona_context}"
                memory_dict["persona_context"] = context_message
            else:
                # For string-based memory
                memory_dict["persona_context"] = self.persona_context
        
        return memory_dict
    
    def clear(self) -> None:
        """Clear memory contents, but retain persona information."""
        super().clear()
        # Persona information is retained even after clearing the conversation history
