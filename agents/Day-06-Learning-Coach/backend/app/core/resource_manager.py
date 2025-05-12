"""
Resource Manager for the Learning Coach Agent.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

import logging

logger = logging.getLogger(__name__)

class ResourceManager:
    """Manager for learning resources."""

    def __init__(self):
        """Initialize the resource manager."""
        self.resources = {}
        self.ratings = {}

        # Add some sample resources
        self._add_sample_resources()

    def _add_sample_resources(self):
        """Add sample resources for development."""
        sample_resources = [
            {
                "id": str(uuid.uuid4()),
                "title": "Python for Beginners",
                "url": "https://www.python.org/about/gettingstarted/",
                "type": "article",
                "description": "Official Python getting started guide",
                "difficulty": "beginner",
                "estimated_time": "30 minutes",
                "topics": ["Python", "Programming Basics"],
                "source": "python.org"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Introduction to HTML and CSS",
                "url": "https://www.freecodecamp.org/learn/responsive-web-design/",
                "type": "course",
                "description": "Learn HTML and CSS fundamentals with interactive exercises",
                "difficulty": "beginner",
                "estimated_time": "10 hours",
                "topics": ["HTML", "CSS", "Web Development"],
                "source": "freecodecamp.org"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "JavaScript Crash Course",
                "url": "https://www.youtube.com/watch?v=hdI2bqOjy3c",
                "type": "video",
                "description": "Quick introduction to JavaScript fundamentals",
                "difficulty": "beginner",
                "estimated_time": "90 minutes",
                "topics": ["JavaScript", "Web Development"],
                "source": "YouTube"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Advanced Python Programming",
                "url": "https://realpython.com/python-advanced-features/",
                "type": "article",
                "description": "Deep dive into advanced Python features",
                "difficulty": "advanced",
                "estimated_time": "2 hours",
                "topics": ["Python", "Advanced Programming"],
                "source": "realpython.com"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "React.js Documentation",
                "url": "https://reactjs.org/docs/getting-started.html",
                "type": "documentation",
                "description": "Official React.js documentation",
                "difficulty": "intermediate",
                "estimated_time": "5 hours",
                "topics": ["React", "JavaScript", "Web Development"],
                "source": "reactjs.org"
            },
            # Web Development Resources
            {
                "id": str(uuid.uuid4()),
                "title": "MDN Web Docs",
                "url": "https://developer.mozilla.org/en-US/docs/Web",
                "type": "documentation",
                "description": "Comprehensive web development documentation",
                "difficulty": "beginner",
                "estimated_time": "ongoing",
                "topics": ["HTML", "CSS", "JavaScript", "Web Development"],
                "source": "mozilla.org"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "CSS Tricks",
                "url": "https://css-tricks.com/",
                "type": "blog",
                "description": "Tips, tricks, and techniques on using CSS",
                "difficulty": "intermediate",
                "estimated_time": "varies",
                "topics": ["CSS", "Web Development"],
                "source": "css-tricks.com"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "JavaScript.info",
                "url": "https://javascript.info/",
                "type": "tutorial",
                "description": "Modern JavaScript tutorial from basics to advanced",
                "difficulty": "beginner",
                "estimated_time": "20 hours",
                "topics": ["JavaScript", "Web Development"],
                "source": "javascript.info"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Web.dev by Google",
                "url": "https://web.dev/",
                "type": "resource",
                "description": "Guidance for modern web development by Google",
                "difficulty": "intermediate",
                "estimated_time": "varies",
                "topics": ["Web Development", "Performance", "Accessibility"],
                "source": "web.dev"
            },
            {
                "id": str(uuid.uuid4()),
                "title": "Frontend Masters",
                "url": "https://frontendmasters.com/",
                "type": "course",
                "description": "In-depth courses on frontend development",
                "difficulty": "intermediate",
                "estimated_time": "varies",
                "topics": ["JavaScript", "React", "Web Development"],
                "source": "frontendmasters.com"
            }
        ]

        for resource in sample_resources:
            self.resources[resource["id"]] = resource

    def add_resource(self, resource: Dict[str, Any]) -> str:
        """
        Add a new resource.

        Args:
            resource: Resource data to add

        Returns:
            ID of the added resource
        """
        # Generate an ID if not provided
        if "id" not in resource:
            resource["id"] = str(uuid.uuid4())

        # Add timestamp if not provided
        if "created_at" not in resource:
            resource["created_at"] = datetime.now(timezone.utc).isoformat()

        # Store the resource
        self.resources[resource["id"]] = resource

        logger.info(f"Added resource: {resource['title']} with ID: {resource['id']}")
        return resource["id"]

    def add_resources_for_topic(self, topic: str, resources: List[Dict[str, Any]]) -> List[str]:
        """
        Add multiple resources for a specific topic.

        Args:
            topic: The topic these resources are for
            resources: List of resource data to add

        Returns:
            List of IDs of the added resources
        """
        resource_ids = []

        for resource in resources:
            # Make sure the topic is included
            if "topics" not in resource:
                resource["topics"] = [topic]
            elif topic not in resource["topics"]:
                resource["topics"].append(topic)

            # Add the resource
            resource_id = self.add_resource(resource)
            resource_ids.append(resource_id)

        logger.info(f"Added {len(resource_ids)} resources for topic: {topic}")
        return resource_ids

    def get_resources(
        self,
        topic: Optional[str] = None,
        resource_type: Optional[str] = None,
        difficulty: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get resources, optionally filtered by topic, type, and difficulty.

        Args:
            topic: Optional topic to filter by
            resource_type: Optional resource type to filter by
            difficulty: Optional difficulty level to filter by
            skip: Number of resources to skip
            limit: Maximum number of resources to return

        Returns:
            List of resources
        """
        filtered_resources = list(self.resources.values())

        if topic:
            filtered_resources = [
                r for r in filtered_resources
                if any(t.lower() == topic.lower() for t in r["topics"])
            ]

        if resource_type:
            filtered_resources = [
                r for r in filtered_resources
                if r["type"].lower() == resource_type.lower()
            ]

        if difficulty:
            filtered_resources = [
                r for r in filtered_resources
                if r["difficulty"].lower() == difficulty.lower()
            ]

        # Sort by title
        filtered_resources.sort(key=lambda r: r["title"])

        # Apply pagination
        return filtered_resources[skip:skip + limit]

    def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific resource by ID.

        Args:
            resource_id: ID of the resource to get

        Returns:
            Resource data or None if not found
        """
        return self.resources.get(resource_id)

    def search_resources(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Search for resources based on a query string.

        Args:
            query: Search query
            skip: Number of resources to skip
            limit: Maximum number of resources to return

        Returns:
            List of matching resources
        """
        query = query.lower()

        matching_resources = [
            r for r in self.resources.values()
            if query in r["title"].lower() or
               query in r["description"].lower() or
               any(query in topic.lower() for topic in r["topics"])
        ]

        # Sort by relevance (simple implementation)
        matching_resources.sort(
            key=lambda r: (
                1 if query in r["title"].lower() else 0,
                1 if query in r["description"].lower() else 0
            ),
            reverse=True
        )

        return matching_resources[skip:skip + limit]

    def recommend_resources(
        self,
        topic: str,
        learning_style: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get personalized resource recommendations.

        Args:
            topic: Topic to recommend resources for
            learning_style: Optional learning style preference
            difficulty: Optional difficulty level
            limit: Maximum number of resources to recommend

        Returns:
            List of recommended resources
        """
        # Simple implementation for now
        filtered_resources = [
            r for r in self.resources.values()
            if any(t.lower() == topic.lower() for t in r["topics"])
        ]

        if difficulty:
            filtered_resources = [
                r for r in filtered_resources
                if r["difficulty"].lower() == difficulty.lower()
            ]

        # Sort by type to provide a mix of resource types
        filtered_resources.sort(key=lambda r: r["type"])

        return filtered_resources[:limit]

    def rate_resource(
        self,
        resource_id: str,
        user_id: int,
        rating: int,
        feedback: Optional[str] = None
    ) -> None:
        """
        Rate a resource and provide optional feedback.

        Args:
            resource_id: ID of the resource to rate
            user_id: ID of the user providing the rating
            rating: Rating value (1-5)
            feedback: Optional feedback text
        """
        if resource_id not in self.resources:
            raise ValueError(f"Resource {resource_id} not found")

        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        # Store the rating
        if resource_id not in self.ratings:
            self.ratings[resource_id] = {}

        self.ratings[resource_id][user_id] = {
            "rating": rating,
            "feedback": feedback,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        logger.info(f"User {user_id} rated resource {resource_id} with {rating}/5")
