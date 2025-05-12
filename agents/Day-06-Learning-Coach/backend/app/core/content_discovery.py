"""
Content discovery for the Learning Coach Agent.

This module provides functionality for discovering and recommending learning resources
based on user preferences, learning styles, and topics of interest.
"""

import logging
import json
from typing import Dict, Any, List, Optional, Tuple, Set

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, field_validator


logger = logging.getLogger(__name__)


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
    free: bool = Field(description="Whether the resource is free or paid", default=True)
    interactive: bool = Field(description="Whether the resource is interactive", default=False)
    language: str = Field(description="Language of the resource", default="English")

    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        """Validate difficulty level."""
        valid_levels = ["beginner", "intermediate", "advanced"]
        if v.lower() not in valid_levels:
            raise ValueError(f"Difficulty must be one of: {', '.join(valid_levels)}")
        return v.lower()


class ResourcesOutput(BaseModel):
    """Output schema for resource discovery."""

    resources: List[Resource] = Field(description="List of discovered resources")
    query: str = Field(description="The query used to discover resources")
    total_count: int = Field(description="Total number of resources found")
    recommended_sequence: List[str] = Field(
        description="Recommended sequence of resource titles for optimal learning",
        default_factory=list
    )


class ContentDiscovery:
    """Discovers and recommends learning resources.

    This class provides functionality to discover, filter, and recommend learning
    resources based on user preferences and learning styles.
    """

    # Define common educational platforms with their domains
    EDUCATIONAL_PLATFORMS = {
        "Khan Academy": "khanacademy.org",
        "Coursera": "coursera.org",
        "edX": "edx.org",
        "Udemy": "udemy.com",
        "Udacity": "udacity.com",
        "FreeCodeCamp": "freecodecamp.org",
        "MIT OpenCourseWare": "ocw.mit.edu",
        "YouTube": "youtube.com",
        "Codecademy": "codecademy.com",
        "W3Schools": "w3schools.com",
        "MDN Web Docs": "developer.mozilla.org",
        "Brilliant": "brilliant.org",
        "DataCamp": "datacamp.com",
        "Pluralsight": "pluralsight.com",
        "LinkedIn Learning": "linkedin.com/learning",
        "HackerRank": "hackerrank.com",
        "LeetCode": "leetcode.com",
        "Kaggle": "kaggle.com",
        "Stack Overflow": "stackoverflow.com",
        "GitHub": "github.com",
        "OpenStax": "openstax.org",
        "OER Commons": "oercommons.org"
    }

    # Define resource types
    RESOURCE_TYPES = [
        "article",
        "video",
        "course",
        "book",
        "tutorial",
        "documentation",
        "interactive",
        "exercise",
        "quiz",
        "project",
        "podcast",
        "webinar",
        "cheatsheet",
        "infographic"
    ]

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

        # In-memory cache for discovered resources
        self.resource_cache = {}

        # Create the prompt template for resource discovery
        template = """
        You are a Learning Coach that discovers educational resources.

        Find relevant learning resources based on the following information:

        Topic: {topic}
        Difficulty level: {difficulty}
        Resource type preference: {resource_type}
        Learning style: {learning_style}
        Additional requirements: {additional_requirements}

        For each resource, provide:
        1. Title - Clear and descriptive title
        2. URL - Use realistic URLs for well-known educational platforms
        3. Type - One of: article, video, course, book, tutorial, documentation, interactive, exercise, quiz, project, podcast, webinar, cheatsheet, infographic
        4. Brief description - What the resource covers and why it's valuable
        5. Difficulty level - beginner, intermediate, or advanced
        6. Estimated time to complete - e.g., '30 minutes', '2 hours', '4 weeks'
        7. Topics covered - List of specific topics/concepts covered
        8. Source - The platform or organization providing the resource (e.g., Khan Academy, Coursera)
        9. Free - Whether the resource is free (true) or paid (false)
        10. Interactive - Whether the resource involves interactive elements (true/false)
        11. Language - The language of the resource (default to English)

        Provide a diverse set of high-quality resources from reputable sources.
        Include a mix of resource types that match the user's learning style.
        For visual learners, prioritize videos and infographics.
        For reading/writing learners, prioritize articles and books.
        For auditory learners, prioritize podcasts and video lectures.
        For kinesthetic learners, prioritize interactive exercises and projects.

        Also provide a recommended sequence for consuming these resources in an optimal learning order.

        Use these educational platforms for realistic resources:
        {platforms}

        {format_instructions}
        """

        self.prompt = PromptTemplate(
            template=template,
            input_variables=["topic", "difficulty", "resource_type", "learning_style", "additional_requirements"],
            partial_variables={
                "platforms": "\n".join([f"- {platform}: {domain}" for platform, domain in self.EDUCATIONAL_PLATFORMS.items()]),
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )

        # Create the chain
        self.chain = self.prompt | self.llm | self.output_parser

        # Create the prompt template for resource recommendations
        recommend_template = """
        You are a Learning Coach that recommends personalized learning resources.

        Based on the user's profile and learning history, recommend the most suitable resources from the available options.

        User profile:
        - Learning style: {learning_style}
        - Current knowledge level: {current_knowledge}
        - Time availability: {time_availability}
        - Preferred resource types: {preferred_resource_types}
        - Learning goals: {learning_goals}

        Available resources:
        {available_resources}

        Previously consumed resources:
        {previous_resources}

        Recommend 3-5 resources that:
        1. Match the user's learning style
        2. Are appropriate for their knowledge level
        3. Fit within their time constraints
        4. Help them progress toward their learning goals
        5. Build upon their previous learning
        6. Provide a diverse mix of content types

        For each recommendation, explain why it's suitable for this specific user.

        {format_instructions}
        """

        self.recommend_prompt = PromptTemplate(
            template=recommend_template,
            input_variables=[
                "learning_style",
                "current_knowledge",
                "time_availability",
                "preferred_resource_types",
                "learning_goals",
                "available_resources",
                "previous_resources"
            ],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            }
        )

        # Create the recommendation chain
        self.recommend_chain = self.recommend_prompt | self.llm | self.output_parser

        logger.info(f"Content discovery service initialized with model: {model_name}")

    async def discover_resources(
        self,
        topic: str,
        difficulty: str = "beginner",
        resource_type: str = "any",
        learning_style: str = "visual",
        additional_requirements: str = "",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Discover learning resources.

        Args:
            topic: The topic to find resources for
            difficulty: The difficulty level
            resource_type: Preferred resource type
            learning_style: The user's learning style
            additional_requirements: Any additional requirements or preferences
            use_cache: Whether to use cached results if available

        Returns:
            Dict containing the discovered resources
        """
        logger.info(f"Discovering resources for topic: {topic}")

        # Create a cache key
        cache_key = f"{topic}_{difficulty}_{resource_type}_{learning_style}"

        # Check cache if enabled
        if use_cache and cache_key in self.resource_cache:
            logger.info(f"Using cached resources for topic: {topic}")
            return self.resource_cache[cache_key]

        try:
            result = await self.chain.ainvoke({
                "topic": topic,
                "difficulty": difficulty,
                "resource_type": resource_type,
                "learning_style": learning_style,
                "additional_requirements": additional_requirements
            })

            # Validate and clean up the results
            result = self._validate_resources(result, topic)

            # Cache the results
            if use_cache:
                self.resource_cache[cache_key] = result

            logger.info(f"Discovered {result['total_count']} resources for topic: {topic}")
            return result
        except Exception as e:
            logger.error(f"Error discovering resources: {str(e)}")
            # Return a simplified resource list if discovery fails
            fallback_result = {
                "resources": [
                    {
                        "title": f"Introduction to {topic}",
                        "url": f"https://example.com/{topic.lower().replace(' ', '-')}",
                        "type": "article",
                        "description": f"A beginner-friendly introduction to {topic}",
                        "difficulty": "beginner",
                        "estimated_time": "30 minutes",
                        "topics": [topic],
                        "source": "Example Learning Platform",
                        "free": True,
                        "interactive": False,
                        "language": "English"
                    }
                ],
                "query": topic,
                "total_count": 1,
                "recommended_sequence": [f"Introduction to {topic}"]
            }
            return fallback_result

    def _validate_resources(self, resources_data: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Validate and clean up resource data.

        Args:
            resources_data: The resource data to validate
            topic: The topic of the resources

        Returns:
            Validated and cleaned up resource data
        """
        # Ensure all required fields are present
        for i, resource in enumerate(resources_data.get("resources", [])):
            # Ensure URL is properly formatted
            if "url" in resource and not resource["url"].startswith("http"):
                resource["url"] = "https://" + resource["url"]

            # Ensure type is valid
            if "type" in resource and resource["type"].lower() not in self.RESOURCE_TYPES:
                resource["type"] = "article"  # Default to article

            # Ensure difficulty is valid
            if "difficulty" in resource and resource["difficulty"].lower() not in ["beginner", "intermediate", "advanced"]:
                resource["difficulty"] = "beginner"  # Default to beginner

            # Ensure topics includes the main topic
            if "topics" in resource and isinstance(resource["topics"], list):
                if topic.lower() not in [t.lower() for t in resource["topics"]]:
                    resource["topics"].append(topic)

            # Set defaults for missing fields
            resource.setdefault("free", True)
            resource.setdefault("interactive", False)
            resource.setdefault("language", "English")

        # Ensure total_count matches the actual number of resources
        resources_data["total_count"] = len(resources_data.get("resources", []))

        # Ensure query is set
        resources_data.setdefault("query", topic)

        # Ensure recommended_sequence is set
        if "recommended_sequence" not in resources_data or not resources_data["recommended_sequence"]:
            resources_data["recommended_sequence"] = [r["title"] for r in resources_data.get("resources", [])]

        return resources_data

    async def recommend_resources(
        self,
        available_resources: List[Dict[str, Any]],
        learning_style: str = "visual",
        current_knowledge: str = "beginner",
        time_availability: str = "1 hour per day",
        preferred_resource_types: List[str] = None,
        learning_goals: str = "",
        previous_resources: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Recommend resources based on user profile and available resources.

        Args:
            available_resources: List of available resources to recommend from
            learning_style: The user's learning style
            current_knowledge: The user's current knowledge level
            time_availability: The user's time availability
            preferred_resource_types: The user's preferred resource types
            learning_goals: The user's learning goals
            previous_resources: Resources the user has previously consumed

        Returns:
            Dict containing the recommended resources
        """
        logger.info("Generating personalized resource recommendations")

        if preferred_resource_types is None:
            preferred_resource_types = ["article", "video", "course"]

        if previous_resources is None:
            previous_resources = []

        try:
            result = await self.recommend_chain.ainvoke({
                "learning_style": learning_style,
                "current_knowledge": current_knowledge,
                "time_availability": time_availability,
                "preferred_resource_types": ", ".join(preferred_resource_types),
                "learning_goals": learning_goals,
                "available_resources": json.dumps(available_resources),
                "previous_resources": json.dumps(previous_resources)
            })

            logger.info(f"Generated {len(result.get('resources', []))} resource recommendations")
            return result
        except Exception as e:
            logger.error(f"Error recommending resources: {str(e)}")
            # Return a simplified recommendation if recommendation fails
            return {
                "resources": available_resources[:3] if len(available_resources) >= 3 else available_resources,
                "query": "personalized recommendations",
                "total_count": min(3, len(available_resources)),
                "recommended_sequence": [r["title"] for r in available_resources[:3]] if len(available_resources) >= 3 else [r["title"] for r in available_resources]
            }

    def filter_resources(
        self,
        resources: List[Dict[str, Any]],
        difficulty: Optional[str] = None,
        resource_type: Optional[str] = None,
        max_time_minutes: Optional[int] = None,
        free_only: bool = False,
        interactive_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Filter resources based on criteria.

        Args:
            resources: The resources to filter
            difficulty: Filter by difficulty level
            resource_type: Filter by resource type
            max_time_minutes: Filter by maximum time in minutes
            free_only: Filter to only free resources
            interactive_only: Filter to only interactive resources

        Returns:
            Filtered list of resources
        """
        logger.info("Filtering resources")

        filtered_resources = resources

        # Filter by difficulty
        if difficulty:
            filtered_resources = [r for r in filtered_resources if r.get("difficulty", "").lower() == difficulty.lower()]

        # Filter by resource type
        if resource_type and resource_type.lower() != "any":
            filtered_resources = [r for r in filtered_resources if r.get("type", "").lower() == resource_type.lower()]

        # Filter by maximum time
        if max_time_minutes:
            def parse_time(time_str):
                """Parse time string to minutes."""
                try:
                    if "minute" in time_str.lower():
                        return int(time_str.lower().split("minute")[0].strip())
                    elif "hour" in time_str.lower():
                        return int(time_str.lower().split("hour")[0].strip()) * 60
                    elif "day" in time_str.lower():
                        return int(time_str.lower().split("day")[0].strip()) * 24 * 60
                    elif "week" in time_str.lower():
                        return int(time_str.lower().split("week")[0].strip()) * 7 * 24 * 60
                    else:
                        return float('inf')
                except:
                    return float('inf')

            filtered_resources = [r for r in filtered_resources if parse_time(r.get("estimated_time", "")) <= max_time_minutes]

        # Filter by free/paid
        if free_only:
            filtered_resources = [r for r in filtered_resources if r.get("free", True)]

        # Filter by interactive
        if interactive_only:
            filtered_resources = [r for r in filtered_resources if r.get("interactive", False)]

        logger.info(f"Filtered to {len(filtered_resources)} resources")
        return filtered_resources

    def get_resource_types(self) -> List[str]:
        """Get all available resource types.

        Returns:
            List of resource types
        """
        return self.RESOURCE_TYPES

    def get_educational_platforms(self) -> Dict[str, str]:
        """Get all available educational platforms.

        Returns:
            Dict of platform names to domains
        """
        return self.EDUCATIONAL_PLATFORMS
