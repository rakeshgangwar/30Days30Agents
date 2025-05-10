"""
Service modules for the Writing Assistant API.
"""

import sys
import os

# Add the parent directory to the path so we can import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(current_dir), ".."))
sys.path.insert(0, parent_dir)

from app.services.openrouter_service import openrouter_service
from app.services.preferences_service import preferences_service

__all__ = ["openrouter_service", "preferences_service"]