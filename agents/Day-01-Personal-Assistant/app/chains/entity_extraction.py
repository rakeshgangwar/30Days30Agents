#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Entity Extraction Chain for the Personal Assistant.

This module implements a LangChain chain for extracting entities from user queries
based on the determined intent (weather locations, reminder details, etc.).
"""

import logging
import json
from typing import Dict, Any, List, ClassVar, Optional

from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
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

    # Class variable to store the last topic for context
    last_topic: ClassVar[Optional[str]] = None

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
            llm = ChatOpenAI(
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

            # Add context about the previous topic to the prompt
            prompt_with_context = query
            if intent == "WEB_SEARCH" and EntityExtractionChain.last_topic:
                logger.info(f"Using previous topic for context: {EntityExtractionChain.last_topic}")
                prompt_with_context = f"{query} (Previous topic: {EntityExtractionChain.last_topic})"

            # Use invoke instead of run to avoid recursion
            inputs = {"query": prompt_with_context, "intent": intent}
            result = self.invoke(inputs)

            # Get text output from result
            if isinstance(result, dict) and "text" in result:
                result_text = result["text"]
            else:
                result_text = str(result)

            # Parse the JSON result
            try:
                # Clean up the result text to handle markdown code blocks
                cleaned_text = result_text
                if "```json" in result_text:
                    # Extract JSON from markdown code block
                    cleaned_text = result_text.split("```json")[1].split("```")[0].strip()
                elif "```" in result_text:
                    # Extract from generic code block
                    cleaned_text = result_text.split("```")[1].split("```")[0].strip()

                entities = json.loads(cleaned_text)
                logger.info(f"Extracted entities: {entities}")

                # Update the last topic if this is a GENERAL_QUESTION or WEB_SEARCH
                if intent == "GENERAL_QUESTION":
                    # Handle both flat and nested entity structures
                    if "topic" in entities:
                        EntityExtractionChain.last_topic = entities["topic"]
                        logger.info(f"Updated last topic to: {EntityExtractionChain.last_topic}")
                    elif "GENERAL_QUESTION" in entities and "topic" in entities["GENERAL_QUESTION"]:
                        EntityExtractionChain.last_topic = entities["GENERAL_QUESTION"]["topic"]
                        logger.info(f"Updated last topic to: {EntityExtractionChain.last_topic}")
                    elif "specific_question" in entities:
                        EntityExtractionChain.last_topic = entities["specific_question"]
                        logger.info(f"Updated last topic to: {EntityExtractionChain.last_topic}")
                    elif "GENERAL_QUESTION" in entities and "specific_question" in entities["GENERAL_QUESTION"]:
                        EntityExtractionChain.last_topic = entities["GENERAL_QUESTION"]["specific_question"]
                        logger.info(f"Updated last topic to: {EntityExtractionChain.last_topic}")
                elif intent == "WEB_SEARCH" and "WEB_SEARCH" in entities and entities["WEB_SEARCH"].get("query"):
                    # Extract the main topic from the search query
                    search_query = entities["WEB_SEARCH"]["query"]
                    if search_query and not search_query.startswith("latest information about"):
                        EntityExtractionChain.last_topic = search_query
                        logger.info(f"Updated last topic to: {EntityExtractionChain.last_topic}")

                return entities
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing entity extraction result: {str(e)}")
                logger.error(f"Raw result: {result_text}")
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

    def __call__(self, inputs: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Process inputs through the chain.

        Args:
            inputs (Dict[str, Any]): Input values with query and intent
            **kwargs: Additional keyword arguments like callbacks

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