"""
Celery Worker Module

This module provides the Celery worker configuration for task scheduling.
"""

from celery import Celery
from app.core.config import settings

# Create Celery app
app = Celery(
    'digi-persona',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.scheduler.tasks']
)

# Configure Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_hijack_root_logger=False,
    broker_connection_retry_on_startup=True,
)

# Optional: Define periodic tasks
app.conf.beat_schedule = {
    'check-scheduled-content-every-minute': {
        'task': 'app.scheduler.tasks.check_scheduled_content',
        'schedule': 60.0,  # Every minute
    },
    'monitor-interactions-every-5-minutes': {
        'task': 'app.scheduler.tasks.monitor_interactions',
        'schedule': 300.0,  # Every 5 minutes
    },
}

if __name__ == '__main__':
    app.start()
