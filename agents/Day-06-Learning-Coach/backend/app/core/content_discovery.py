"""
Content discovery for the Learning Coach Agent.
"""

from typing import Dict, Any, List, Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class Resource(BaseModel):
    """A learning resource."""

    title: str = Field(description="Title of the resource")
    url: str = Field(description="URL of the resource")
    type: str = Field(description="Type of resource (article, video, course, book, etc.)")
    description: str = Field(description="Brief description of the resource")
    difficulty: str = Field(description="Difficulty level (beginner, intermediate, advanced)")
    estimated_time: str = Field(description="Estimated time to complete (e.g., '30 minutes', '2 hours')")
    topics: List[str] = Field(description="Topics covered by the resource")
    source: str = Field(description="Source of the resource (e.g., 'Khan Academy', 'Coursera')")


class ResourcesOutput(BaseModel):
    """Output schema for resource discovery."""

    resources: List[Resource] = Field(description="List of discovered resources")
    query: str = Field(description="The query used to discover resources")
    total_count: int = Field(description="Total number of resources found")


class ContentDiscovery:
    """Discovers learning resources."""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        """Initialize the content discovery service.

        Args:
            model_name: The name of the LLM model to use
        """
        # Get API key from environment
        import os
        api_key = os.getenv("OPENAI_API_KEY")

        self.llm = ChatOpenAI(model=model_name, temperature=0.2, api_key=api_key)
        self.output_parser = JsonOutputParser(pydantic_object=ResourcesOutput)

        # Create the prompt template
        template = """
        You are a Learning Coach that discovers educational resources.

        Find relevant learning resources based on the following information:

        Topic: {topic}
        Difficulty level: {difficulty}
        Resource type preference: {resource_type}
        Learning style: {learning_style}

        For each resource, provide:
        1. Title
        2. URL (use realistic URLs for well-known educational platforms)
        3. Type (article, video, course, book, etc.)
        4. Brief description
        5. Difficulty level
        6. Estimated time to complete
        7. Topics covered
        8. Source (e.g., Khan Academy, Coursera, etc.)

        Provide a diverse set of high-quality resources from reputable sources.

        {format_instructions}
        """

        self.prompt = PromptTemplate(
            template=template,
            input_variables=["topic", "difficulty", "resource_type", "learning_style"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )

        # Create the chain
        self.chain = self.prompt | self.llm | self.output_parser

    async def discover_resources(
        self,
        topic: str,
        difficulty: str = "beginner",
        resource_type: str = "any",
        learning_style: str = "visual"
    ) -> Dict[str, Any]:
        """Discover learning resources.

        Args:
            topic: The topic to find resources for
            difficulty: The difficulty level
            resource_type: Preferred resource type
            learning_style: The user's learning style

        Returns:
            Dict containing the discovered resources
        """
        try:
            result = await self.chain.ainvoke({
                "topic": topic,
                "difficulty": difficulty,
                "resource_type": resource_type,
                "learning_style": learning_style
            })
            return result
        except Exception as e:
            # Return a simplified resource list if discovery fails
            return {
                "resources": [
                    {
                        "title": f"Introduction to {topic}",
                        "url": f"https://example.com/{topic.lower().replace(' ', '-')}",
                        "type": "article",
                        "description": f"A beginner-friendly introduction to {topic}",
                        "difficulty": "beginner",
                        "estimated_time": "30 minutes",
                        "topics": [topic],
                        "source": "Example Learning Platform"
                    }
                ],
                "query": topic,
                "total_count": 1
            }
