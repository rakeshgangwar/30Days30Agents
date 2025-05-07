#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Memory management for the Personal Assistant.

This module implements a hierarchical memory system with:
1. Working Memory: Recent conversation turns
2. Short-term Memory: Key information from current session
3. Long-term Memory: Persistent user preferences and important facts
"""

import os
import json
import logging
from typing import Dict, Any, List

from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryMemory
from langchain.llms import OpenAI

from config import (
    OPENAI_API_KEY,
    MODEL_NAME,
    TEMPERATURE,
    CHAT_HISTORY_WINDOW_SIZE,
    USER_PREFERENCES_PATH,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HierarchicalMemory:
    """
    Implementation of a hierarchical memory system with working memory,
    short-term memory, and long-term memory.
    """
    
    def __init__(self, chat_history_window_size=CHAT_HISTORY_WINDOW_SIZE):
        """
        Initialize the hierarchical memory system.
        
        Args:
            chat_history_window_size (int): Number of recent messages to keep in working memory
        """
        # Initialize LLM for summary generation
        self.llm = OpenAI(
            model_name=MODEL_NAME,
            temperature=TEMPERATURE,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Working memory: Last N conversation turns
        self.working_memory = ConversationBufferWindowMemory(
            k=chat_history_window_size,
            memory_key="chat_history",
            return_messages=True
        )
        
        # Short-term memory: Summarized conversation context
        self.short_term_memory = ConversationSummaryMemory(
            llm=self.llm,
            memory_key="conversation_summary"
        )
        
        # Long-term memory: User preferences
        self.user_preferences = UserPreferences()
    
    def add_user_message(self, message: str) -> None:
        """
        Add a user message to the memory.
        
        Args:
            message (str): The user's message
        """
        self.working_memory.chat_memory.add_user_message(message)
        self.short_term_memory.chat_memory.add_user_message(message)
    
    def add_ai_message(self, message: str) -> None:
        """
        Add an AI message to the memory.
        
        Args:
            message (str): The AI's message
        """
        self.working_memory.chat_memory.add_ai_message(message)
        self.short_term_memory.chat_memory.add_ai_message(message)
    
    def get_relevant_context(self, query: str, intent: str = None) -> Dict[str, Any]:
        """
        Get relevant context for a query from all memory layers.
        
        Args:
            query (str): The user's query
            intent (str, optional): The detected intent of the query
            
        Returns:
            Dict[str, Any]: Combined context from all memory layers
        """
        # Get recent conversation from working memory
        recent_context = self.working_memory.load_memory_variables({})
        
        # Get conversation summary from short-term memory
        summary = self.short_term_memory.load_memory_variables({})
        
        # Get user preferences from long-term memory
        user_prefs = self.user_preferences.get_all()
        
        # Combine all context
        return {
            "recent_context": recent_context,
            "conversation_summary": summary,
            "user_preferences": user_prefs
        }


class UserPreferences:
    """
    Manages user preferences for the Personal Assistant.
    
    This includes persistent storage and retrieval of preferences
    such as default location, temperature unit, etc.
    """
    
    def __init__(self, storage_path=USER_PREFERENCES_PATH):
        """
        Initialize the user preferences manager.
        
        Args:
            storage_path (str): Path to the JSON file for storing preferences
        """
        self.storage_path = storage_path
        self.preferences = self._load_preferences()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """
        Load preferences from the JSON file.
        
        Returns:
            Dict[str, Any]: The loaded preferences
        """
        try:
            if not os.path.exists(self.storage_path):
                logger.warning(f"Preferences file not found at {self.storage_path}")
                return {}
                
            with open(self.storage_path, 'r') as f:
                preferences = json.load(f)
                logger.info(f"Loaded preferences from {self.storage_path}")
                return preferences
        except Exception as e:
            logger.error(f"Error loading preferences: {str(e)}")
            return {}
    
    def _save_preferences(self) -> None:
        """Save the current preferences to the JSON file."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.preferences, f, indent=2)
                logger.info(f"Saved preferences to {self.storage_path}")
        except Exception as e:
            logger.error(f"Error saving preferences: {str(e)}")
    
    def get(self, key: str, default=None) -> Any:
        """
        Get a specific preference.
        
        Args:
            key (str): The preference key to get
            default: The default value to return if the key doesn't exist
            
        Returns:
            Any: The preference value or default
        """
        return self.preferences.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a specific preference.
        
        Args:
            key (str): The preference key to set
            value (Any): The preference value
        """
        old_value = self.preferences.get(key)
        self.preferences[key] = value
        
        # Track history of changes
        if "history" not in self.preferences:
            self.preferences["history"] = []
            
        self.preferences["history"].append({
            "key": key,
            "old_value": old_value,
            "new_value": value
        })
        
        self._save_preferences()
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all preferences.
        
        Returns:
            Dict[str, Any]: All preferences
        """
        # Return a copy without the history
        result = self.preferences.copy()
        if "history" in result:
            del result["history"]
        return result