# TravelBuddy - Conversational Travel Agent

TravelBuddy is an AI-powered conversational travel planning assistant built with PydanticAI. It helps users with various travel-related queries and tasks, including creating personalized travel itineraries, providing transportation information, weather forecasts, attraction recommendations, and more.

## Features

- **Conversational Interface**: Chat naturally with the agent about your travel plans
- **Context Awareness**: The agent remembers previous parts of the conversation
- **Travel Itinerary Generation**: Get detailed day-by-day travel plans
- **Transportation Information**: Learn about transportation options between locations
- **Attraction Recommendations**: Discover popular attractions at your destination
- **Restaurant Suggestions**: Get restaurant recommendations based on location
- **Hotel Information**: Find accommodation options for your trip
- **Local Tips**: Receive cultural insights and local tips for your destination
- **Weather Forecasts**: Check the weather at your travel destination

## Setup

### Prerequisites

- Python 3.8 or higher
- Required Python packages:
  - pydantic-ai
  - httpx
  - python-dotenv (optional, for loading environment variables from .env file)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/travel-agent.git
   cd travel-agent
   ```

2. Install the required dependencies:
   ```
   pip install pydantic-ai httpx python-dotenv
   ```

3. Set up your API keys:
   - Copy the `.env.example` file to `.env`:
     ```
     cp .env.example .env
     ```
   - Edit the `.env` file and add your actual API keys

### API Keys

The following API keys are used by the travel agent:

- **OpenAI API Key** (Required): Powers the language model
  - Sign up at [OpenAI](https://platform.openai.com/signup)
  
- **Google Maps API Key** (Optional but recommended): Used for transportation, restaurant, and hotel information
  - Get a key from [Google Cloud Platform](https://console.cloud.google.com/)
  - Enable the Maps JavaScript API, Places API, and Directions API
  
- **Tavily API Key** (Optional but recommended): Used for attractions and local tips
  - Sign up at [Tavily](https://tavily.com/)
  
- **OpenWeatherMap API Key** (Optional): Used for weather forecasts
  - Sign up at [OpenWeatherMap](https://openweathermap.org/api)

## Usage

### Interactive Conversation

Run the agent in interactive mode:

```
python agent/agent.py
```

This will start a conversation where you can chat with TravelBuddy. Type your travel-related questions or requests, and the agent will respond conversationally.

Special commands:
- Type `itinerary` to see an example of generating a travel itinerary
- Type `exit` or `quit` to end the conversation

### Demo Conversation

To see a predefined conversation that demonstrates the agent's capabilities, edit `agent/agent.py` and uncomment the `asyncio.run(demo_conversation())` line in the `if __name__ == "__main__":` block.

### Programmatic Usage

You can also use the TravelAgent class in your own code:

```python
from agent.agent import TravelAgent
import asyncio

async def example():
    agent = TravelAgent(openai_api_key="your_openai_api_key")
    
    # Chat with the agent
    response = await agent.chat("I'm planning a trip to Paris next month. What should I know?")
    print(response)
    
    # Generate an itinerary
    itinerary = await agent.generate_itinerary({
        "from_location": "London",
        "to_location": "Paris",
        "start_date": "2024-07-01",
        "end_date": "2024-07-03",
        "preferences": {
            "budget": "medium",
            "interests": ["art", "food", "history"],
            "transportation": "train"
        }
    })
    print(itinerary["itinerary"])

asyncio.run(example())
```

## License

[MIT License](LICENSE)
