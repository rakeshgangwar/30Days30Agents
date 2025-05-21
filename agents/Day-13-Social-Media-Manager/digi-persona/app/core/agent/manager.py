"""
Agent Manager Module

This module provides the core functionality for managing LLM agents with persona context.
It handles agent initialization, state management, and lifecycle operations.
"""

from typing import Dict, Optional, Any

from langchain.agents import AgentExecutor
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.schema import BaseMemory
from langchain_openai import ChatOpenAI

from app.core.agent.memory import PersonaConversationMemory
from app.core.agent.tools import get_persona_tools
from app.core.agent.prompts import get_persona_prompt
from app.core.personas.context import persona_context
from app.db.models.persona import Persona


class PersonaAgentManager:
    """
    Manages the lifecycle of persona-specific LLM agents.
    
    This class handles the creation, configuration, and execution of agents
    based on persona context. It ensures that each agent has the appropriate
    tools, memory, and prompt templates for the specific persona.
    """
    
    def __init__(self):
        """Initialize the agent manager."""
        self._agents: Dict[int, AgentExecutor] = {}
    
    def get_agent(self, persona_id: Optional[int] = None) -> AgentExecutor:
        """
        Get or create an agent for the specified persona.
        
        Args:
            persona_id: The ID of the persona to get an agent for.
                If None, uses the current persona from context.
                
        Returns:
            An agent executor configured for the persona.
            
        Raises:
            ValueError: If no persona ID is provided and none is in context.
        """
        # Get persona ID from context if not provided
        if persona_id is None:
            persona_id = persona_context.require_persona()
        
        # Return existing agent if available
        if persona_id in self._agents:
            return self._agents[persona_id]
        
        # Create new agent
        agent = self._create_agent(persona_id)
        self._agents[persona_id] = agent
        return agent
    
    def _create_agent(self, persona_id: int) -> AgentExecutor:
        """
        Create a new agent for the specified persona.
        
        Args:
            persona_id: The ID of the persona to create an agent for.
            
        Returns:
            A new agent executor configured for the persona.
        """
        # Get persona details from database
        persona = self._get_persona(persona_id)
        
        # Create memory
        memory = PersonaConversationMemory(persona_id=persona_id)
        
        # Get tools for persona
        tools = get_persona_tools(persona)
        
        # Create LLM
        llm = ChatOpenAI(temperature=0.7, model="gpt-4o")
        
        # Create prompt
        prompt = get_persona_prompt(persona)
        
        # Create agent
        agent = OpenAIFunctionsAgent(
            llm=llm,
            tools=tools,
            prompt=prompt,
        )
        
        # Create agent executor
        return AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
        )
    
    def _get_persona(self, persona_id: int) -> Persona:
        """
        Get persona details from the database.
        
        Args:
            persona_id: The ID of the persona to get.
            
        Returns:
            The persona object.
            
        Raises:
            ValueError: If the persona does not exist.
        """
        # This would be replaced with actual database query
        # For now, we'll just return a mock persona
        from app.db.session import get_db
        
        db = next(get_db())
        persona = db.query(Persona).filter(Persona.id == persona_id).first()
        
        if not persona:
            raise ValueError(f"Persona with ID {persona_id} not found")
        
        return persona
    
    def reset_agent(self, persona_id: Optional[int] = None) -> None:
        """
        Reset the agent for the specified persona.
        
        Args:
            persona_id: The ID of the persona to reset the agent for.
                If None, uses the current persona from context.
                
        Raises:
            ValueError: If no persona ID is provided and none is in context.
        """
        # Get persona ID from context if not provided
        if persona_id is None:
            persona_id = persona_context.require_persona()
        
        # Remove agent from cache
        if persona_id in self._agents:
            del self._agents[persona_id]
    
    async def run(self, input_text: str, persona_id: Optional[int] = None, **kwargs: Any) -> str:
        """
        Run the agent with the specified input.
        
        Args:
            input_text: The input text to process.
            persona_id: The ID of the persona to use.
                If None, uses the current persona from context.
            **kwargs: Additional arguments to pass to the agent.
                
        Returns:
            The agent's response.
            
        Raises:
            ValueError: If no persona ID is provided and none is in context.
        """
        agent = self.get_agent(persona_id)
        return await agent.ainvoke({"input": input_text, **kwargs})


# Global agent manager instance
agent_manager = PersonaAgentManager()
