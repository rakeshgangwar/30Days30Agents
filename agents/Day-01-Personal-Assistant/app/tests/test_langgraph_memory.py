#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for LangGraph memory implementation.

This script tests the LangGraph memory implementation by simulating
a conversation and verifying that the memory system works correctly.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.append(str(Path(__file__).parent.parent))

from langgraph_memory import LangGraphMemory
from langchain_core.messages import HumanMessage, AIMessage

class TestLangGraphMemory(unittest.TestCase):
    """Test cases for LangGraph memory implementation."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary memory path for testing
        self.test_memory_path = "test_memory.sqlite"

        # Initialize the memory system
        self.memory = LangGraphMemory(memory_path=self.test_memory_path)

        # Test thread ID
        self.thread_id = "test_thread"

    def tearDown(self):
        """Clean up after the test."""
        # Remove the test memory file
        if os.path.exists(self.test_memory_path):
            os.remove(self.test_memory_path)

    def test_add_and_retrieve_messages(self):
        """Test adding and retrieving messages."""
        # Add messages
        self.memory.add_user_message("Hello, my name is Alice.", thread_id=self.thread_id)
        self.memory.add_ai_message("Hello Alice! How can I help you today?", thread_id=self.thread_id)

        # Get messages
        messages = self.memory.get_messages(thread_id=self.thread_id)

        # Check that we have the correct number of messages
        self.assertEqual(len(messages), 2)

        # Check that the messages are of the correct type
        self.assertIsInstance(messages[0], HumanMessage)
        self.assertIsInstance(messages[1], AIMessage)

        # Check that the messages have the correct content
        self.assertEqual(messages[0].content, "Hello, my name is Alice.")
        self.assertEqual(messages[1].content, "Hello Alice! How can I help you today?")

    def test_get_relevant_context(self):
        """Test getting relevant context."""
        # Add messages
        self.memory.add_user_message("Hello, my name is Bob.", thread_id=self.thread_id)
        self.memory.add_ai_message("Hello Bob! How can I help you today?", thread_id=self.thread_id)
        self.memory.add_user_message("What's the weather like?", thread_id=self.thread_id)

        # Get relevant context
        context = self.memory.get_relevant_context("Tell me about the weather", thread_id=self.thread_id)

        # Check that we have the correct context
        self.assertIn("recent_context", context)
        self.assertIn("conversation_summary", context)
        self.assertIn("user_preferences", context)

        # Check that the recent context has the correct messages
        recent_messages = context["recent_context"]["chat_history"]
        self.assertEqual(len(recent_messages), 3)  # All messages should be included

    def test_multiple_threads(self):
        """Test using multiple conversation threads."""
        # Thread 1
        thread_1 = "thread_1"
        self.memory.add_user_message("Hello, I'm thread 1.", thread_id=thread_1)
        self.memory.add_ai_message("Hello thread 1!", thread_id=thread_1)

        # Thread 2
        thread_2 = "thread_2"
        self.memory.add_user_message("Hello, I'm thread 2.", thread_id=thread_2)
        self.memory.add_ai_message("Hello thread 2!", thread_id=thread_2)

        # Get messages from thread 1
        messages_1 = self.memory.get_messages(thread_id=thread_1)
        self.assertEqual(len(messages_1), 2)
        self.assertEqual(messages_1[0].content, "Hello, I'm thread 1.")

        # Get messages from thread 2
        messages_2 = self.memory.get_messages(thread_id=thread_2)
        self.assertEqual(len(messages_2), 2)
        self.assertEqual(messages_2[0].content, "Hello, I'm thread 2.")

    def test_conversation_summary(self):
        """Test that conversation summary is generated."""
        # Add enough messages to trigger a summary
        self.memory.add_user_message("Hello, my name is Charlie.", thread_id=self.thread_id)
        self.memory.add_ai_message("Hello Charlie! How can I help you today?", thread_id=self.thread_id)
        self.memory.add_user_message("I'm looking for information about AI.", thread_id=self.thread_id)
        self.memory.add_ai_message("I'd be happy to tell you about AI. What specifically would you like to know?", thread_id=self.thread_id)

        # Force an update of the summary
        self.memory._update_summary(thread_id=self.thread_id)

        # Check that a summary was generated
        self.assertNotEqual(self.memory.conversation_summary, "")
        self.assertIsInstance(self.memory.conversation_summary, str)

        # The summary should mention AI
        self.assertIn("ai", self.memory.conversation_summary.lower())
        # The summary should contain some content
        self.assertTrue(len(self.memory.conversation_summary) > 10)

if __name__ == "__main__":
    unittest.main()
