"""
Persona Prompts

This module provides prompt templates for persona agents.
"""
from typing import Dict, Any, Optional
from langchain.prompts import PromptTemplate


DEFAULT_PERSONA_TEMPLATE = """
You are acting as {persona_name}, with the following characteristics:

Description: {persona_description}
Tone: {persona_tone}
Style: {persona_style}
Interests: {persona_interests}

When responding, maintain the persona's tone, style, and interests. Be authentic and consistent with the persona's characteristics.

{additional_context}
"""

CONTENT_GENERATION_TEMPLATE = """
You are acting as {persona_name}, with the following characteristics:

Description: {persona_description}
Tone: {persona_tone}
Style: {persona_style}
Interests: {persona_interests}

Your task is to generate {content_type} content for {platform} about the topic: {topic}.

Make sure the content is:
1. Authentic to the persona's voice and style
2. Appropriate for the platform ({platform})
3. Engaging and relevant to the topic
4. Within the character limits for the platform

Additional context: {additional_context}

Generate the content now:
"""


def get_persona_prompt(persona_data: Dict[str, Any], additional_context: Optional[str] = None) -> PromptTemplate:
    """
    Get a prompt template for a persona.

    Args:
        persona_data: Dictionary containing persona information
        additional_context: Optional additional context to include in the prompt

    Returns:
        A PromptTemplate for the persona
    """
    # Create the prompt template
    prompt_template = PromptTemplate(
        input_variables=["persona_name", "persona_description", "persona_tone",
                        "persona_style", "persona_interests", "additional_context"],
        template=DEFAULT_PERSONA_TEMPLATE
    )

    return prompt_template


def get_content_generation_prompt(persona_data: Dict[str, Any], content_type: str,
                                platform: str, topic: str,
                                additional_context: Optional[str] = None) -> PromptTemplate:
    """
    Get a prompt template for content generation.

    Args:
        persona_data: Dictionary containing persona information
        content_type: Type of content to generate (e.g., tweet, post, article)
        platform: Platform for the content (e.g., Twitter, LinkedIn)
        topic: Topic for the content
        additional_context: Optional additional context to include in the prompt

    Returns:
        A PromptTemplate for content generation
    """
    # Create the prompt template
    prompt_template = PromptTemplate(
        input_variables=["persona_name", "persona_description", "persona_tone",
                        "persona_style", "persona_interests", "content_type",
                        "platform", "topic", "additional_context"],
        template=CONTENT_GENERATION_TEMPLATE
    )

    return prompt_template
