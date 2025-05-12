"""
Intent recognition for the Learning Coach Agent.

This module provides intent recognition capabilities for the Learning Coach Agent,
allowing it to understand user queries and extract relevant entities.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, field_validator


logger = logging.getLogger(__name__)


class IntentOutput(BaseModel):
    """Output schema for intent recognition."""

    intent: str = Field(
        description="The identified intent of the user's message"
    )
    confidence: float = Field(
        description="Confidence score between 0 and 1"
    )
    entities: Dict[str, Any] = Field(
        description="Extracted entities relevant to the intent",
        default_factory=dict
    )

    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """Validate that confidence is between 0 and 1."""
        if v < 0 or v > 1:
            raise ValueError("Confidence score must be between 0 and 1")
        return v


class IntentRecognizer:
    """Recognizes user intent from natural language input.

    This class uses a language model to identify the user's intent from their
    natural language input and extract relevant entities.
    """

    # Define the possible intents with descriptions
    INTENT_DESCRIPTIONS = {
        "create_learning_path": "Create a new learning path for a subject",
        "get_learning_path": "Retrieve an existing learning path",
        "update_learning_path": "Modify an existing learning path",
        "explain_concept": "Explain a concept or topic",
        "generate_quiz": "Create a quiz on a specific topic",
        "check_progress": "Check learning progress on a path or topic",
        "discover_resources": "Find learning resources on a topic",
        "get_recommendations": "Get personalized learning recommendations",
        "general_question": "Answer a general question not covered by other intents",
        "greeting": "Respond to a greeting or introduction",
        "help": "Provide help about the Learning Coach capabilities",
        "feedback": "Process feedback about the Learning Coach",
        "set_preferences": "Set or update user learning preferences",
        "summarize_topic": "Provide a summary of a topic or concept"
    }

    # Entity types that can be extracted
    ENTITY_TYPES = {
        "subject": "The main subject or topic (e.g., 'Python', 'Machine Learning')",
        "topic": "A specific topic within a subject",
        "difficulty": "Difficulty level (beginner, intermediate, advanced)",
        "goal": "The user's learning goal or objective",
        "current_knowledge": "The user's current knowledge level",
        "learning_style": "The user's preferred learning style (visual, auditory, reading, kinesthetic)",
        "time_commitment": "How much time the user can commit to learning",
        "resource_type": "Type of resource (article, video, course, book, etc.)",
        "num_questions": "Number of questions for a quiz",
        "path_id": "Identifier for a specific learning path",
        "user_preferences": "User preferences for learning"
    }

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the intent recognizer.

        Args:
            model_name: The name of the LLM model to use
        """
        # Get API key from environment
        import os
        api_key = os.getenv("OPENAI_API_KEY")

        self.llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key)
        self.output_parser = JsonOutputParser(pydantic_object=IntentOutput)

        # Create the prompt template with enhanced instructions
        template = """
        You are an intent recognition system for a Learning Coach Agent that helps users learn new subjects and skills.

        Based on the user's message, identify the most likely intent from the following options:
        {intent_descriptions}

        Also extract any relevant entities that would be useful for fulfilling this intent.
        Possible entity types include:
        {entity_types}

        User message: {user_input}

        Context (if available): {context}

        Respond with a JSON object that includes:
        1. The identified intent (must be one of the listed intents)
        2. A confidence score between 0 and 1
        3. Any extracted entities relevant to the intent

        Examples of entity extraction:
        - For "I want to learn Python programming": subject="Python programming"
        - For "Create a quiz about machine learning with 10 questions": topic="machine learning", num_questions=10
        - For "I'm a beginner in data science and want to become proficient": subject="data science", current_knowledge="beginner", goal="become proficient"
        - For "I prefer video tutorials and can study 3 hours per week": learning_style="visual", time_commitment="3 hours per week"

        {format_instructions}
        """

        self.prompt = PromptTemplate(
            template=template,
            input_variables=["user_input", "context"],
            partial_variables={
                "intent_descriptions": "\n".join([f"- {intent}: {description}" for intent, description in self.INTENT_DESCRIPTIONS.items()]),
                "entity_types": "\n".join([f"- {entity_type}: {description}" for entity_type, description in self.ENTITY_TYPES.items()]),
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )

        # Create the chain
        self.chain = self.prompt | self.llm | self.output_parser

        logger.info(f"Intent recognizer initialized with model: {model_name}")

    async def recognize_intent(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Recognize the intent from user input.

        Args:
            user_input: The user's input text
            context: Optional context information to help with intent recognition

        Returns:
            Dict containing the recognized intent, confidence, and entities
        """
        if context is None:
            context = {}

        logger.info(f"Recognizing intent for: {user_input[:50]}..." if len(user_input) > 50 else f"Recognizing intent for: {user_input}")

        try:
            result = await self.chain.ainvoke({
                "user_input": user_input,
                "context": str(context)
            })

            # Validate the intent
            if result["intent"] not in self.INTENT_DESCRIPTIONS:
                logger.warning(f"Invalid intent detected: {result['intent']}. Falling back to general_question.")
                result["intent"] = "general_question"
                result["confidence"] = 0.5

            logger.info(f"Recognized intent: {result['intent']} with confidence: {result['confidence']}")
            return result
        except Exception as e:
            logger.error(f"Error recognizing intent: {str(e)}")
            # Fallback to general question intent if parsing fails
            return {
                "intent": "general_question",
                "confidence": 0.5,
                "entities": {}
            }

    def get_intent_description(self, intent: str) -> str:
        """Get the description for a specific intent.

        Args:
            intent: The intent to get the description for

        Returns:
            The description of the intent
        """
        return self.INTENT_DESCRIPTIONS.get(intent, "Unknown intent")

    def get_all_intents(self) -> List[str]:
        """Get all available intents.

        Returns:
            List of all available intents
        """
        return list(self.INTENT_DESCRIPTIONS.keys())
