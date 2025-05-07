#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for the intent classification chain of the Personal Assistant.
"""

import unittest
import os
from unittest.mock import patch, MagicMock

from chains.intent_classification import IntentClassificationChain

class TestIntentClassificationChain(unittest.TestCase):
    """Test cases for the intent classification chain."""

    def setUp(self):
        """Set up test environment."""
        # Set a dummy API key for testing
        os.environ["OPENAI_API_KEY"] = "fake_key_for_testing"

    @patch('langchain.chains.LLMChain.invoke')
    def test_weather_intent_classification(self, mock_invoke):
        """Test classification of weather-related queries."""
        # Configure mock to return a weather intent
        mock_invoke.return_value = {"text": "WEATHER"}

        # Create chain
        chain = IntentClassificationChain()

        # Test weather intent recognition
        result = chain.classify_intent("What's the weather like in New York today?")
        self.assertEqual(result, "WEATHER")

    @patch('langchain.chains.LLMChain.invoke')
    def test_reminder_intent_classification(self, mock_invoke):
        """Test classification of reminder-related queries."""
        # Configure mock to return a reminder intent
        mock_invoke.return_value = {"text": "REMINDER"}

        # Create chain
        chain = IntentClassificationChain()

        # Test reminder intent recognition
        result = chain.classify_intent("Remind me to call my doctor tomorrow at 10 AM")
        self.assertEqual(result, "REMINDER")

    @patch('langchain.chains.LLMChain.invoke')
    def test_general_question_intent_classification(self, mock_invoke):
        """Test classification of general knowledge queries."""
        # Configure mock to return a general question intent
        mock_invoke.return_value = {"text": "GENERAL_QUESTION"}

        # Create chain
        chain = IntentClassificationChain()

        # Test general question intent recognition
        result = chain.classify_intent("How many calories are in an apple?")
        self.assertEqual(result, "GENERAL_QUESTION")

    @patch('langchain.chains.LLMChain.invoke')
    def test_news_intent_classification(self, mock_invoke):
        """Test classification of news-related queries."""
        # Configure mock to return a news intent
        mock_invoke.return_value = {"text": "NEWS"}

        # Create chain
        chain = IntentClassificationChain()

        # Test news intent recognition
        result = chain.classify_intent("What's the latest news about technology?")
        self.assertEqual(result, "NEWS")

    @patch('langchain.chains.LLMChain.invoke')
    def test_invalid_intent_handling(self, mock_invoke):
        """Test handling of invalid intent responses."""
        # Configure mock to return an invalid intent
        mock_invoke.return_value = {"text": "INVALID_INTENT"}

        # Create chain
        chain = IntentClassificationChain()

        # Test that invalid intents are converted to UNKNOWN
        result = chain.classify_intent("Something that would cause an invalid response")
        self.assertEqual(result, "UNKNOWN")

    @patch('langchain.chains.LLMChain.invoke')
    def test_exception_handling(self, mock_invoke):
        """Test handling of exceptions during classification."""
        # Configure mock to raise an exception
        mock_invoke.side_effect = Exception("Test exception")

        # Create chain
        chain = IntentClassificationChain()

        # Test that exceptions are handled gracefully
        result = chain.classify_intent("Query that would cause an exception")
        self.assertEqual(result, "UNKNOWN")

if __name__ == "__main__":
    unittest.main()