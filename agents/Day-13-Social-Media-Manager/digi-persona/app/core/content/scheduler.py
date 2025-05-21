"""
Content Scheduler Module

This module provides functionality for scheduling content.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.core.ai.generator import ContentGenerator
from app.core.content.manager import ContentManager, get_content_manager
from app.db.models.content import Content


class ContentScheduler:
    """
    Scheduler for content operations.

    This class provides methods for scheduling content and retrieving
    content that is due for posting.
    """

    def __init__(self, db: Session, content_manager: Optional[ContentManager] = None, content_generator: Optional[ContentGenerator] = None):
        """
        Initialize the content scheduler.

        Args:
            db: The database session.
            content_manager: Optional content manager instance.
            content_generator: Optional content generator instance.
        """
        self.db = db
        self.content_manager = content_manager or get_content_manager(db)
        self.content_generator = content_generator or ContentGenerator()

    def get_due_content(self, current_time: Optional[datetime] = None) -> List[Content]:
        """
        Get content that is due for posting.

        Args:
            current_time: The current time. If None, uses the current UTC time.

        Returns:
            List of content items that are due for posting.
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        return (
            self.db.query(Content)
            .filter(
                and_(
                    Content.status == "scheduled",
                    Content.scheduled_time <= current_time,
                )
            )
            .all()
        )

    def get_upcoming_content(
        self,
        persona_id: Optional[int] = None,
        platform: Optional[str] = None,
        hours_ahead: int = 24,
        current_time: Optional[datetime] = None,
    ) -> List[Content]:
        """
        Get content that is scheduled for posting in the near future.

        Args:
            persona_id: Filter by persona ID.
            platform: Filter by platform.
            hours_ahead: Number of hours ahead to look.
            current_time: The current time. If None, uses the current UTC time.

        Returns:
            List of content items scheduled for posting in the near future.
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        end_time = current_time + timedelta(hours=hours_ahead)

        query = self.db.query(Content).filter(
            and_(
                Content.status == "scheduled",
                Content.scheduled_time > current_time,
                Content.scheduled_time <= end_time,
            )
        )

        if persona_id is not None:
            query = query.filter(Content.persona_id == persona_id)

        if platform is not None:
            query = query.filter(Content.platform == platform)

        return query.order_by(Content.scheduled_time).all()

    def reschedule_content(self, content_id: int, new_scheduled_time: datetime) -> Optional[Content]:
        """
        Reschedule a content item.

        Args:
            content_id: The ID of the content item to reschedule.
            new_scheduled_time: The new scheduled time.

        Returns:
            The rescheduled content item, or None if not found.
        """
        content = self.db.query(Content).filter(Content.id == content_id).first()
        if not content:
            return None

        content.scheduled_time = new_scheduled_time
        content.status = "scheduled"

        self.db.commit()
        self.db.refresh(content)
        return content

    def cancel_scheduled_content(self, content_id: int) -> Optional[Content]:
        """
        Cancel a scheduled content item.

        Args:
            content_id: The ID of the content item to cancel.

        Returns:
            The cancelled content item, or None if not found.
        """
        content = self.db.query(Content).filter(Content.id == content_id).first()
        if not content:
            return None

        content.scheduled_time = None
        content.status = "draft"

        self.db.commit()
        self.db.refresh(content)
        return content

    def get_posting_schedule(
        self,
        persona_id: int,
        platform: str,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict[str, Any]]:
        """
        Get the posting schedule for a persona on a platform.

        Args:
            persona_id: The ID of the persona.
            platform: The platform.
            start_date: The start date of the schedule.
            end_date: The end date of the schedule.

        Returns:
            List of scheduled content items with metadata.
        """
        scheduled_content = (
            self.db.query(Content)
            .filter(
                and_(
                    Content.persona_id == persona_id,
                    Content.platform == platform,
                    Content.status == "scheduled",
                    Content.scheduled_time >= start_date,
                    Content.scheduled_time <= end_date,
                )
            )
            .order_by(Content.scheduled_time)
            .all()
        )

        return [
            {
                "id": content.id,
                "content_type": content.content_type,
                "text": content.text,
                "scheduled_time": content.scheduled_time,
                "created_at": content.created_at,
            }
            for content in scheduled_content
        ]


    def generate_and_schedule(
        self,
        persona_id: int,
        content_type: str,
        topic: str,
        platform: str,
        scheduled_time: datetime,
        additional_context: Optional[str] = None,
        max_length: Optional[int] = None,
    ) -> Content:
        """
        Generate content and schedule it for posting.

        Args:
            persona_id: ID of the persona to generate content for.
            content_type: Type of content to generate.
            topic: Topic to generate content about.
            platform: Platform to generate content for.
            scheduled_time: When to post the content.
            additional_context: Additional context for generation.
            max_length: Maximum length of the generated content.

        Returns:
            The created and scheduled content item.
        """
        # Generate the content
        content_data = self.content_manager.generate_content(
            persona_id=persona_id,
            content_type=content_type,
            topic=topic,
            platform=platform,
            additional_context=additional_context,
            max_length=max_length,
            save=True,
        )

        # Schedule the content
        return self.reschedule_content(content_data["id"], scheduled_time)

    def generate_batch_and_schedule(
        self,
        persona_id: int,
        content_type: str,
        topics: List[str],
        platform: str,
        start_time: datetime,
        interval_minutes: int = 60,
        additional_context: Optional[str] = None,
        max_length: Optional[int] = None,
    ) -> List[Content]:
        """
        Generate multiple content items and schedule them with regular intervals.

        Args:
            persona_id: ID of the persona to generate content for.
            content_type: Type of content to generate.
            topics: List of topics to generate content about.
            platform: Platform to generate content for.
            start_time: When to post the first content.
            interval_minutes: Minutes between each post.
            additional_context: Additional context for generation.
            max_length: Maximum length of the generated content.

        Returns:
            List of created and scheduled content items.
        """
        scheduled_content = []
        current_time = start_time

        for topic in topics:
            content = self.generate_and_schedule(
                persona_id=persona_id,
                content_type=content_type,
                topic=topic,
                platform=platform,
                scheduled_time=current_time,
                additional_context=additional_context,
                max_length=max_length,
            )
            scheduled_content.append(content)
            current_time += timedelta(minutes=interval_minutes)

        return scheduled_content

    def schedule_batch(
        self,
        content_ids: List[int],
        start_time: datetime,
        interval_minutes: int = 60,
    ) -> List[Content]:
        """
        Schedule multiple content items with regular intervals.

        Args:
            content_ids: List of content IDs to schedule.
            start_time: When to post the first content.
            interval_minutes: Minutes between each post.

        Returns:
            List of updated content items.
        """
        scheduled_content = []
        current_time = start_time

        for content_id in content_ids:
            content = self.reschedule_content(content_id, current_time)
            if content:
                scheduled_content.append(content)
                current_time += timedelta(minutes=interval_minutes)

        return scheduled_content

    def process_due_content(self) -> List[Dict[str, Any]]:
        """
        Process all content that is due for posting.

        Returns:
            List of processed content items with status.
        """
        due_content = self.get_due_content()
        results = []

        for content in due_content:
            try:
                # Get the platform manager
                from app.core.platforms.manager import get_platform_manager
                platform_manager = get_platform_manager(self.db)

                # Post the content to the platform
                post_info = platform_manager.post_content(
                    persona_id=content.persona_id,
                    platform_name=content.platform,
                    content=content.text,
                    media_urls=content.media_urls or []
                )

                # For now, we'll just update the status
                content.status = "published"
                content.published_time = datetime.now(timezone.utc)
                content.external_id = post_info.get("id", "")
                self.db.commit()
                self.db.refresh(content)

                results.append({
                    "content_id": content.id,
                    "success": True,
                    "message": f"Content published successfully on {content.platform}",
                    "post_info": post_info
                })
            except Exception as e:
                results.append({
                    "content_id": content.id,
                    "success": False,
                    "message": f"Failed to publish content: {str(e)}"
                })

        return results


def get_content_scheduler(db: Session) -> ContentScheduler:
    """
    Get a content scheduler instance.

    Args:
        db: The database session.

    Returns:
        A content scheduler instance.
    """
    return ContentScheduler(db)
