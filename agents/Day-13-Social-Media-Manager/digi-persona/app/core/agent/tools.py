"""
Agent Tools Module

This module provides tools for LLM agents with persona context.
It handles the creation and configuration of persona-specific tools.
"""

from typing import List, Optional

from langchain.tools import BaseTool
from langchain.tools.base import ToolException
from sqlalchemy.orm import Session

from app.core.content.manager import get_content_manager
from app.core.personas.manager import get_persona_manager
from app.db.models.persona import Persona
from app.db.session import SessionLocal


def get_persona_tools(persona: Persona) -> List[BaseTool]:
    """
    Get tools for the specified persona.

    Args:
        persona: The persona to get tools for.

    Returns:
        A list of tools configured for the persona.
    """
    # Create basic tools
    tools = [
        ContentGenerationTool(persona_id=persona.id),
        ContentPostingTool(persona_id=persona.id),
        InteractionResponseTool(persona_id=persona.id),
        SearchTool(),
    ]

    return tools


class ContentGenerationTool(BaseTool):
    """Tool for generating content based on persona attributes."""

    name = "content_generation"
    description = "Generate content for social media platforms based on the persona's attributes."

    def __init__(self, persona_id: int):
        """
        Initialize the content generation tool.

        Args:
            persona_id: The ID of the persona to generate content for.
        """
        self.persona_id = persona_id
        super().__init__()

    def _run(self, content_type: str, topic: str, platform: str = "twitter", additional_context: Optional[str] = None, max_length: Optional[int] = None) -> str:
        """
        Generate content for the specified type and topic.

        Args:
            content_type: The type of content to generate (e.g., tweet, post, article).
            topic: The topic to generate content about.
            platform: The platform to generate content for (e.g., twitter, linkedin, bluesky).
            additional_context: Additional context for generation.
            max_length: Maximum length of the generated content.

        Returns:
            The generated content.

        Raises:
            ToolException: If content generation fails.
        """
        try:
            # Create a database session
            db = SessionLocal()
            try:
                # Get the persona manager and content manager
                persona_manager = get_persona_manager(db)
                content_manager = get_content_manager(db)

                # Get the persona
                persona = persona_manager.get_persona(self.persona_id)
                if not persona:
                    raise ToolException(f"Persona with ID {self.persona_id} not found")

                # Generate content
                content_data = content_manager.generate_content(
                    persona_id=self.persona_id,
                    content_type=content_type,
                    topic=topic,
                    platform=platform,
                    additional_context=additional_context,
                    max_length=max_length,
                    save=False,
                )

                return content_data["text"]
            finally:
                db.close()
        except Exception as e:
            raise ToolException(f"Error generating content: {str(e)}")

    async def _arun(self, content_type: str, topic: str, platform: str = "twitter", additional_context: Optional[str] = None, max_length: Optional[int] = None) -> str:
        """
        Asynchronously generate content for the specified type and topic.

        Args:
            content_type: The type of content to generate (e.g., tweet, post, article).
            topic: The topic to generate content about.
            platform: The platform to generate content for (e.g., twitter, linkedin, bluesky).
            additional_context: Additional context for generation.
            max_length: Maximum length of the generated content.

        Returns:
            The generated content.

        Raises:
            ToolException: If content generation fails.
        """
        return self._run(content_type, topic, platform, additional_context, max_length)


