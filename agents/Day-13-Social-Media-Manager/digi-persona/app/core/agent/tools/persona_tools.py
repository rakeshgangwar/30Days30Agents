"""
Persona Tools

This module provides tools for persona agents to interact with the system.
"""
from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool


class PersonaProfileTool(BaseTool):
    """Tool for accessing persona profile information."""

    name: str = "persona_profile"
    description: str = "Get information about the persona's profile, preferences, and characteristics."

    def __init__(self, persona_data: Dict[str, Any]):
        """Initialize with persona data."""
        super().__init__()
        self.persona_data = persona_data

    def _run(self, query: Optional[str] = None) -> str:
        """Return persona profile information."""
        if not query:
            # Return all profile information
            return f"""
            Persona Profile:
            Name: {self.persona_data.get('name', 'Unknown')}
            Description: {self.persona_data.get('description', 'No description available')}
            Interests: {', '.join(self.persona_data.get('interests', ['None']))}
            Tone: {self.persona_data.get('tone', 'Neutral')}
            Style: {self.persona_data.get('style', 'Standard')}
            """

        # Handle specific queries about the persona
        query = query.lower()
        if "name" in query:
            return f"The persona's name is {self.persona_data.get('name', 'Unknown')}."
        elif "description" in query or "about" in query:
            return f"Description: {self.persona_data.get('description', 'No description available')}"
        elif "interest" in query:
            return f"Interests: {', '.join(self.persona_data.get('interests', ['None']))}"
        elif "tone" in query:
            return f"Tone: {self.persona_data.get('tone', 'Neutral')}"
        elif "style" in query:
            return f"Style: {self.persona_data.get('style', 'Standard')}"
        else:
            return f"No specific information found for query: {query}"

    async def _arun(self, query: Optional[str] = None) -> str:
        """Async implementation of _run."""
        return self._run(query)


class ContentHistoryTool(BaseTool):
    """Tool for accessing persona's content history."""

    name: str = "content_history"
    description: str = "Get information about the persona's previous content and posts."

    def __init__(self, content_history: List[Dict[str, Any]]):
        """Initialize with content history."""
        super().__init__()
        self.content_history = content_history

    def _run(self, query: Optional[str] = None) -> str:
        """Return content history information."""
        if not self.content_history:
            return "No content history available for this persona."

        if not query:
            # Return summary of recent content
            recent_content = self.content_history[:5]  # Last 5 items
            result = "Recent content:\n\n"
            for i, content in enumerate(recent_content, 1):
                result += f"{i}. {content.get('text', 'No text')} ({content.get('platform', 'Unknown')} - {content.get('created_at', 'Unknown date')})\n"
            return result

        # Handle specific queries about content history
        query = query.lower()
        if "recent" in query:
            count = 3  # Default
            # Try to extract a number from the query
            import re
            numbers = re.findall(r'\d+', query)
            if numbers:
                count = min(int(numbers[0]), len(self.content_history))

            recent_content = self.content_history[:count]
            result = f"Last {count} content items:\n\n"
            for i, content in enumerate(recent_content, 1):
                result += f"{i}. {content.get('text', 'No text')} ({content.get('platform', 'Unknown')} - {content.get('created_at', 'Unknown date')})\n"
            return result

        elif "platform" in query:
            # Try to extract platform name from query
            platforms = ["twitter", "linkedin", "facebook", "instagram", "bluesky"]
            platform = next((p for p in platforms if p in query), None)

            if platform:
                platform_content = [c for c in self.content_history if c.get('platform', '').lower() == platform]
                if not platform_content:
                    return f"No content found for platform: {platform}"

                result = f"Content on {platform}:\n\n"
                for i, content in enumerate(platform_content[:5], 1):
                    result += f"{i}. {content.get('text', 'No text')} ({content.get('created_at', 'Unknown date')})\n"
                return result
            else:
                return "Please specify a platform (e.g., Twitter, LinkedIn, etc.)"

        else:
            return "Please specify what content history you want to retrieve (e.g., 'recent', 'platform Twitter', etc.)"

    async def _arun(self, query: Optional[str] = None) -> str:
        """Async implementation of _run."""
        return self._run(query)


def get_persona_tools(persona_id: int, persona_data: Dict[str, Any], content_history: List[Dict[str, Any]] = None) -> List[BaseTool]:
    """
    Get tools for a specific persona.

    Args:
        persona_id: The ID of the persona
        persona_data: Dictionary containing persona profile information
        content_history: List of dictionaries containing content history

    Returns:
        List of tools for the persona
    """
    tools = []

    # Add profile tool
    tools.append(PersonaProfileTool(persona_data))

    # Add content history tool if available
    if content_history:
        tools.append(ContentHistoryTool(content_history))

    # Add more tools as needed

    return tools
