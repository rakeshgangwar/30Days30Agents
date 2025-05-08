"""Configuration module for the Research Assistant."""

import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the application
BASE_DIR = Path(__file__).parent.parent.absolute()

# Directory for caching web pages
CACHE_DIR = os.getenv("CACHE_DIR", "./cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Directory for storing research database
RESEARCH_DB_DIR = os.getenv("RESEARCH_DB_DIR", "./research_db")
os.makedirs(RESEARCH_DB_DIR, exist_ok=True)

# Debug mode
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EXA_API_KEY = os.getenv("EXA_API_KEY")
GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Search engine configuration
DEFAULT_SEARCH_ENGINE = "exa"  # Options: exa, serpapi, google
MAX_SEARCH_RESULTS = 10

# Research parameters
MIN_SOURCES = 3
MAX_SOURCES = 15
DEFAULT_RESEARCH_DEPTH = "medium"  # Options: light, medium, deep

# Model configuration
DEFAULT_LLM_MODEL = "gpt-3.5-turbo"
GEMINI_MODEL = "gemini-1.5-pro"

# Web browsing configuration
USE_PLAYWRIGHT = True
PLAYWRIGHT_TIMEOUT = 60000  # milliseconds
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Document processing
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
MAX_DOCUMENT_LENGTH = 10000

# Vector store settings
EMBEDDING_MODEL = "openai"  # Options: openai, gemini
VECTOR_STORE_TYPE = "chroma"  # Options: chroma, faiss

def get_llm_config() -> Dict[str, str]:
    """Get the LLM configuration based on available API keys."""
    if OPENAI_API_KEY:
        return {
            "provider": "openai",
            "model": DEFAULT_LLM_MODEL,
            "api_key": OPENAI_API_KEY
        }
    elif GOOGLE_GEMINI_API_KEY:
        return {
            "provider": "gemini",
            "model": GEMINI_MODEL,
            "api_key": GOOGLE_GEMINI_API_KEY
        }
    else:
        raise ValueError("No valid LLM API key found in environment variables.")

def get_search_config() -> Dict[str, str]:
    """Get the search engine configuration based on available API keys."""
    if EXA_API_KEY and DEFAULT_SEARCH_ENGINE == "exa":
        return {
            "engine": "exa",
            "api_key": EXA_API_KEY
        }
    elif SERPAPI_API_KEY:
        return {
            "engine": "serpapi",
            "api_key": SERPAPI_API_KEY
        }
    else:
        raise ValueError("No valid search API key found in environment variables.")

def validate_config() -> None:
    """Validate the configuration and check for required API keys."""
    missing_keys = []
    
    if not OPENAI_API_KEY and not GOOGLE_GEMINI_API_KEY:
        missing_keys.append("OPENAI_API_KEY or GOOGLE_GEMINI_API_KEY")
    
    if not EXA_API_KEY and not SERPAPI_API_KEY:
        missing_keys.append("EXA_API_KEY or SERPAPI_API_KEY")
    
    if missing_keys:
        raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")