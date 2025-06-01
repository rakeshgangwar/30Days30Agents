"""
Logging configuration for the Meeting Assistant application.
Configures loguru for structured logging.
"""

import os
import sys
from pathlib import Path
from loguru import logger

from config.settings import settings

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Log file path
log_file = log_dir / "app.log"

# Configure loguru logger
log_level = settings.LOG_LEVEL

# Remove default handler
logger.remove()

# Add console handler with appropriate format
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=log_level,
    colorize=True,
)

# Add file handler with rotation
logger.add(
    log_file,
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level=log_level,
    rotation="500 MB",
    retention="10 days",
    compression="zip",
)

# Add context variables for environment
logger = logger.bind(environment=settings.ENVIRONMENT)

# Export logger
__all__ = ["logger"]
