#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for the intent classification chain of the Personal Assistant.
"""

import unittest
import os
from unittest.mock import patch, MagicMock

from app.chains.intent_classification import IntentClassificationChain

class TestIntentClassificationChain(unittest.TestCase):
    """Test cases for the intent classification chain."""
    
    def setUp(self):
        """Set up test environment."""
        # Set a dummy API key for testing
        os.environ["OPENAI_API_KEY"] = "fake_key_for_testing"
        
        # Create a mock LLM that returns predefined responses
        self.mock_llm = MagicMock()
        self.mock_llm.return_value = "WEATHER"  # Default mock response
    
    @patch('app.chains.intent_classification.OpenAI')
    def test_weather_intent_classification(self, mock_openai):
        """Test classification of weather-related queries."""
        # Configure mock
        mock_openai.return_value = self.mock_llm
        self.mock_llm.return_value = "WEATHER"
        
        # Create chain with mock LLM
        chain = IntentClassificationChain(llm=self.mock_llm)
        
        # Test weather intent recognition
        result = chain.classify_intent("What's the weather like in New York today?")
        self.assertEqual(result, "WEATHER")
        
        # Make sure the LLM was called
        self.mock_llm.assert_called_once()
    
    @patch('app.chains.intent_classification.OpenAI')
    def test_reminder_intent_classification(self, mock_openai):
        """Test classification of reminder-related queries."""
        # Configure mock
        mock_openai.return_value = self.mock_llm
        self.mock_llm.return_value = "REMINDER"
        
        # Create chain with mock LLM
        chain = IntentClassificationChain(llm=self.mock_llm)
        
        # Test reminder intent recognition
        result = chain.classify_intent("Remind me to call my doctor tomorrow at 10 AM")
        self.assertEqual(result, "REMINDER")
    
    @patch('app.chains.intent_classification.OpenAI')
    def test_general_question_intent_classification(self, mock_openai):
        """Test classification of general knowledge queries."""
        # Configure mock
        mock_openai.return_value = self.mock_llm
        self.mock_llm.return_value = "GENERAL_QUESTION"
        
        # Create chain with mock LLM
        chain = IntentClassificationChain(llm=self.mock_llm)
        
        # Test general question intent recognition
        result = chain.classify_intent("How many calories are in an apple?")
        self.assertEqual(result, "GENERAL_QUESTION")
    
    @patch('app.chains.intent_classification.OpenAI')
    def test_news_intent_classification(self, mock_openai):
        """Test classification of news-related queries."""
        # Configure mock
        mock_openai.return_value = self.mock_llm
        self.mock_llm.return_value = "NEWS"
        
        # Create chain with mock LLM
        chain = IntentClassificationChain(llm=self.mock_llm)
        
        # Test news intent recognition
        result = chain.classify_intent("What's the latest news about technology?")
        self.assertEqual(result, "NEWS")
    
    @patch('app.chains.intent_classification.OpenAI')
    def test_invalid_intent_handling(self, mock_openai):
        """Test handling of invalid intent responses."""
        # Configure mock to return an invalid intent
        mock_openai.return_value = self.mock_llm
        self.mock_llm.return_value = "INVALID_INTENT"
        
        # Create chain with mock LLM
        chain = IntentClassificationChain(llm=self.mock_llm)
        
        # Test that invalid intents are converted to UNKNOWN
        result = chain.classify_intent("Something that would cause an invalid response")
        self.assertEqual(result, "UNKNOWN")
    
    @patch('app.chains.intent_classification.OpenAI')
    def test_exception_handling(self, mock_openai):
        """Test handling of exceptions during classification."""
        # Configure mock to raise an exception
        mock_openai.return_value = self.mock_llm
        self.mock_llm.side_effect = Exception("Test exception")
        
        # Create chain with mock LLM
        chain = IntentClassificationChain(llm=self.mock_llm)
        
        # Test that exceptions are handled gracefully
        result = chain.classify_intent("Query that would cause an exception")
        self.assertEqual(result, "UNKNOWN")

if __name__ == "__main__":
    unittest.main()