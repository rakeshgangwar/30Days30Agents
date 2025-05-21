"""
Agent Prompts Module

This module provides prompt templates for LLM agents with persona context.
It handles the creation and rendering of persona-specific prompts.
"""

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage

from app.db.models.persona import Persona


def get_persona_prompt(persona: Persona) -> ChatPromptTemplate:
    """
    Get a prompt template for the specified persona.
    
    Args:
        persona: The persona to create a prompt for.
        
    Returns:
        A prompt template configured for the persona.
    """
    # Create system message with persona details
    system_message = _create_system_message(persona)
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            system_message,
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content="{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    
    return prompt


def _create_system_message(persona: Persona) -> SystemMessage:
    """
    Create a system message with persona details.
    
    Args:
        persona: The persona to create a system message for.
        
    Returns:
        A system message with persona details.
    """
    # Format interests and values as comma-separated lists
    interests = ", ".join(persona.interests) if persona.interests else "None"
    values = ", ".join(persona.values) if persona.values else "None"
    expertise = ", ".join(persona.expertise) if persona.expertise else "None"
    
    # Create system message content
    content = f"""
    You are {persona.name}, an AI assistant with the following characteristics:
    
    Background: {persona.background}
    Interests: {interests}
    Values: {values}
    Expertise: {expertise}
    Tone: {persona.tone}
    Purpose: {persona.purpose}
    
    When responding to users, maintain the persona described above. Use the appropriate tone,
    reference your background and expertise when relevant, and stay true to your values.
    
    You have access to various tools to help you accomplish tasks. Use these tools when appropriate
    to provide the best assistance possible.
    """
    
    return SystemMessage(content=content.strip())
