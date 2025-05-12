"""
Learning path manager for the Learning Coach Agent.
"""

from typing import Dict, Any, List, Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class LearningPathTopic(BaseModel):
    """A topic in a learning path."""

    title: str = Field(description="Title of the topic")
    description: str = Field(description="Description of the topic")
    estimated_hours: float = Field(description="Estimated hours to complete")
    prerequisites: List[str] = Field(
        description="Prerequisite topics",
        default_factory=list
    )
    resources: List[Dict[str, Any]] = Field(
        description="Learning resources for this topic",
        default_factory=list
    )


class LearningPathOutput(BaseModel):
    """Output schema for learning path creation."""

    title: str = Field(description="Title of the learning path")
    description: str = Field(description="Description of the learning path")
    topics: List[LearningPathTopic] = Field(
        description="Topics in the learning path"
    )
    difficulty: str = Field(
        description="Difficulty level (beginner, intermediate, advanced)"
    )
    estimated_total_hours: float = Field(
        description="Estimated total hours to complete the path"
    )


class LearningPathManager:
    """Creates and manages learning paths."""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the learning path manager.

        Args:
            model_name: The name of the LLM model to use
        """
        # Get API key from environment
        import os
        api_key = os.getenv("OPENAI_API_KEY")

        self.llm = ChatOpenAI(model=model_name, temperature=0.2, api_key=api_key)
        self.output_parser = JsonOutputParser(pydantic_object=LearningPathOutput)

        # Create the prompt template for path creation
        template = """
        You are a Learning Coach that creates personalized learning paths.

        Create a detailed learning path based on the following information:

        Subject: {subject}
        User's goal: {goal}
        User's current knowledge: {current_knowledge}
        User's preferred learning style: {learning_style}
        Time commitment: {time_commitment}

        The learning path should include:
        1. A clear title and description
        2. A logical sequence of topics to learn
        3. For each topic:
           - A descriptive title
           - A brief description
           - Estimated hours to complete
           - Prerequisites (if any)
           - Recommended resources (books, courses, videos, articles)
        4. Overall difficulty level
        5. Total estimated hours to complete

        {format_instructions}
        """

        self.create_path_prompt = PromptTemplate(
            template=template,
            input_variables=[
                "subject",
                "goal",
                "current_knowledge",
                "learning_style",
                "time_commitment"
            ],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )

        # Create the chain
        self.create_path_chain = self.create_path_prompt | self.llm | self.output_parser

    async def create_learning_path(
        self,
        subject: str,
        goal: str,
        current_knowledge: str = "beginner",
        learning_style: str = "visual",
        time_commitment: str = "5 hours per week"
    ) -> Dict[str, Any]:
        """Create a personalized learning path.

        Args:
            subject: The subject to learn
            goal: The user's learning goal
            current_knowledge: The user's current knowledge level
            learning_style: The user's preferred learning style
            time_commitment: The user's time commitment

        Returns:
            Dict containing the learning path details
        """
        try:
            result = await self.create_path_chain.ainvoke({
                "subject": subject,
                "goal": goal,
                "current_knowledge": current_knowledge,
                "learning_style": learning_style,
                "time_commitment": time_commitment
            })
            return result
        except Exception as e:
            # Return a simplified learning path if generation fails
            return {
                "title": f"Learning Path for {subject}",
                "description": f"A basic path to learn {subject} with a focus on {goal}.",
                "topics": [
                    {
                        "title": "Introduction to " + subject,
                        "description": "Basic concepts and fundamentals",
                        "estimated_hours": 2.0,
                        "prerequisites": [],
                        "resources": []
                    }
                ],
                "difficulty": "beginner",
                "estimated_total_hours": 2.0
            }
