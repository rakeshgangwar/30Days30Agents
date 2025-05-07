#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LangGraph-based memory implementation for the Personal Assistant.

This module provides memory management using LangGraph's persistence capabilities,
allowing for more sophisticated memory handling with automatic state management.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    trim_messages
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START

from config import (
    OPENAI_API_KEY,
    MODEL_NAME,
    TEMPERATURE,
    CHAT_HISTORY_WINDOW_SIZE,
    USER_PREFERENCES_PATH,
    DATA_DIR,
    MEMORY_DB_PATH
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LangGraphMemory:
    """
    Implementation of memory system using LangGraph's persistence capabilities.

    This class provides:
    1. Working Memory: Recent conversation turns using LangGraph's MessagesState
    2. Short-term Memory: Conversation summaries
    3. Long-term Memory: User preferences stored persistently
    """

    def __init__(
        self,
        chat_history_window_size=CHAT_HISTORY_WINDOW_SIZE,
        memory_path=None
    ):
        """
        Initialize the LangGraph memory system.

        Args:
            chat_history_window_size (int): Number of recent messages to keep in working memory
            memory_path (str, optional): Path to store persistent memory
        """
        from langchain_openai import ChatOpenAI

        # Initialize LLM for summary generation
        self.llm = ChatOpenAI(
            model_name=MODEL_NAME,
            temperature=TEMPERATURE,
            openai_api_key=OPENAI_API_KEY
        )

        # Working memory: stores all messages
        self.messages = {}

        # Working memory window size
        self.chat_history_window_size = chat_history_window_size

        # Short-term memory: conversation summary
        self.conversation_summary = ""

        # Long-term memory: User preferences
        self.user_preferences = UserPreferences()

    def _format_messages_for_summary(self, messages) -> str:
        """Format messages for the summary prompt."""
        formatted = []
        for msg in messages:
            prefix = "User" if isinstance(msg, HumanMessage) else "Assistant"
            formatted.append(f"{prefix}: {msg.content}")
        return "\n".join(formatted)

    def add_user_message(self, message: str, thread_id: str = "default") -> None:
        """
        Add a user message to the memory.

        Args:
            message (str): The user's message
            thread_id (str): The thread ID for the conversation
        """
        # Initialize thread if it doesn't exist
        if thread_id not in self.messages:
            self.messages[thread_id] = []

        # Add the message to the thread
        self.messages[thread_id].append(HumanMessage(content=message))

        # Update the summary
        self._update_summary(thread_id)

    def add_ai_message(self, message: str, thread_id: str = "default") -> None:
        """
        Add an AI message to the memory.

        Args:
            message (str): The AI's message
            thread_id (str): The thread ID for the conversation
        """
        # Initialize thread if it doesn't exist
        if thread_id not in self.messages:
            self.messages[thread_id] = []

        # Add the message to the thread
        self.messages[thread_id].append(AIMessage(content=message))

        # Update the summary
        self._update_summary(thread_id)

    def _update_summary(self, thread_id: str = "default") -> None:
        """
        Update the conversation summary.

        Args:
            thread_id (str): The thread ID for the conversation
        """
        # Get the current state
        current_messages = self.get_messages(thread_id)

        # Only update summary when we have at least 2 messages (a complete exchange)
        if len(current_messages) >= 2:
            # Create a prompt for summarization
            summary_prompt = [
                SystemMessage(content="Summarize the following conversation concisely, focusing on key information."),
                HumanMessage(content=f"Here's the conversation so far: {self._format_messages_for_summary(current_messages)}")
            ]

            # Generate summary
            self.conversation_summary = self.llm.invoke(summary_prompt).content

    def get_messages(self, thread_id: str = "default") -> List:
        """
        Get all messages for a thread.

        Args:
            thread_id (str): The thread ID for the conversation

        Returns:
            List: The messages in the thread
        """
        # Return the messages for the thread
        return self.messages.get(thread_id, [])

    def add(self, key: str, value: Any) -> None:
        """
        Add a key-value pair to memory.

        Args:
            key (str): The key to store
            value (Any): The value to store
        """
        # For user_name, extract from message content
        if key == "user_name" and isinstance(value, str) and "my name is" in value.lower():
            # Extract name from message like "My name is John Smith"
            parts = value.lower().split("my name is")
            if len(parts) > 1:
                name = parts[1].strip()
                self.user_preferences.set(key, name)
            else:
                self.user_preferences.set(key, value)
        else:
            # Store in user preferences
            self.user_preferences.set(key, value)

    def get(self, key: str, default=None) -> Any:
        """
        Get a value from memory.

        Args:
            key (str): The key to retrieve
            default: The default value to return if key doesn't exist

        Returns:
            Any: The stored value or default
        """
        # Check user preferences first
        value = self.user_preferences.get(key, default)

        # If not found and it's user_name, try to extract from messages
        if value is None and key == "user_name":
            # Try to find name in messages
            for thread_id, messages in self.messages.items():
                for msg in messages:
                    if isinstance(msg, HumanMessage) and "my name is" in msg.content.lower():
                        parts = msg.content.lower().split("my name is")
                        if len(parts) > 1:
                            # Extract the full name after "my name is"
                            name_text = parts[1].strip()

                            # Capitalize each word in the name
                            name_parts = name_text.split()
                            if name_parts:
                                name = " ".join(part.capitalize() for part in name_parts)
                                # Store for future use
                                self.user_preferences.set(key, name)
                                return name

        return value

    def remove(self, key: str) -> None:
        """
        Remove a key from memory.

        Args:
            key (str): The key to remove
        """
        if key in self.user_preferences.preferences:
            del self.user_preferences.preferences[key]
            self.user_preferences._save_preferences()

    def get_all(self, key: str) -> List[Any]:
        """
        Get all values for a key (for keys that can have multiple values).

        Args:
            key (str): The key to retrieve all values for

        Returns:
            List[Any]: All values for the key
        """
        # For conversation, return all message pairs
        if key == "conversation":
            result = []
            for thread_id, messages in self.messages.items():
                # Group messages into pairs
                i = 0
                while i < len(messages) - 1:
                    if isinstance(messages[i], HumanMessage) and isinstance(messages[i+1], AIMessage):
                        result.append({
                            "query": messages[i].content,
                            "response": messages[i+1].content
                        })
                    i += 2
            return result

        # Default: return as list
        value = self.get(key)
        return [value] if value is not None else []

    def serialize(self) -> str:
        """
        Serialize the memory to a string.

        Returns:
            str: Serialized memory
        """
        # Create a dictionary with all memory components
        memory_dict = {
            "messages": {
                thread_id: [
                    {"type": "human" if isinstance(msg, HumanMessage) else "ai",
                     "content": msg.content}
                    for msg in msgs
                ]
                for thread_id, msgs in self.messages.items()
            },
            "conversation_summary": self.conversation_summary,
            "user_preferences": self.user_preferences.get_all()
        }

        # Serialize to JSON
        return json.dumps(memory_dict)

    def deserialize(self, serialized: str) -> None:
        """
        Deserialize memory from a string.

        Args:
            serialized (str): Serialized memory
        """
        try:
            memory_dict = json.loads(serialized)

            # Restore messages
            self.messages = {}
            for thread_id, msgs in memory_dict.get("messages", {}).items():
                self.messages[thread_id] = []
                for msg in msgs:
                    if msg["type"] == "human":
                        self.messages[thread_id].append(HumanMessage(content=msg["content"]))
                    else:
                        self.messages[thread_id].append(AIMessage(content=msg["content"]))

            # Restore conversation summary
            self.conversation_summary = memory_dict.get("conversation_summary", "")

            # Restore user preferences
            for key, value in memory_dict.get("user_preferences", {}).items():
                self.user_preferences.set(key, value)

        except Exception as e:
            logger.error(f"Error deserializing memory: {str(e)}")

    def get_relevant_context(self, query: str, thread_id: str = "default", intent: str = None) -> Dict[str, Any]:
        """
        Get relevant context for a query from all memory layers.

        Args:
            query (str): The user's query
            thread_id (str): The thread ID for the conversation
            intent (str, optional): The detected intent of the query

        Returns:
            Dict[str, Any]: Combined context from all memory layers
        """
        # Get all messages for the thread
        all_messages = self.get_messages(thread_id)

        # Get recent conversation from working memory (trimmed to window size)
        recent_messages = trim_messages(
            all_messages,
            token_counter=len,  # Simple count of messages
            max_tokens=self.chat_history_window_size,
            strategy="last",
            start_on="human",
            include_system=True
        )

        # Get user preferences from long-term memory
        user_prefs = self.user_preferences.get_all()

        # Combine all context
        return {
            "recent_context": {"chat_history": recent_messages},
            "conversation_summary": {"conversation_summary": self.conversation_summary},
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
