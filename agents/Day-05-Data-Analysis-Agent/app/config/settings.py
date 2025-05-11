"""
Data Analysis Agent - Configuration Settings

This module contains configuration settings and environment variables for the Data Analysis Agent.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# LLM Settings
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "anthropic/claude-3.7-sonnet")
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", "0.2"))
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", "1024"))
DEFAULT_REQUEST_TIMEOUT = int(os.getenv("DEFAULT_REQUEST_TIMEOUT", "60"))
DEFAULT_MAX_RETRIES = int(os.getenv("DEFAULT_MAX_RETRIES", "3"))

# Agent Settings
AGENT_TYPE = os.getenv("AGENT_TYPE", "OPENAI_FUNCTIONS")
AGENT_MAX_ITERATIONS = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
AGENT_MAX_EXECUTION_TIME = int(os.getenv("AGENT_MAX_EXECUTION_TIME", "30"))
AGENT_EARLY_STOPPING_METHOD = os.getenv("AGENT_EARLY_STOPPING_METHOD", "force")
AGENT_ALLOW_DANGEROUS_CODE = os.getenv("AGENT_ALLOW_DANGEROUS_CODE", "true").lower() == "true"

# Database Settings
DEFAULT_SQLITE_PATH = os.getenv("DEFAULT_SQLITE_PATH", "test_data.db")
DEFAULT_DB_TYPE = os.getenv("DEFAULT_DB_TYPE", "sqlite")

# Application Settings
APP_TITLE = "Data Analysis Agent"
APP_ICON = "📊"
APP_LAYOUT = "wide"
APP_INITIAL_SIDEBAR_STATE = "expanded"
