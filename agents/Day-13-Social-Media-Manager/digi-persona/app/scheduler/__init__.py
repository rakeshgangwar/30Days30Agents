"""
Scheduler Package

This package provides task scheduling functionality for the application.
"""

from app.scheduler.worker import app as celery_app

__all__ = ["celery_app"]
