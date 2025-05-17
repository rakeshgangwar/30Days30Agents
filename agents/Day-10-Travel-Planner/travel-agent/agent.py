import os
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from pydantic_ai import Agent
from httpx import AsyncClient

# Try to import ModelMessage from pydantic_ai.messages
try:
    from pydantic_ai.messages import ModelMessage
except ImportError:
    # If import fails, create a type alias as a fallback
    from typing import Any as ModelMessage

# Try to load environment variables with python-dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If dotenv is not installed, print a warning
    print("Warning: python-dotenv not installed. Environment variables must be set manually.")

from dependencies import TravelDependencies
from travel_tools import (
    get_transportation,
    get_weather_forecast,
    get_attractions,
    get_restaurants,
    get_hotels,
    get_local_tips
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TravelAgent:
    """AI-powered conversational travel planning agent using PydanticAI."""

    def __init__(self, openai_api_key: str):
        """Initialize the travel agent.

        Args:
            openai_api_key: OpenAI API key for the LLM.
        """
        logger.info("Initializing TravelAgent...")

        # Create the agent with appropriate system prompt for conversational interactions
        self.agent = Agent(
            'openai:gpt-4o',
            deps_type=TravelDependencies,
            instructions=(
                "You are a sophisticated AI travel planning assistant named TravelBuddy. "
                "You can help users with various travel-related queries and tasks, including: "
                "- Creating personalized travel itineraries based on user preferences "
                "- Providing information about transportation options between locations "
                "- Sharing weather forecasts for travel destinations "
                "- Recommending attractions, restaurants, and hotels "
                "- Offering local tips and cultural insights "
                "- Answering general travel questions "
                "Use the provided tools to gather information when needed. "
                "Be conversational, helpful, and maintain context throughout the conversation. "
                "If you need more information from the user to provide better assistance, ask clarifying questions."
            ),
            retries=2,  # Allow tools to retry on failure
        )

        # Register all the tools with the agent
        self.agent.tool(get_transportation)
        self.agent.tool(get_weather_forecast)
        self.agent.tool(get_attractions)
        self.agent.tool(get_restaurants)
        self.agent.tool(get_hotels)
        self.agent.tool(get_local_tips)

        # Store the API key
        self.openai_api_key = openai_api_key

        # Initialize message history
        self.message_history: List[ModelMessage] = []

    async def chat(self, user_message: str) -> str:
        """Process a user message and generate a response.

        Args:
            user_message: The user's message or query.

        Returns:
            The agent's response as a string.
        """
        logger.info(f"Processing user message: {user_message}")

        # Set up the dependencies
        async with AsyncClient() as client:
            deps = TravelDependencies(
                client=client,
                openai_api_key=self.openai_api_key,
                google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY"),
                tavily_api_key=os.getenv("TAVILY_API_KEY"),
                openweathermap_api_key=os.getenv("OPENWEATHERMAP_API_KEY")
            )

            # Run the agent with the user message and message history
            result = await self.agent.run(
                user_message,
                deps=deps,
                message_history=self.message_history
            )

            # Update message history with new messages from this interaction
            self.message_history = result.all_messages()

            # Return the agent's response
            return result.output

    async def generate_itinerary(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a travel itinerary with comprehensive information.

        This method maintains backward compatibility with the task-based approach
        but uses the conversational agent internally.

        Args:
            request_data: Dictionary containing travel request details.

        Returns:
            Dictionary containing the generated itinerary and related information.
        """
        from_location = request_data["from_location"]
        to_location = request_data["to_location"]
        start_date = request_data["start_date"]
        end_date = request_data.get("end_date", start_date)  # Default to start_date if not provided
        preferences = request_data.get("preferences", {})
        num_travelers = request_data.get("number_of_travelers", 1)
        include_weather = request_data.get("include_weather", True)
        include_local_tips = request_data.get("include_local_tips", True)

        # Calculate number of days
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = (end - start).days + 1

        # Create the prompt for the agent
        prompt = f"""Create a {num_days}-day travel itinerary from {from_location} to {to_location}.

TRIP DETAILS:
- Start Date: {start_date}
- End Date: {end_date}
- Duration: {num_days} days
- Travelers: {num_travelers}
- Budget: {preferences.get('budget', 'medium')}
- Transportation: {preferences.get('transportation', 'mixed')}
- Accommodation: {preferences.get('accommodation_type', 'hotel')}
- Interests: {', '.join(preferences.get('interests', ['culture', 'food', 'sightseeing']))}

Please use the available tools to gather information about transportation options, weather,
attractions, restaurants, hotels, and local tips. Then create a detailed day-by-day itinerary.

Format the response as a detailed day-by-day itinerary starting with:
"Here is your {num_days}-day itinerary from {from_location} to {to_location}:"

Include for each day:
1. Date and day number
2. Morning activities with times
3. Afternoon activities with times
4. Evening activities with times
5. Restaurant recommendations for meals
6. Transportation details
7. Hotel/accommodation information

End with practical travel tips.
"""
        # Reset message history for a fresh itinerary generation
        self.message_history = []

        # Use the chat method to generate the itinerary
        itinerary = await self.chat(prompt)

        # Return the formatted response matching frontend requirements
        return {
            "itinerary": itinerary,
            "from_location": from_location,
            "to_location": to_location,
            "start_date": start_date,
            "end_date": end_date,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "includes_weather": include_weather,
                "includes_local_tips": include_local_tips,
                "number_of_travelers": num_travelers
            },
            "request_details": {
                "from_location": from_location,
                "to_location": to_location,
                "start_date": start_date,
                "end_date": end_date,
                "duration_days": num_days,
                "preferences": preferences,
                "number_of_travelers": num_travelers
            }
        }

    async def chat_stream(self, user_message: str) -> AsyncClient:
        """Process a user message and stream the response.

        Args:
            user_message: The user's message or query.

        Returns:
            An async iterator that yields response chunks.
        """
        logger.info(f"Processing user message (streaming): {user_message}")

        # Set up the dependencies
        client = AsyncClient()
        deps = TravelDependencies(
            client=client,
            openai_api_key=self.openai_api_key,
            google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            openweathermap_api_key=os.getenv("OPENWEATHERMAP_API_KEY")
        )

        # Run the agent with streaming
        stream_result = await self.agent.run_stream(
            user_message,
            deps=deps,
            message_history=self.message_history
        )

        # Update message history after streaming is complete
        self.message_history = stream_result.all_messages()

        return stream_result


async def main():
    """Run a simple example of the conversational travel agent."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable is not set!")
        return

    # Create the travel agent
    agent = TravelAgent(openai_api_key=openai_api_key)

    print("Welcome to TravelBuddy - Your AI Travel Assistant!")
    print("Type 'exit' or 'quit' to end the conversation.")
    print("Type 'itinerary' to see an example of generating a travel itinerary.")
    print("-" * 50)

    while True:
        # Get user input
        user_input = input("\nYou: ")

        # Check for exit command
        if user_input.lower() in ["exit", "quit"]:
            print("Thank you for using TravelBuddy. Goodbye!")
            break

        # Check for itinerary example command
        if user_input.lower() == "itinerary":
            print("\nGenerating an example itinerary...")
            itinerary = await agent.generate_itinerary(
                {
                    "from_location": "San Francisco",
                    "to_location": "Los Angeles",
                    "start_date": "2024-06-01",
                    "end_date": "2024-06-03",
                    "preferences": {
                        "budget": "medium",
                        "interests": ["food", "culture", "nature"],
                        "transportation": "car"
                    }
                }
            )
            print("\nGenerated Itinerary:")
            print(itinerary["itinerary"])
            continue

        # Process the user message and get a response
        response = await agent.chat(user_input)

        # Display the response
        print(f"\nTravelBuddy: {response}")


async def demo_conversation():
    """Demonstrate a sample conversation with the travel agent."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY environment variable is not set!")
        return

    # Create the travel agent
    agent = TravelAgent(openai_api_key=openai_api_key)

    # Sample conversation
    print("Welcome to TravelBuddy - Your AI Travel Assistant!")
    print("-" * 50)

    # First message
    user_message = "I'm planning a trip to Japan in October. What should I know?"
    print(f"\nYou: {user_message}")
    response = await agent.chat(user_message)
    print(f"\nTravelBuddy: {response}")

    # Second message
    user_message = "What are the best cities to visit for a first-time visitor?"
    print(f"\nYou: {user_message}")
    response = await agent.chat(user_message)
    print(f"\nTravelBuddy: {response}")

    # Third message
    user_message = "Can you recommend some traditional foods I should try?"
    print(f"\nYou: {user_message}")
    response = await agent.chat(user_message)
    print(f"\nTravelBuddy: {response}")

    print("\nDemo conversation complete!")


if __name__ == "__main__":
    """
    To use this conversational travel agent:

    1. Make sure you have the required dependencies installed:
       - pydantic-ai
       - httpx
       - python-dotenv (optional)

    2. Set your API keys as environment variables or in a .env file:
       - OPENAI_API_KEY (required)
       - GOOGLE_MAPS_API_KEY (optional, for transportation and location data)
       - TAVILY_API_KEY (optional, for attractions and local tips)
       - OPENWEATHERMAP_API_KEY (optional, for weather forecasts)

    3. Run this script to start an interactive conversation:
       python agent/agent.py

    4. Or uncomment the demo_conversation() line below to see a predefined conversation.
    """
    # Choose which function to run
    # asyncio.run(demo_conversation())  # Uncomment to run the demo conversation
    asyncio.run(main())  # Interactive conversation
