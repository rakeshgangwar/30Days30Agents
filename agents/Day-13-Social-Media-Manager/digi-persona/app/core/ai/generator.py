"""
AI Generator Module

This module provides content generation functionality using AI.
"""

import asyncio
from typing import Dict, List, Optional, Any

from app.core.ai.client import OpenAIClient, get_openai_client
from app.core.agent.manager import agent_manager
from app.db.models.persona import Persona


class ContentGenerator:
    """
    Content generator using AI.

    This class provides methods for generating content based on persona attributes
    and content requirements.
    """

    def __init__(self, openai_client: Optional[OpenAIClient] = None):
        """
        Initialize the content generator.

        Args:
            openai_client: The OpenAI client to use. If None, gets the global instance.
        """
        self.openai_client = openai_client or get_openai_client()
        self.agent_manager = agent_manager

    def generate_content(
        self,
        persona: Persona,
        content_type: str,
        topic: str,
        platform: str,
        additional_context: Optional[str] = None,
        max_length: Optional[int] = None,
    ) -> str:
        """
        Generate content for a persona.

        Args:
            persona: The persona to generate content for.
            content_type: The type of content to generate (e.g., tweet, post, article).
            topic: The topic to generate content about.
            platform: The platform to generate content for (e.g., twitter, linkedin, bluesky).
            additional_context: Additional context for generation.
            max_length: Maximum length of the generated content.

        Returns:
            The generated content.
        """
        # Try to use the agent framework first
        try:
            # Create the agent input prompt
            agent_input = self._create_agent_input(
                content_type=content_type,
                topic=topic,
                platform=platform,
                additional_context=additional_context,
                max_length=max_length,
            )

            # Run the agent asynchronously
            content = asyncio.run(self.agent_manager.run(agent_input, persona.id))
            return content
        except Exception as e:
            # Fall back to direct prompt if agent fails
            print(f"Agent-based generation failed: {str(e)}. Falling back to direct prompt.")
            prompt = self._create_prompt(
                persona=persona,
                content_type=content_type,
                topic=topic,
                platform=platform,
                additional_context=additional_context,
                max_length=max_length,
            )

            return self.openai_client.generate_text(prompt=prompt)

    def generate_interaction_response(
        self,
        persona: Persona,
        interaction_text: str,
        interaction_type: str,
        platform: str,
        original_content: Optional[str] = None,
    ) -> str:
        """
        Generate a response to an interaction.

        Args:
            persona: The persona to generate a response for.
            interaction_text: The text of the interaction to respond to.
            interaction_type: The type of interaction (e.g., mention, reply).
            platform: The platform the interaction is on.
            original_content: The original content that was interacted with.

        Returns:
            The generated response.
        """
        # Try to use the agent framework first
        try:
            # Create the agent input prompt
            agent_input = self._create_agent_interaction_input(
                interaction_text=interaction_text,
                interaction_type=interaction_type,
                platform=platform,
                original_content=original_content,
            )

            # Run the agent asynchronously
            response = asyncio.run(self.agent_manager.run(agent_input, persona.id))
            return response
        except Exception as e:
            # Fall back to direct prompt if agent fails
            print(f"Agent-based interaction response failed: {str(e)}. Falling back to direct prompt.")
            prompt = self._create_interaction_prompt(
                persona=persona,
                interaction_text=interaction_text,
                interaction_type=interaction_type,
                platform=platform,
                original_content=original_content,
            )

            return self.openai_client.generate_text(prompt=prompt)

    def _create_prompt(
        self,
        persona: Persona,
        content_type: str,
        topic: str,
        platform: str,
        additional_context: Optional[str] = None,
        max_length: Optional[int] = None,
    ) -> str:
        """
        Create a prompt for content generation.

        Args:
            persona: The persona to generate content for.
            content_type: The type of content to generate.
            topic: The topic to generate content about.
            platform: The platform to generate content for.
            additional_context: Additional context for generation.
            max_length: Maximum length of the generated content.

        Returns:
            The prompt for content generation.
        """
        # Format persona attributes
        interests = ", ".join(persona.interests) if persona.interests else "None"
        values = ", ".join(persona.values) if persona.values else "None"
        expertise = ", ".join(persona.expertise) if persona.expertise else "None"

        # Create platform-specific instructions
        platform_instructions = self._get_platform_instructions(platform, content_type)

        # Create length instructions
        length_instructions = ""
        if max_length:
            length_instructions = f"The content must be no longer than {max_length} characters."

        # Create the prompt
        prompt = f"""
        You are {persona.name}, with the following characteristics:

        Background: {persona.background}
        Interests: {interests}
        Values: {values}
        Expertise: {expertise}
        Tone: {persona.tone}
        Purpose: {persona.purpose}

        Create a {content_type} about {topic} for {platform}.

        {platform_instructions}

        {length_instructions}

        {additional_context or ""}

        Write in the first person as {persona.name}. Maintain the persona's tone and style.
        Focus on providing value to the audience while staying true to the persona's values and expertise.
        """

        return prompt.strip()

    def _create_interaction_prompt(
        self,
        persona: Persona,
        interaction_text: str,
        interaction_type: str,
        platform: str,
        original_content: Optional[str] = None,
    ) -> str:
        """
        Create a prompt for interaction response generation.

        Args:
            persona: The persona to generate a response for.
            interaction_text: The text of the interaction to respond to.
            interaction_type: The type of interaction.
            platform: The platform the interaction is on.
            original_content: The original content that was interacted with.

        Returns:
            The prompt for interaction response generation.
        """
        # Format persona attributes
        interests = ", ".join(persona.interests) if persona.interests else "None"
        values = ", ".join(persona.values) if persona.values else "None"
        expertise = ", ".join(persona.expertise) if persona.expertise else "None"

        # Create platform-specific instructions
        platform_instructions = self._get_platform_instructions(platform, "reply")

        # Create the prompt
        prompt = f"""
        You are {persona.name}, with the following characteristics:

        Background: {persona.background}
        Interests: {interests}
        Values: {values}
        Expertise: {expertise}
        Tone: {persona.tone}
        Purpose: {persona.purpose}

        Someone has {interaction_type}ed to you on {platform} with the following message:

        "{interaction_text}"

        {f'This was in response to your original content: "{original_content}"' if original_content else ''}

        Craft a response to this {interaction_type}.

        {platform_instructions}

        Write in the first person as {persona.name}. Maintain the persona's tone and style.
        Be engaging and authentic while staying true to the persona's values and expertise.
        """

        return prompt.strip()

    def _create_agent_input(self, content_type: str, topic: str, platform: str, additional_context: Optional[str] = None, max_length: Optional[int] = None) -> str:
        """
        Create an input prompt for the agent to generate content.

        Args:
            content_type: The type of content to generate.
            topic: The topic to generate content about.
            platform: The platform to generate content for.
            additional_context: Additional context for generation.
            max_length: Maximum length of the generated content.

        Returns:
            The input prompt for the agent.
        """
        platform_instructions = self._get_platform_instructions(platform, content_type)

        length_instructions = ""
        if max_length:
            length_instructions = f"The content must be no longer than {max_length} characters."

        prompt = f"""Generate a {content_type} about {topic} for {platform}.

{platform_instructions}

{length_instructions}

{additional_context or ''}

Provide only the content itself without any explanations or additional text."""

        return prompt.strip()

    def _create_agent_interaction_input(self, interaction_text: str, interaction_type: str, platform: str, original_content: Optional[str] = None) -> str:
        """
        Create an input prompt for the agent to generate an interaction response.

        Args:
            interaction_text: The text of the interaction to respond to.
            interaction_type: The type of interaction.
            platform: The platform the interaction is on.
            original_content: The original content that was interacted with.

        Returns:
            The input prompt for the agent.
        """
        platform_instructions = self._get_platform_instructions(platform, "reply")

        original_content_text = ""
        if original_content:
            original_content_text = f"This was in response to your original content: \"{original_content}\""

        prompt = f"""Someone has {interaction_type}ed to you on {platform} with the following message:

"{interaction_text}"

{original_content_text}

Craft a response to this {interaction_type}.

{platform_instructions}

Provide only the response itself without any explanations or additional text."""

        return prompt.strip()

    def _get_platform_instructions(self, platform: str, content_type: str) -> str:
        """
        Get platform-specific instructions for content generation.

        Args:
            platform: The platform to generate content for.
            content_type: The type of content to generate.

        Returns:
            Platform-specific instructions.
        """
        if platform.lower() == "twitter":
            return "Keep it concise, under 280 characters. Use hashtags sparingly and effectively."
        elif platform.lower() == "linkedin":
            if content_type.lower() == "post":
                return "Be professional but engaging. Focus on providing value. Use line breaks for readability. Include a call to action if appropriate."
            elif content_type.lower() == "article":
                return "Be thorough and insightful. Structure with headings and subheadings. Provide actionable insights. Maintain a professional tone."
        elif platform.lower() == "bluesky":
            return "Be conversational and authentic. You can use up to 300 characters. Feel free to use hashtags if relevant."

        return "Adapt your content to the platform's conventions and audience expectations."


# Global content generator instance
_content_generator: Optional[ContentGenerator] = None


def get_content_generator() -> ContentGenerator:
    """
    Get the content generator instance.

    Returns:
        The content generator instance.
    """
    global _content_generator
    if _content_generator is None:
        _content_generator = ContentGenerator()
    return _content_generator
