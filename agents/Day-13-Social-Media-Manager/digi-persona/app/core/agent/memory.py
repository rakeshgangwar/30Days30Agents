"""
Agent Memory Module

This module provides memory implementations for LLM agents with persona context.
It handles conversation history storage and retrieval.
"""

from typing import Any, Dict, List, Optional

from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseChatMessageHistory

from app.core.personas.context import persona_context


class PersonaConversationMemory(ConversationBufferMemory):
    """
    Conversation memory for persona-specific agents.
    
    This class extends the ConversationBufferMemory to include persona context
    and provide persona-specific conversation history.
    """
    
    def __init__(
        self,
        persona_id: Optional[int] = None,
        memory_key: str = "chat_history",
        return_messages: bool = True,
        output_key: Optional[str] = None,
        input_key: Optional[str] = None,
        human_prefix: str = "Human",
        ai_prefix: str = "AI",
    ):
        """
        Initialize the persona conversation memory.
        
        Args:
            persona_id: The ID of the persona to store memory for.
                If None, uses the current persona from context.
            memory_key: The key to use for the memory in the agent's state.
            return_messages: Whether to return the history as a list of messages.
            output_key: The key to use for the output in the agent's state.
            input_key: The key to use for the input in the agent's state.
            human_prefix: The prefix to use for human messages.
            ai_prefix: The prefix to use for AI messages.
        """
        # Get persona ID from context if not provided
        if persona_id is None:
            persona_id = persona_context.require_persona()
        
        self.persona_id = persona_id
        
        # Initialize base memory
        super().__init__(
            memory_key=memory_key,
            return_messages=return_messages,
            output_key=output_key,
            input_key=input_key,
            human_prefix=human_prefix,
            ai_prefix=ai_prefix,
        )
        
        # Set chat memory
        self.chat_memory = PersonaChatMessageHistory(persona_id=self.persona_id)


class PersonaChatMessageHistory(BaseChatMessageHistory):
    """
    Chat message history for persona-specific agents.
    
    This class implements the BaseChatMessageHistory interface to provide
    persona-specific conversation history storage and retrieval.
    """
    
    def __init__(self, persona_id: int):
        """
        Initialize the persona chat message history.
        
        Args:
            persona_id: The ID of the persona to store history for.
        """
        self.persona_id = persona_id
        self._messages: List[Dict[str, Any]] = []
    
    def add_message(self, message: Dict[str, Any]) -> None:
        """
        Add a message to the history.
        
        Args:
            message: The message to add.
        """
        # In a real implementation, this would store the message in a database
        # For now, we'll just store it in memory
        self._messages.append(message)
    
    def clear(self) -> None:
        """Clear the message history."""
        self._messages = []
    
    @property
    def messages(self) -> List[Dict[str, Any]]:
        """
        Get the message history.
        
        Returns:
            The list of messages in the history.
        """
        # In a real implementation, this would retrieve messages from a database
        # For now, we'll just return the in-memory messages
        return self._messages
