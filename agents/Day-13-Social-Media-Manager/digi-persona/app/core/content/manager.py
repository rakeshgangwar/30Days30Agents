"""
Content Manager Module

This module provides functionality for managing content.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.ai.generator import ContentGenerator, get_content_generator
from app.core.personas.manager import PersonaManager, get_persona_manager
from app.db.models.content import Content
from app.db.models.persona import Persona


class ContentManager:
    """
    Manager for content operations.

    This class provides methods for creating, retrieving, updating, and deleting
    content, as well as generating content using AI.
    """

    def __init__(
        self,
        db: Session,
        persona_manager: Optional[PersonaManager] = None,
        content_generator: Optional[ContentGenerator] = None,
    ):
        """
        Initialize the content manager.

        Args:
            db: The database session.
            persona_manager: The persona manager to use. If None, gets a new instance.
            content_generator: The content generator to use. If None, gets a new instance.
        """
        self.db = db
        self.persona_manager = persona_manager or get_persona_manager(db)
        self.content_generator = content_generator or get_content_generator()

    def create_content(self, content_data: Dict[str, Any]) -> Content:
        """
        Create a new content item.

        Args:
            content_data: Dictionary containing content attributes.

        Returns:
            The created content item.
        """
        content = Content(**content_data)
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content

    def get_content(self, content_id: int) -> Optional[Content]:
        """
        Get a content item by ID.

        Args:
            content_id: The ID of the content item to get.

        Returns:
            The content item, or None if not found.
        """
        return self.db.query(Content).filter(Content.id == content_id).first()

    def get_content_items(
        self,
        persona_id: Optional[int] = None,
        platform: Optional[str] = None,
        content_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Content]:
        """
        Get a list of content items.

        Args:
            persona_id: Filter by persona ID.
            platform: Filter by platform.
            content_type: Filter by content type.
            status: Filter by status.
            skip: Number of content items to skip.
            limit: Maximum number of content items to return.

        Returns:
            List of content items.
        """
        query = self.db.query(Content)

        if persona_id is not None:
            query = query.filter(Content.persona_id == persona_id)

        if platform is not None:
            query = query.filter(Content.platform == platform)

        if content_type is not None:
            query = query.filter(Content.content_type == content_type)

        if status is not None:
            query = query.filter(Content.status == status)

        return query.order_by(desc(Content.created_at)).offset(skip).limit(limit).all()

    def update_content(self, content_id: int, content_data: Dict[str, Any]) -> Optional[Content]:
        """
        Update a content item.

        Args:
            content_id: The ID of the content item to update.
            content_data: Dictionary containing updated content attributes.

        Returns:
            The updated content item, or None if not found.
        """
        content = self.get_content(content_id)
        if not content:
            return None

        for key, value in content_data.items():
            if hasattr(content, key):
                setattr(content, key, value)

        self.db.commit()
        self.db.refresh(content)
        return content

    def delete_content(self, content_id: int) -> bool:
        """
        Delete a content item.

        Args:
            content_id: The ID of the content item to delete.

        Returns:
            True if the content item was deleted, False if not found.
        """
        content = self.get_content(content_id)
        if not content:
            return False

        self.db.delete(content)
        self.db.commit()
        return True

    def update_content_status(self, content_id: int, status: str) -> Optional[Content]:
        """
        Update the status of a content item.

        Args:
            content_id: The ID of the content item to update.
            status: The new status.

        Returns:
            The updated content item, or None if not found.
        """
        return self.update_content(content_id, {"status": status})

    def approve_content(self, content_id: int) -> Optional[Content]:
        """
        Approve a content item.

        Args:
            content_id: The ID of the content item to approve.

        Returns:
            The approved content item, or None if not found.
        """
        return self.update_content_status(content_id, "approved")

    def publish_content(self, content_id: int) -> Optional[Content]:
        """
        Mark a content item as published.

        Args:
            content_id: The ID of the content item to mark as published.

        Returns:
            The published content item, or None if not found.
        """
        return self.update_content(
            content_id,
            {
                "status": "published",
                "published_time": datetime.utcnow(),
            },
        )

    def generate_content(
        self,
        persona_id: int,
        content_type: str,
        topic: str,
        platform: str,
        additional_context: Optional[str] = None,
        max_length: Optional[int] = None,
        save: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate content for a persona.

        Args:
            persona_id: The ID of the persona to generate content for.
            content_type: The type of content to generate.
            topic: The topic to generate content about.
            platform: The platform to generate content for.
            additional_context: Additional context for generation.
            max_length: Maximum length of the generated content.
            save: Whether to save the generated content to the database.

        Returns:
            Dictionary containing the generated content and metadata.

        Raises:
            ValueError: If the persona is not found.
        """
        # Get the persona
        persona = self.persona_manager.get_persona(persona_id)
        if not persona:
            raise ValueError(f"Persona with ID {persona_id} not found")

        # Generate the content
        text = self.content_generator.generate_content(
            persona=persona,
            content_type=content_type,
            topic=topic,
            platform=platform,
            additional_context=additional_context,
            max_length=max_length,
        )

        # Create the content data
        content_data = {
            "persona_id": persona_id,
            "content_type": content_type,
            "text": text,
            "platform": platform,
            "status": "draft",
            "content_metadata": {
                "topic": topic,
                "additional_context": additional_context,
                "max_length": max_length,
                "generated_at": datetime.utcnow().isoformat(),
            },
        }

        # Save the content if requested
        if save:
            content = self.create_content(content_data)
            content_data["id"] = content.id

        return content_data

    def schedule_content(
        self,
        content_id: int,
        scheduled_time: datetime,
    ) -> Optional[Content]:
        """
        Schedule a content item for posting.

        Args:
            content_id: The ID of the content item to schedule.
            scheduled_time: The time to schedule the content for.

        Returns:
            The scheduled content item, or None if not found.
        """
        return self.update_content(
            content_id,
            {
                "scheduled_time": scheduled_time,
                "status": "scheduled",
            },
        )


def get_content_manager(db: Session) -> ContentManager:
    """
    Get a content manager instance.

    Args:
        db: The database session.

    Returns:
        A content manager instance.
    """
    return ContentManager(db)
