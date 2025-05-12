"""
Agent service for the Learning Coach Agent.
"""

from typing import Dict, Any, Optional

from app.core.agent import LearningCoachAgent


class AgentService:
    """Service for interacting with the Learning Coach Agent."""
    
    def __init__(self):
        """Initialize the agent service."""
        self.agent = LearningCoachAgent()
    
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
        
        # Process the input using the agent
        response = await self.agent.process_input(user_input, context)
        
        return response
