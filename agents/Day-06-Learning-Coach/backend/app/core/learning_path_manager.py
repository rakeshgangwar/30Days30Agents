"""
Learning path manager for the Learning Coach Agent.

This module provides functionality for creating and managing personalized learning paths
based on user preferences, goals, and learning styles.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, field_validator


logger = logging.getLogger(__name__)


class Resource(BaseModel):
    """A learning resource within a topic."""

    title: str = Field(description="Title of the resource")
    url: str = Field(description="URL of the resource")
    type: str = Field(description="Type of resource (article, video, course, book, etc.)")
    description: str = Field(description="Brief description of the resource")
    estimated_time: str = Field(description="Estimated time to complete (e.g., '30 minutes', '2 hours')")
    difficulty: str = Field(description="Difficulty level (beginner, intermediate, advanced)")
    free: bool = Field(description="Whether the resource is free or paid", default=True)


class LearningPathTopic(BaseModel):
    """A topic in a learning path."""

    title: str = Field(description="Title of the topic")
    description: str = Field(description="Description of the topic")
    estimated_hours: float = Field(description="Estimated hours to complete")
    key_concepts: List[str] = Field(
        description="Key concepts covered in this topic",
        default_factory=list
    )
    prerequisites: List[str] = Field(
        description="Prerequisite topics",
        default_factory=list
    )
    resources: List[Resource] = Field(
        description="Learning resources for this topic",
        default_factory=list
    )
    exercises: List[str] = Field(
        description="Suggested exercises or practice activities",
        default_factory=list
    )

    @field_validator('estimated_hours')
    @classmethod
    def validate_hours(cls, v: float) -> float:
        """Validate that estimated hours is positive."""
        if v <= 0:
            raise ValueError("Estimated hours must be positive")
        return v


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
    learning_outcomes: List[str] = Field(
        description="Expected learning outcomes upon completion",
        default_factory=list
    )
    prerequisites: List[str] = Field(
        description="Prerequisites for the entire learning path",
        default_factory=list
    )

    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        """Validate difficulty level."""
        valid_levels = ["beginner", "intermediate", "advanced"]
        if v.lower() not in valid_levels:
            raise ValueError(f"Difficulty must be one of: {', '.join(valid_levels)}")
        return v.lower()

    @field_validator('estimated_total_hours')
    @classmethod
    def validate_total_hours(cls, v: float) -> float:
        """Validate that total hours is positive."""
        if v <= 0:
            raise ValueError("Estimated total hours must be positive")
        return v


class LearningPathManager:
    """Creates and manages personalized learning paths.

    This class provides functionality to create, retrieve, update, and manage
    learning paths based on user preferences and goals.
    """

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

        # In-memory storage for learning paths (would be replaced with database in production)
        self.learning_paths = {}

        # Create the prompt template for path creation
        template = """
        You are a Learning Coach that creates personalized learning paths.

        Create a detailed learning path based on the following information:

        Subject: {subject}
        User's goal: {goal}
        User's current knowledge: {current_knowledge}
        User's preferred learning style: {learning_style}
        Time commitment: {time_commitment}
        Additional requirements: {additional_requirements}

        The learning path should include:
        1. A clear title and description
        2. A logical sequence of topics to learn, organized from foundational to advanced
        3. For each topic:
           - A descriptive title
           - A brief description
           - Key concepts covered
           - Estimated hours to complete
           - Prerequisites (if any)
           - Recommended resources (books, courses, videos, articles)
           - Suggested exercises or practice activities
        4. Overall difficulty level
        5. Total estimated hours to complete
        6. Expected learning outcomes
        7. Prerequisites for the entire learning path

        Ensure the learning path is:
        - Tailored to the user's current knowledge level
        - Aligned with their learning style preferences
        - Realistic given their time commitment
        - Focused on their specific goals
        - Structured with clear progression between topics

        For resources, include a mix of:
        - Free and paid options
        - Different formats (videos, articles, interactive exercises)
        - Varying difficulty levels
        - Reputable sources

        {format_instructions}
        """

        self.create_path_prompt = PromptTemplate(
            template=template,
            input_variables=[
                "subject",
                "goal",
                "current_knowledge",
                "learning_style",
                "time_commitment",
                "additional_requirements"
            ],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )

        # Create the chain
        self.create_path_chain = self.create_path_prompt | self.llm | self.output_parser

        # Create the prompt template for path updating
        update_template = """
        You are a Learning Coach that updates personalized learning paths.

        You need to update an existing learning path based on the following information:

        Current learning path: {current_path}

        Update requirements: {update_requirements}

        User's current knowledge: {current_knowledge}
        User's preferred learning style: {learning_style}
        Time commitment: {time_commitment}

        Make the requested changes while preserving the overall structure and quality of the learning path.
        Ensure the updated path remains coherent and logical in its progression.

        {format_instructions}
        """

        self.update_path_prompt = PromptTemplate(
            template=update_template,
            input_variables=[
                "current_path",
                "update_requirements",
                "current_knowledge",
                "learning_style",
                "time_commitment"
            ],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )

        # Create the update chain
        self.update_path_chain = self.update_path_prompt | self.llm | self.output_parser

        logger.info(f"Learning path manager initialized with model: {model_name}")

    async def create_learning_path(
        self,
        subject: str,
        goal: str,
        current_knowledge: str = "beginner",
        learning_style: str = "visual",
        time_commitment: str = "5 hours per week",
        additional_requirements: str = "",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a personalized learning path.

        Args:
            subject: The subject to learn
            goal: The user's learning goal
            current_knowledge: The user's current knowledge level
            learning_style: The user's preferred learning style
            time_commitment: The user's time commitment
            additional_requirements: Any additional requirements or preferences
            user_id: Optional user ID to associate with the learning path

        Returns:
            Dict containing the learning path details
        """
        logger.info(f"Creating learning path for subject: {subject}")

        try:
            result = await self.create_path_chain.ainvoke({
                "subject": subject,
                "goal": goal,
                "current_knowledge": current_knowledge,
                "learning_style": learning_style,
                "time_commitment": time_commitment,
                "additional_requirements": additional_requirements
            })

            # Generate a unique ID for the learning path
            path_id = str(uuid.uuid4())

            # Add metadata
            result["id"] = path_id
            result["created_at"] = datetime.utcnow().isoformat()
            result["updated_at"] = datetime.utcnow().isoformat()
            result["subject"] = subject
            result["user_id"] = user_id
            result["progress"] = {
                "completed_topics": 0,
                "total_topics": len(result["topics"]),
                "percentage": 0
            }

            # Store the learning path
            self.learning_paths[path_id] = result

            logger.info(f"Created learning path with ID: {path_id}")
            return result
        except Exception as e:
            logger.error(f"Error creating learning path: {str(e)}")
            # Return a simplified learning path if generation fails
            fallback_path = {
                "title": f"Learning Path for {subject}",
                "description": f"A basic path to learn {subject} with a focus on {goal}.",
                "topics": [
                    {
                        "title": "Introduction to " + subject,
                        "description": "Basic concepts and fundamentals",
                        "estimated_hours": 2.0,
                        "prerequisites": [],
                        "resources": [],
                        "key_concepts": ["Basic concepts"],
                        "exercises": ["Practice the basics"]
                    }
                ],
                "difficulty": "beginner",
                "estimated_total_hours": 2.0,
                "learning_outcomes": [f"Basic understanding of {subject}"],
                "prerequisites": []
            }

            # Generate a unique ID for the fallback path
            path_id = str(uuid.uuid4())

            # Add metadata
            fallback_path["id"] = path_id
            fallback_path["created_at"] = datetime.utcnow().isoformat()
            fallback_path["updated_at"] = datetime.utcnow().isoformat()
            fallback_path["subject"] = subject
            fallback_path["user_id"] = user_id
            fallback_path["progress"] = {
                "completed_topics": 0,
                "total_topics": 1,
                "percentage": 0
            }

            # Store the fallback path
            self.learning_paths[path_id] = fallback_path

            logger.info(f"Created fallback learning path with ID: {path_id}")
            return fallback_path

    async def update_learning_path(
        self,
        path_id: str,
        update_requirements: str,
        current_knowledge: str = "beginner",
        learning_style: str = "visual",
        time_commitment: str = "5 hours per week"
    ) -> Dict[str, Any]:
        """Update an existing learning path.

        Args:
            path_id: The ID of the learning path to update
            update_requirements: Description of the updates to make
            current_knowledge: The user's current knowledge level
            learning_style: The user's preferred learning style
            time_commitment: The user's time commitment

        Returns:
            Dict containing the updated learning path details
        """
        logger.info(f"Updating learning path with ID: {path_id}")

        # Check if the learning path exists
        if path_id not in self.learning_paths:
            logger.error(f"Learning path with ID {path_id} not found")
            raise ValueError(f"Learning path with ID {path_id} not found")

        current_path = self.learning_paths[path_id]

        try:
            result = await self.update_path_chain.ainvoke({
                "current_path": current_path,
                "update_requirements": update_requirements,
                "current_knowledge": current_knowledge,
                "learning_style": learning_style,
                "time_commitment": time_commitment
            })

            # Preserve metadata
            result["id"] = path_id
            result["created_at"] = current_path["created_at"]
            result["updated_at"] = datetime.utcnow().isoformat()
            result["subject"] = current_path.get("subject", "")
            result["user_id"] = current_path.get("user_id")

            # Update progress information
            result["progress"] = {
                "completed_topics": current_path.get("progress", {}).get("completed_topics", 0),
                "total_topics": len(result["topics"]),
                "percentage": (current_path.get("progress", {}).get("completed_topics", 0) / len(result["topics"])) * 100 if len(result["topics"]) > 0 else 0
            }

            # Update the stored learning path
            self.learning_paths[path_id] = result

            logger.info(f"Updated learning path with ID: {path_id}")
            return result
        except Exception as e:
            logger.error(f"Error updating learning path: {str(e)}")
            # Return the original learning path if update fails
            return current_path

    def get_learning_path(self, path_id: str) -> Dict[str, Any]:
        """Get a learning path by ID.

        Args:
            path_id: The ID of the learning path to retrieve

        Returns:
            Dict containing the learning path details
        """
        logger.info(f"Retrieving learning path with ID: {path_id}")

        if path_id not in self.learning_paths:
            logger.error(f"Learning path with ID {path_id} not found")
            raise ValueError(f"Learning path with ID {path_id} not found")

        return self.learning_paths[path_id]

    def get_all_learning_paths(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all learning paths, optionally filtered by user ID.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of learning paths
        """
        if user_id:
            logger.info(f"Retrieving all learning paths for user: {user_id}")
            return [path for path in self.learning_paths.values() if path.get("user_id") == user_id]
        else:
            logger.info("Retrieving all learning paths")
            return list(self.learning_paths.values())

    def update_progress(self, path_id: str, completed_topics: int) -> Dict[str, Any]:
        """Update the progress of a learning path.

        Args:
            path_id: The ID of the learning path to update
            completed_topics: The number of completed topics

        Returns:
            Dict containing the updated progress information
        """
        logger.info(f"Updating progress for learning path with ID: {path_id}")

        if path_id not in self.learning_paths:
            logger.error(f"Learning path with ID {path_id} not found")
            raise ValueError(f"Learning path with ID {path_id} not found")

        path = self.learning_paths[path_id]
        total_topics = len(path["topics"])

        if completed_topics > total_topics:
            completed_topics = total_topics

        percentage = (completed_topics / total_topics) * 100 if total_topics > 0 else 0

        progress = {
            "completed_topics": completed_topics,
            "total_topics": total_topics,
            "percentage": percentage
        }

        path["progress"] = progress
        path["updated_at"] = datetime.utcnow().isoformat()

        logger.info(f"Updated progress for learning path with ID: {path_id}")
        return progress
