#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Intent Classification Chain for the Personal Assistant.

This module implements a LangChain chain for classifying user queries
into specific intents (weather, reminder, general question, etc.).
"""

import logging
from typing import Dict, Any, List

from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

import sys
import os
# Add parent directory to path to import from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODEL_NAME, TEMPERATURE, OPENAI_API_KEY
from prompts.base_prompts import intent_classification_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentClassificationChain(LLMChain):
    """Chain for classifying user queries into specific intents."""
    
    def __init__(
        self,
        llm=None,
        prompt=intent_classification_prompt,
        verbose=False
    ):
        """
        Initialize the intent classification chain.
        
        Args:
            llm: The language model to use (default: OpenAI model from config)
            prompt: The prompt template to use (default: intent_classification_prompt)
            verbose: Whether to log detailed output
        """
        if llm is None:
            llm = ChatOpenAI(
                model_name=MODEL_NAME,
                temperature=0.1,  # Lower temperature for more consistent classification
                openai_api_key=OPENAI_API_KEY
            )
        
        super().__init__(llm=llm, prompt=prompt, verbose=verbose)
    
    def classify_intent(self, query: str) -> str:
        """
        Classify the intent of a user query.
        
        Args:
            query (str): The user's query
            
        Returns:
            str: The classified intent
        """
        try:
            logger.info(f"Classifying intent for query: {query}")
            
            # Use invoke instead of run to avoid recursion
            inputs = {"query": query}
            result = self.invoke(inputs)
            
            # Get text output from result
            if isinstance(result, dict) and "text" in result:
                output_text = result["text"]
            else:
                output_text = str(result)
            
            # Clean the result
            intent = output_text.strip().upper()
            
            # Validate intent
            valid_intents = [
                "WEATHER", "REMINDER", "GENERAL_QUESTION", 
                "NEWS", "PREFERENCE", "GREETING", "UNKNOWN"
            ]
            
            if intent not in valid_intents:
                logger.warning(f"Invalid intent returned: {intent}. Using UNKNOWN.")
                intent = "UNKNOWN"
            
            logger.info(f"Classified intent: {intent}")
            return intent
            
        except Exception as e:
            logger.error(f"Error in intent classification: {str(e)}")
            return "UNKNOWN"
    
    def __call__(self, inputs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Process inputs through the chain.
        
        Args:
            inputs (Dict[str, Any]): Input values
            **kwargs: Additional keyword arguments like callbacks
            
        Returns:
            Dict[str, Any]: Output with classified intent
        """
        query = inputs.get("query", "")
        intent = self.classify_intent(query)
        
        return {
            "query": query,
            "intent": intent
        }