class ContentPostingTool(BaseTool):
    """Tool for posting content to social media platforms."""

    name = "content_posting"
    description = "Post content to social media platforms."

    def __init__(self, persona_id: int):
        """
        Initialize the content posting tool.

        Args:
            persona_id: The ID of the persona to post content for.
        """
        self.persona_id = persona_id
        super().__init__()

    def _run(self, platform: str, content: str, content_type: str = "post") -> str:
        """
        Post content to the specified platform.

        Args:
            platform: The platform to post to (e.g., twitter, linkedin, bluesky).
            content: The content to post.
            content_type: The type of content to post (e.g., tweet, post, article).

        Returns:
            A confirmation message.

        Raises:
            ToolException: If posting fails.
        """
        try:
            # Create a database session
            db = SessionLocal()
            try:
                # Get the persona manager and content manager
                content_manager = get_content_manager(db)

                # Create content
                content_data = {
                    "persona_id": self.persona_id,
                    "content_type": content_type,
                    "text": content,
                    "platform": platform,
                    "status": "pending_review",  # Set to pending_review for human approval
                }

                # Save content to database
                content_item = content_manager.create_content(content_data)

                return f"Content created and pending review. Content ID: {content_item.id}"
            finally:
                db.close()
        except Exception as e:
            raise ToolException(f"Error posting content: {str(e)}")

    async def _arun(self, platform: str, content: str, content_type: str = "post") -> str:
        """
        Asynchronously post content to the specified platform.

        Args:
            platform: The platform to post to (e.g., twitter, linkedin, bluesky).
            content: The content to post.
            content_type: The type of content to post (e.g., tweet, post, article).

        Returns:
            A confirmation message.

        Raises:
            ToolException: If posting fails.
        """
        return self._run(platform, content, content_type)


class InteractionResponseTool(BaseTool):
    """Tool for responding to interactions on social media platforms."""

    name = "interaction_response"
    description = "Respond to interactions on social media platforms."

    def __init__(self, persona_id: int):
        """
        Initialize the interaction response tool.

        Args:
            persona_id: The ID of the persona to respond as.
        """
        self.persona_id = persona_id
        super().__init__()

    def _run(self, platform: str, interaction_id: str, response: str) -> str:
        """
        Respond to an interaction on the specified platform.

        Args:
            platform: The platform to respond on (e.g., twitter, linkedin, bluesky).
            interaction_id: The ID of the interaction to respond to.
            response: The response to send.

        Returns:
            A confirmation message.

        Raises:
            ToolException: If responding fails.
        """
        try:
            # Create a database session
            db = SessionLocal()
            try:
                # In a real implementation with platform integrations, we would:
                # 1. Get the interaction from the database
                # 2. Create a response in the database
                # 3. Send the response to the platform
                # 4. Update the interaction status

                # For now, we'll just create a content item for the response
                content_manager = get_content_manager(db)

                # Create content for the response
                content_data = {
                    "persona_id": self.persona_id,
                    "content_type": "reply",
                    "text": response,
                    "platform": platform,
                    "status": "pending_review",  # Set to pending_review for human approval
                    "content_metadata": {
                        "interaction_id": interaction_id,
                        "is_response": True,
                    },
                }

                # Save content to database
                content_item = content_manager.create_content(content_data)

                return f"Response created and pending review. Content ID: {content_item.id}"
            finally:
                db.close()
        except Exception as e:
            raise ToolException(f"Error responding to interaction: {str(e)}")

    async def _arun(self, platform: str, interaction_id: str, response: str) -> str:
        """
        Asynchronously respond to an interaction on the specified platform.

        Args:
            platform: The platform to respond on (e.g., twitter, linkedin, bluesky).
            interaction_id: The ID of the interaction to respond to.
            response: The response to send.

        Returns:
            A confirmation message.

        Raises:
            ToolException: If responding fails.
        """
        return self._run(platform, interaction_id, response)


class SearchTool(BaseTool):
    """Tool for searching for information."""

    name = "search"
    description = "Search for information on the web."

    def _run(self, query: str) -> str:
        """
        Search for information using the specified query.

        Args:
            query: The search query.

        Returns:
            The search results.

        Raises:
            ToolException: If searching fails.
        """
        try:
            # In a real implementation, this would call a search API
            # For now, we'll just return a placeholder
            return f"Search results for: {query}"
        except Exception as e:
            raise ToolException(f"Error searching: {str(e)}")

    async def _arun(self, query: str) -> str:
        """
        Asynchronously search for information using the specified query.

        Args:
            query: The search query.

        Returns:
            The search results.

        Raises:
            ToolException: If searching fails.
        """
        return self._run(query)
