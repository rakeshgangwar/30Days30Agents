"""
Quiz generator for the Learning Coach Agent.
"""

from typing import Dict, Any, List, Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class QuizQuestion(BaseModel):
    """A quiz question."""

    question: str = Field(description="The question text")
    options: List[str] = Field(description="Multiple choice options")
    correct_answer: int = Field(description="Index of the correct answer (0-based)")
    explanation: str = Field(description="Explanation of the correct answer")


class QuizOutput(BaseModel):
    """Output schema for quiz generation."""

    title: str = Field(description="Title of the quiz")
    description: str = Field(description="Description of the quiz")
    topic: str = Field(description="Topic of the quiz")
    difficulty: str = Field(description="Difficulty level (beginner, intermediate, advanced)")
    questions: List[QuizQuestion] = Field(description="List of quiz questions")
    estimated_time_minutes: int = Field(description="Estimated time to complete in minutes")


class QuizGenerator:
    """Generates quizzes for learning topics."""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the quiz generator.

        Args:
            model_name: The name of the LLM model to use
        """
        # Get API key from environment
        import os
        api_key = os.getenv("OPENAI_API_KEY")

        self.llm = ChatOpenAI(model=model_name, temperature=0.2, api_key=api_key)
        self.output_parser = JsonOutputParser(pydantic_object=QuizOutput)

        # Create the prompt template
        template = """
        You are a Learning Coach that creates educational quizzes.

        Create a quiz based on the following information:

        Topic: {topic}
        Difficulty level: {difficulty}
        Number of questions: {num_questions}

        For each question, provide:
        1. The question text
        2. Multiple choice options (4 options)
        3. The index of the correct answer (0-based)
        4. An explanation of why the answer is correct

        Make sure the questions are diverse and cover different aspects of the topic.
        The difficulty should match the specified level.

        {format_instructions}
        """

        self.prompt = PromptTemplate(
            template=template,
            input_variables=["topic", "difficulty", "num_questions"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )

        # Create the chain
        self.chain = self.prompt | self.llm | self.output_parser

    async def generate_quiz(
        self,
        topic: str,
        difficulty: str = "beginner",
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """Generate a quiz.

        Args:
            topic: The topic for the quiz
            difficulty: The difficulty level
            num_questions: Number of questions to generate

        Returns:
            Dict containing the quiz details
        """
        try:
            result = await self.chain.ainvoke({
                "topic": topic,
                "difficulty": difficulty,
                "num_questions": num_questions
            })
            return result
        except Exception as e:
            # Return a simplified quiz if generation fails
            return {
                "title": f"Quiz on {topic}",
                "description": f"A basic quiz to test your knowledge of {topic}",
                "topic": topic,
                "difficulty": difficulty,
                "questions": [
                    {
                        "question": f"What is {topic}?",
                        "options": [
                            f"A fundamental concept in {topic}",
                            f"An advanced technique in {topic}",
                            f"A historical figure related to {topic}",
                            f"None of the above"
                        ],
                        "correct_answer": 0,
                        "explanation": f"This is a basic definition question about {topic}."
                    }
                ],
                "estimated_time_minutes": 5
            }
