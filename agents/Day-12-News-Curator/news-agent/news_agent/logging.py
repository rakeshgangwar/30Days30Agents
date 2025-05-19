"""
Logging configuration for the news curator agent.

This module provides a centralized logging configuration for the entire application.
It sets up loggers with appropriate handlers and formatters for different components.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Union

# Define log levels
TRACE_LEVEL = 5  # Custom level below DEBUG
logging.addLevelName(TRACE_LEVEL, "TRACE")


def trace(self, message, *args, **kwargs):
    """Log 'message' at TRACE level (more detailed than DEBUG)."""
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kwargs)


# Add trace method to Logger class
logging.Logger.trace = trace

# Default format strings
DEFAULT_FORMAT = "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
DETAILED_FORMAT = "%(asctime)s [%(levelname)8s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
SIMPLE_FORMAT = "[%(levelname)s] %(message)s"

# Global log level (can be overridden by environment variable)
LOG_LEVEL = os.environ.get("NEWS_AGENT_LOG_LEVEL", "INFO").upper()

# Log directory
LOG_DIR = Path(os.environ.get("NEWS_AGENT_LOG_DIR", "logs"))


class TaskContextFilter(logging.Filter):
    """Filter that adds task context information to log records."""

    def filter(self, record):
        if not hasattr(record, "task_id"):
            record.task_id = "main"
        return True


def get_logger(
    name: str, 
    level: Optional[Union[int, str]] = None, 
    format_string: Optional[str] = None,
    file_output: bool = False,
) -> logging.Logger:
    """Get a configured logger.

    Args:
        name: Name of the logger
        level: Log level (defaults to global LOG_LEVEL)
        format_string: Format string for log messages
        file_output: Whether to also log to a file

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    # Only configure if it hasn't been configured yet
    if not logger.handlers:
        # Set level
        if level is None:
            level = LOG_LEVEL
        logger.setLevel(level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Create formatter
        if format_string is None:
            format_string = DEFAULT_FORMAT
        formatter = logging.Formatter(format_string)
        console_handler.setFormatter(formatter)
        
        # Add filter for task context
        task_filter = TaskContextFilter()
        console_handler.addFilter(task_filter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
        
        # Add file handler if requested
        if file_output:
            # Create log directory if it doesn't exist
            LOG_DIR.mkdir(exist_ok=True, parents=True)
            
            # Create file handler
            file_handler = logging.FileHandler(LOG_DIR / f"{name}.log")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            file_handler.addFilter(task_filter)
            logger.addHandler(file_handler)
    
    return logger


# Configure third-party loggers
def configure_third_party_loggers():
    """Configure loggers for third-party libraries."""
    # Set higher log level for noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    # Configure anyio logger with detailed format
    anyio_logger = get_logger("anyio", level="INFO", format_string=DETAILED_FORMAT)
    
    # Configure MCP loggers with detailed format
    mcp_logger = get_logger("mcp", level="DEBUG", format_string=DETAILED_FORMAT, file_output=True)
    mcp_client_logger = get_logger("mcp.client", level="DEBUG", format_string=DETAILED_FORMAT, file_output=True)
    mcp_server_logger = get_logger("mcp.server", level="DEBUG", format_string=DETAILED_FORMAT, file_output=True)
    
    # Configure pydantic_ai loggers
    pydantic_ai_logger = get_logger("pydantic_ai", level="DEBUG", format_string=DETAILED_FORMAT, file_output=True)
    
    return {
        "anyio": anyio_logger,
        "mcp": mcp_logger,
        "mcp.client": mcp_client_logger,
        "mcp.server": mcp_server_logger,
        "pydantic_ai": pydantic_ai_logger,
    }


# Main application loggers
def configure_app_loggers():
    """Configure loggers for the application."""
    # Main application logger
    app_logger = get_logger("news_agent", level=LOG_LEVEL, format_string=DETAILED_FORMAT, file_output=True)
    
    # Component loggers
    agent_logger = get_logger("news_agent.agent", level=LOG_LEVEL, format_string=DETAILED_FORMAT, file_output=True)
    freshrss_logger = get_logger("news_agent.freshrss", level=LOG_LEVEL, format_string=DETAILED_FORMAT, file_output=True)
    interactive_logger = get_logger("news_agent.interactive", level=LOG_LEVEL, format_string=DETAILED_FORMAT, file_output=True)
    
    # Tools loggers
    tools_logger = get_logger("news_agent.tools", level=LOG_LEVEL, format_string=DETAILED_FORMAT, file_output=True)
    
    return {
        "app": app_logger,
        "agent": agent_logger,
        "freshrss": freshrss_logger,
        "interactive": interactive_logger,
        "tools": tools_logger,
    }


# Initialize all loggers
def setup_logging():
    """Set up all loggers for the application."""
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    
    # Configure third-party loggers
    third_party_loggers = configure_third_party_loggers()
    
    # Configure application loggers
    app_loggers = configure_app_loggers()
    
    # Return all configured loggers
    return {**third_party_loggers, **app_loggers}


# Global loggers dictionary
loggers = setup_logging()
