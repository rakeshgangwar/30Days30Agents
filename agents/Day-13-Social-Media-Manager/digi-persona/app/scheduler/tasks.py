"""
Celery Tasks Module

This module provides Celery tasks for the application.
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from app.scheduler.worker import app
from app.db.session import SessionLocal
from app.core.content.scheduler import get_content_scheduler
from app.core.content.manager import get_content_manager
from app.core.platforms.manager import get_platform_manager
from app.core.personas.context import persona_context
from app.db.models.content import Content


@app.task
def check_scheduled_content() -> Dict[str, Any]:
    """
    Check for content that is due for posting and post it.

    Returns:
        A dictionary with the results of the operation.
    """
    db = SessionLocal()
    try:
        scheduler = get_content_scheduler(db)
        due_content = scheduler.get_due_content()

        posted_count = 0
        failed_count = 0

        for content in due_content:
            try:
                # Set persona context
                persona_context.set_persona(content.persona_id)

                # Get the platform manager
                platform_manager = get_platform_manager(db)

                # Get platform connection for this persona and platform
                connections = platform_manager.get_platform_connections(
                    persona_id=content.persona_id,
                    active_only=True
                )

                # Find the connection for this platform
                platform_connection = next(
                    (conn for conn in connections if conn.platform_name.lower() == content.platform.lower()),
                    None
                )

                if not platform_connection:
                    raise ValueError(f"No active connection found for platform {content.platform}")

                # Post the content to the platform with retries
                max_retries = 3
                retry_count = 0
                success = False
                last_error = None

                while retry_count < max_retries and not success:
                    try:
                        print(f"Attempting to post content {content.id} to {content.platform} (attempt {retry_count + 1}/{max_retries})")

                        post_info = platform_manager.post_content(
                            persona_id=content.persona_id,
                            platform_name=content.platform,
                            content=content.text,
                            media_urls=content.media_urls or []
                        )

                        # Update the content with the post info
                        content_manager = get_content_manager(db)
                        content_manager.update_content(
                            content.id,
                            {
                                "status": "posted",
                                "posted_at": datetime.now(timezone.utc),
                                "external_id": post_info.get("id", ""),
                                "external_url": post_info.get("url", ""),
                            },
                        )

                        print(f"Successfully posted content {content.id} to {content.platform}: {post_info}")
                        posted_count += 1
                        success = True
                        break
                    except Exception as e:
                        last_error = e
                        retry_count += 1
                        print(f"Attempt {retry_count}/{max_retries} failed: {str(e)}")

                        # Add a delay between retries
                        import time
                        time.sleep(2 * retry_count)  # Exponential backoff

                if not success:
                    # If all retries failed, update the content status to "failed"
                    content_manager = get_content_manager(db)
                    content_manager.update_content(
                        content.id,
                        {
                            "status": "failed",
                            "content_metadata": {
                                **(content.content_metadata or {}),
                                "error": str(last_error),
                                "failed_at": datetime.now(timezone.utc).isoformat()
                            }
                        },
                    )
                    raise ValueError(f"Failed to post content after {max_retries} retries: {str(last_error)}")
            except Exception as e:
                # Log the error
                print(f"Error posting content {content.id}: {str(e)}")
                failed_count += 1

        return {
            "task": "check_scheduled_content",
            "due_content_count": len(due_content),
            "posted_count": posted_count,
            "failed_count": failed_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        db.close()


@app.task
def monitor_interactions() -> Dict[str, Any]:
    """
    Monitor interactions across platforms for all personas.

    Returns:
        A dictionary with the results of the operation.
    """
    db = SessionLocal()
    try:
        # This would call the platform integration to check for new interactions
        # For now, just return a placeholder
        return {
            "task": "monitor_interactions",
            "new_interactions_count": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        db.close()


@app.task
def generate_content(
    persona_id: int,
    content_type: str,
    topic: str,
    platform: str,
    additional_context: Optional[str] = None,
    max_length: Optional[int] = None,
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

    Returns:
        A dictionary with the results of the operation.
    """
    db = SessionLocal()
    try:
        # Set persona context
        persona_context.set_persona(persona_id)

        # Get content manager
        content_manager = get_content_manager(db)

        # Generate content
        content_data = content_manager.generate_content(
            persona_id=persona_id,
            content_type=content_type,
            topic=topic,
            platform=platform,
            additional_context=additional_context,
            max_length=max_length,
            save=True,
        )

        return {
            "task": "generate_content",
            "persona_id": persona_id,
            "content_id": content_data.get("id"),
            "content_type": content_type,
            "platform": platform,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        db.close()


@app.task
def schedule_content_generation_for_all_personas() -> Dict[str, Any]:
    """
    Schedule content generation for all active personas.

    Returns:
        A dictionary with the results of the operation.
    """
    db = SessionLocal()
    try:
        # This would get all active personas and schedule content generation
        # For now, just return a placeholder
        return {
            "task": "schedule_content_generation_for_all_personas",
            "scheduled_tasks_count": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        db.close()
