"""
Celery Configuration Module

This module configures Celery for task scheduling.
"""

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "digi_persona",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.core.tasks.content_tasks"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    "process-due-content-every-minute": {
        "task": "app.core.tasks.content_tasks.process_due_content",
        "schedule": crontab(minute="*"),  # Run every minute
    },
}

# Export Celery app
app = celery_app
