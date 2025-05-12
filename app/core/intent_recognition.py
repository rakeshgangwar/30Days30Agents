"""
Intent recognition for the Learning Coach Agent.
"""

from typing import Dict, Any, List, Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


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


class IntentRecognizer:
    """Recognizes user intent from natural language input."""
    
    # Define the possible intents
    INTENTS = [
        "create_learning_path",
        "get_learning_path",
        "update_learning_path",
        "explain_concept",
        "generate_quiz",
        "check_progress",
        "discover_resources",
        "get_recommendations",
        "general_question",
        "greeting",
        "help",
        "feedback"
    ]
    
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        """Initialize the intent recognizer.
        
        Args:
            model_name: The name of the LLM model to use
        """
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.output_parser = JsonOutputParser(pydantic_object=IntentOutput)
        
        # Create the prompt template
        template = """
        You are an intent recognition system for a Learning Coach Agent.
        
        Based on the user's message, identify the most likely intent from the following options:
        {intents}
        
        Also extract any relevant entities that would be useful for fulfilling this intent.
        
        User message: {user_input}
        
        Respond with a JSON object that includes:
        1. The identified intent
        2. A confidence score between 0 and 1
        3. Any extracted entities relevant to the intent
        
        {format_instructions}
        """
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["user_input"],
            partial_variables={
                "intents": ", ".join(self.INTENTS),
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )
        
        # Create the chain
        self.chain = self.prompt | self.llm | self.output_parser
    
    async def recognize_intent(self, user_input: str) -> Dict[str, Any]:
        """Recognize the intent from user input.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Dict containing the recognized intent, confidence, and entities
        """
        try:
            result = await self.chain.ainvoke({"user_input": user_input})
            return result
        except Exception as e:
            # Fallback to general question intent if parsing fails
            return {
                "intent": "general_question",
                "confidence": 0.5,
                "entities": {}
            }
