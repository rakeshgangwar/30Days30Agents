#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration settings for Personal Assistant.

This module contains all the configuration parameters and settings
for the agent, including model parameters, API settings, and
any other customizable options.
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Model settings
MODEL_NAME = "gpt-4o-mini"  # Default model as specified in agent-spec.md
TEMPERATURE = 0.7  # Default temperature setting
MAX_TOKENS = 1000  # Maximum tokens in response

# API keys (loaded from environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")

# Agent-specific settings
AGENT_NAME = "Personal Assistant"
AGENT_DESCRIPTION = "A foundation agent that handles basic personal assistance tasks such as setting reminders, answering questions, and providing information."

# Prompt templates
SYSTEM_PROMPT = """
You are {agent_name}, an AI assistant that {agent_description}

You can help with:
1. Answering general knowledge questions
2. Setting reminders and tasks
3. Checking weather information
4. Finding news articles
5. Providing simple calculations and conversions

Please respond in a helpful, friendly manner and ask for clarification if needed.
"""

# Memory settings
CHAT_HISTORY_WINDOW_SIZE = 10  # Number of recent messages to keep in working memory
DEFAULT_USER_PREFERENCES = {
  "default_location": "New York",
  "temperature_unit": "celsius",
  "news_topics": ["technology", "science"],
}

# File paths
DATA_DIR = "./data"
LOG_DIR = "./logs"
USER_PREFERENCES_PATH = os.path.join(DATA_DIR, "user_preferences.json")
MEMORY_DB_PATH = os.path.join(DATA_DIR, "memory.sqlite")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Initialize user preferences file if it doesn't exist
def init_user_preferences():
    """Initialize the user preferences file if it doesn't exist."""
    if not os.path.exists(USER_PREFERENCES_PATH):
        with open(USER_PREFERENCES_PATH, 'w') as f:
            json.dump(DEFAULT_USER_PREFERENCES, f, indent=2)

        print(f"Initialized user preferences at {USER_PREFERENCES_PATH}")

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = os.path.join(LOG_DIR, "personal_assistant.log")

# UI settings
UI_THEME = "light"
UI_PORT = 8501  # Default port for Streamlit

# Tool-specific settings
WEATHER_API_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
OPEN_METEO_API_URL = "https://api.open-meteo.com/v1/forecast"
NEWS_API_BASE_URL = "https://newsapi.org/v2/top-headlines"
WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

# Initialize defaults
init_user_preferences()