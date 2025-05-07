#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Entity Extraction Chain for the Personal Assistant.

This module implements a LangChain chain for extracting entities from user queries
based on the determined intent (weather locations, reminder details, etc.).
"""

import logging
import json
from typing import Dict, Any, List

from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

import sys
import os
# Add parent directory to path to import from sibling directories
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import MODEL_NAME, TEMPERATURE, OPENAI_API_KEY
from prompts.base_prompts import entity_extraction_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EntityExtractionChain(LLMChain):
    """Chain for extracting entities from user queries based on intent."""
    
    def __init__(
        self,
        llm=None,
        prompt=entity_extraction_prompt,
        verbose=False
    ):
        """
        Initialize the entity extraction chain.
        
        Args:
            llm: The language model to use (default: OpenAI model from config)
            prompt: The prompt template to use (default: entity_extraction_prompt)
            verbose: Whether to log detailed output
        """
        if llm is None:
            llm = OpenAI(
                model_name=MODEL_NAME,
                temperature=0.1,  # Lower temperature for more consistent extraction
                openai_api_key=OPENAI_API_KEY
            )
        
        super().__init__(llm=llm, prompt=prompt, verbose=verbose)
    
    def extract_entities(self, query: str, intent: str) -> Dict[str, Any]:
        """
        Extract entities from a user query based on intent.
        
        Args:
            query (str): The user's query
            intent (str): The classified intent
            
        Returns:
            Dict[str, Any]: Extracted entities
        """
        try:
            logger.info(f"Extracting entities for query: {query}, intent: {intent}")
            
            # Run the chain
            result = self.run(query=query, intent=intent)
            
            # Parse the JSON result
            try:
                entities = json.loads(result)
                logger.info(f"Extracted entities: {entities}")
                return entities
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing entity extraction result: {str(e)}")
                logger.error(f"Raw result: {result}")
                # Return empty entities dictionary
                return self._get_default_entities(intent)
            
        except Exception as e:
            logger.error(f"Error in entity extraction: {str(e)}")
            return self._get_default_entities(intent)
    
    def _get_default_entities(self, intent: str) -> Dict[str, Any]:
        """
        Get default entity structure based on intent.
        
        Args:
            intent (str): The classified intent
            
        Returns:
            Dict[str, Any]: Default entity structure
        """
        if intent == "WEATHER":
            return {
                "location": None,
                "date": None,
                "specific_info": None
            }
        elif intent == "REMINDER":
            return {
                "task": None,
                "time": None,
                "date": None,
                "priority": None
            }
        elif intent == "GENERAL_QUESTION":
            return {
                "topic": None,
                "specific_question": None
            }
        elif intent == "NEWS":
            return {
                "topic": None,
                "source": None,
                "timeframe": None
            }
        elif intent == "PREFERENCE":
            return {
                "setting": None,
                "value": None
            }
        else:
            return {}
    
    def __call__(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process inputs through the chain.
        
        Args:
            inputs (Dict[str, Any]): Input values with query and intent
            
        Returns:
            Dict[str, Any]: Output with extracted entities
        """
        query = inputs.get("query", "")
        intent = inputs.get("intent", "UNKNOWN")
        
        entities = self.extract_entities(query, intent)
        
        return {
            "query": query,
            "intent": intent,
            "entities": entities
        }