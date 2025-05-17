# TravelBuddy - Quick Start Guide

This guide will help you get started with TravelBuddy, an AI-powered travel planning assistant.

## Prerequisites

Before you begin, make sure you have:

- Python 3.12 or higher installed
- API keys for the following services:
  - OpenAI (required)
  - Google Maps (recommended)
  - OpenWeatherMap (recommended)
  - Tavily (recommended)

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/travel_agent.git
   cd travel_agent
   ```

2. **Set up a virtual environment**

   ```bash
   python -m venv agent/.venv
   source agent/.venv/bin/activate  # On Windows: agent\.venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   cd agent
   uv sync
   ```

## Configuration

1. **Create a `.env` file in the `agent` directory with your API keys:**

   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

2. **Enable required APIs in Google Cloud Console:**
   - Distance Matrix API
   - Places API
   - Geocoding API

## Running TravelBuddy

### Command Line Interface

Run the agent in interactive mode:

```bash
cd agent
uv run agent.py
```

You'll see a welcome message and can start chatting with TravelBuddy.

**Example commands:**
- Ask travel questions: "What should I know before visiting Japan?"
- Generate an itinerary: Type `itinerary` to see an example
- Exit: Type `exit` or `quit`

### Web Interface

Launch the web interface:

```bash
cd agent
uv run app.py
```

This will start a Gradio web server, typically at http://127.0.0.1:7860/

The web interface has two tabs:
1. **Chat**: For conversational interactions
2. **Generate Itinerary**: For creating detailed travel plans

## Example Usage

### Asking Travel Questions

You can ask TravelBuddy various travel-related questions:

- "What's the best time to visit Paris?"
- "How do I get from London to Edinburgh?"
- "What are the top attractions in Tokyo?"
- "What's the weather like in New York in December?"
- "Can you recommend restaurants in Rome?"
- "What should I know about local customs in Thailand?"

### Generating an Itinerary

To generate a travel itinerary, you'll need to provide:

1. **Origin and destination**
   - From: "San Francisco"
   - To: "Los Angeles"

2. **Travel dates**
   - Start date: "2024-07-01"
   - End date: "2024-07-05"

3. **Preferences**
   - Budget: "medium" (options: budget, medium, luxury)
   - Transportation: "car" (options: car, train, flight, mixed)
   - Accommodation: "hotel" (options: hotel, hostel, airbnb)
   - Interests: "food, nature, history" (comma-separated list)
   - Number of travelers: 2

TravelBuddy will then generate a day-by-day itinerary with:
- Transportation options
- Weather forecasts
- Recommended attractions
- Restaurant suggestions
- Hotel recommendations
- Local tips and insights

## Using TravelBuddy in Your Code

You can integrate TravelBuddy into your Python applications:

```python
from agent.agent import TravelAgent
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def example():
    # Initialize the agent
    agent = TravelAgent(openai_api_key=os.getenv("OPENAI_API_KEY"))
    
    # Chat with the agent
    response = await agent.chat("I'm planning a trip to Barcelona. What should I know?")
    print(f"Response: {response}")
    
    # Generate an itinerary
    itinerary_request = {
        "from_location": "Madrid",
        "to_location": "Barcelona",
        "start_date": "2024-08-01",
        "end_date": "2024-08-03",
        "preferences": {
            "budget": "medium",
            "interests": ["art", "food", "architecture"],
            "transportation": "train"
        }
    }
    
    result = await agent.generate_itinerary(itinerary_request)
    print(result["itinerary"])

# Run the example
asyncio.run(example())
```

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Error: "OPENAI_API_KEY environment variable is not set!"
   - Solution: Make sure you've created a `.env` file with your API keys or set them as environment variables

2. **Google Maps API Errors**
   - Error: "This API project is not authorized to use this API"
   - Solution: Enable the required APIs in your Google Cloud Console

3. **Installation Issues**
   - Error: "No module named 'pydantic_ai'"
   - Solution: Make sure you've activated the virtual environment and installed all dependencies

4. **Gradio Interface Issues**
   - Error: "Address already in use"
   - Solution: Change the port with `demo.launch(server_port=7861)`

## Getting Help

If you encounter any issues:

1. Check the detailed documentation in the `docs` directory
2. Look for error messages in the console output
3. Enable debug logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

## Next Steps

- Explore the [full documentation](travel_agent_documentation.md) for detailed information
- Check the [technical documentation](technical_documentation.md) for implementation details
- Customize the agent by modifying the system prompt in `agent.py`
- Add new tool functions to extend the agent's capabilities
