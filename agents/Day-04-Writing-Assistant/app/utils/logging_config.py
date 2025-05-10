"""
Logging configuration for the Writing Assistant API.
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import sys
import os

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.core.config import settings

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)


def setup_logging():
    """Configure logging for the application."""
    log_level = getattr(logging, settings.LOG_LEVEL)
    
    # Logger setup
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers if any
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    
    # Formatter
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = RotatingFileHandler(
        logs_dir / "writing_assistant.log", 
        maxBytes=10485760,  # 10MB
        backupCount=10,
    )
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(log_level)
    root_logger.addHandler(file_handler)
    
    # Set specific log levels for some noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    
    return root_logger