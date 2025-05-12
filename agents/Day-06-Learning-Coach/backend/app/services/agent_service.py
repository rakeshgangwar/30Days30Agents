"""
Agent service for the Learning Coach Agent.
"""

import logging
import os
from typing import Dict, Any, Optional

from app.core.agent import LearningCoachAgent


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentService:
    """Service for interacting with the Learning Coach Agent."""

    def __init__(self, model_name: str = None):
        """Initialize the agent service.

        Args:
            model_name: Optional model name to use for the agent
        """
        # Use environment variable for model if not provided
        if model_name is None:
            model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # Make sure OpenAI API key is set in the environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_mock = False

        if not openai_api_key:
            logger.warning("OPENAI_API_KEY environment variable is not set!")
            logger.warning("Using mock implementation for development")
            self.use_mock = True
        else:
            logger.info(f"OPENAI_API_KEY is set (length: {len(openai_api_key)})")
            # Set the API key in the environment explicitly
            os.environ["OPENAI_API_KEY"] = openai_api_key

        logger.info(f"Initializing Learning Coach Agent with model: {model_name}")

        if not self.use_mock:
            self.agent = LearningCoachAgent(model_name=model_name)
        else:
            # No agent initialization needed for mock implementation
            logger.info("Using mock implementation")

    async def process_user_input(
        self, user_input: str, user_id: Optional[int] = None, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process user input and generate a response.

        Args:
            user_input: The user's input text
            user_id: Optional user ID for personalized responses
            context: Optional context information

        Returns:
            Dict containing the agent's response and any additional information
        """
        # Initialize context if not provided
        if context is None:
            context = {}

        # Add user ID to context if provided
        if user_id is not None:
            context["user_id"] = user_id

        # Log the incoming request
        logger.info(f"Processing user input: {user_input[:50]}..." if len(user_input) > 50 else f"Processing user input: {user_input}")

        # If using mock implementation, return mock responses
        if self.use_mock:
            logger.info("Using mock implementation to generate response")

            # Generate a mock response based on the input
            if "learning path" in user_input.lower():
                response_text = f"I'd be happy to create a learning path for {user_input}. This is a mock response since no OpenAI API key is configured."
            elif "quiz" in user_input.lower():
                response_text = f"Here's a quiz about {user_input}. This is a mock response since no OpenAI API key is configured."
            elif "resources" in user_input.lower() or "recommend" in user_input.lower():
                response_text = f"I found some resources about {user_input}. This is a mock response since no OpenAI API key is configured."
            else:
                response_text = f"I received your message about {user_input}. This is a mock response since no OpenAI API key is configured."

            # Determine response type based on the input
            if "learning path" in user_input.lower():
                response_type = "learning_path"
            elif "quiz" in user_input.lower():
                response_type = "quiz"
            elif "resources" in user_input.lower() or "recommend" in user_input.lower():
                response_type = "resources"
            else:
                response_type = "general"

            mock_response = {
                "response": response_text,
                "response_type": response_type,
                "context": context
            }

            logger.info(f"Generated mock response: {mock_response['response'][:50]}..." if len(mock_response['response']) > 50 else f"Generated mock response: {mock_response['response']}")

            return mock_response

        # If not using mock, use the real agent
        try:
            # Process the input using the agent
            response = await self.agent.process_input(user_input, context)

            # Log successful response
            logger.info(f"Generated response: {response['response'][:50]}..." if len(response['response']) > 50 else f"Generated response: {response['response']}")

            return response
        except Exception as e:
            # Log error
            logger.error(f"Error processing user input: {str(e)}")

            # Return a fallback response
            return {
                "response": "I'm sorry, I encountered an error while processing your request. Please try again with a different query.",
                "response_type": "error",
                "context": context
            }
