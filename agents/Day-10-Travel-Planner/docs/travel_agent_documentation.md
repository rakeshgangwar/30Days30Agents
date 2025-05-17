# TravelBuddy - AI Travel Assistant Documentation

## Table of Contents

1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
   - [Command Line Interface](#command-line-interface)
   - [Gradio Web Interface](#gradio-web-interface)
   - [API Integration](#api-integration)
6. [Tools and Functionality](#tools-and-functionality)
   - [Transportation](#transportation)
   - [Weather Forecast](#weather-forecast)
   - [Attractions](#attractions)
   - [Restaurants](#restaurants)
   - [Hotels](#hotels)
   - [Local Tips](#local-tips)
   - [Current Date](#current-date)
7. [Dependencies](#dependencies)
8. [Troubleshooting](#troubleshooting)
9. [Future Enhancements](#future-enhancements)

## Introduction

TravelBuddy is an AI-powered travel planning assistant built using PydanticAI and various travel-related APIs. It provides personalized travel recommendations, itineraries, and answers to travel-related questions through a conversational interface.

The agent can help with:
- Creating personalized travel itineraries
- Providing transportation options between locations
- Sharing weather forecasts for destinations
- Recommending attractions, restaurants, and hotels
- Offering local tips and cultural insights
- Answering general travel questions

## System Architecture

TravelBuddy is built on a modular architecture with the following components:

1. **Core Agent**: Built with PydanticAI, using OpenAI's GPT-4o model for natural language understanding and generation
2. **Tool Functions**: Specialized functions for retrieving travel information from various sources
3. **Dependencies Manager**: Handles API keys and external service connections
4. **User Interfaces**: Command-line and Gradio web interfaces

The system follows a tool-based architecture where the LLM (GPT-4o) acts as the orchestrator, calling specialized tools to gather information and generate responses.

```
┌─────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                 │     │                   │     │                   │
│  User Interface │────▶│  TravelAgent      │────▶│  PydanticAI Agent │
│  (CLI/Gradio)   │     │  (Orchestrator)   │     │  (GPT-4o)         │
│                 │     │                   │     │                   │
└─────────────────┘     └───────────────────┘     └─────────┬─────────┘
                                                            │
                                                            ▼
┌─────────────────┐     ┌───────────────────┐     ┌───────────────────┐
│                 │     │                   │     │                   │
│  External APIs  │◀───▶│  Tool Functions   │◀────│  Dependencies     │
│  (Maps, Weather)│     │  (Travel Tools)   │     │  Manager          │
│                 │     │                   │     │                   │
└─────────────────┘     └───────────────────┘     └───────────────────┘
```

## Installation

### Prerequisites

- Python 3.12 or higher
- API keys for:
  - OpenAI (required)
  - Google Maps (optional, for transportation, restaurants, and hotels)
  - OpenWeatherMap (optional, for weather forecasts)
  - Tavily (optional, for attractions and local tips)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/travel_agent.git
   cd travel_agent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv agent/.venv
   source agent/.venv/bin/activate  # On Windows: agent\.venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   cd agent
   pip install -e .
   ```

## Configuration

TravelBuddy requires API keys to function properly. Set up your environment variables:

1. Create a `.env` file in the `agent` directory:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

2. Ensure the following APIs are enabled in your Google Cloud Console:
   - Distance Matrix API
   - Places API
   - Geocoding API

## Usage

### Command Line Interface

Run the agent in interactive mode:

```bash
cd agent
python agent.py
```

Commands:
- Type your travel questions to chat with the agent
- Type `itinerary` to see an example of generating a travel itinerary
- Type `exit` or `quit` to end the conversation

### Gradio Web Interface

Launch the web interface:

```bash
cd agent
python app.py
```

The interface provides two tabs:
1. **Chat**: For conversational interactions with the agent
2. **Generate Itinerary**: For creating detailed travel plans with specific parameters

### API Integration

Integrate TravelBuddy into your Python application:

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

## Tools and Functionality

### Transportation

The `get_transportation` tool provides transportation options between two locations.

**Features:**
- Supports multiple transportation modes: car, train, mixed
- Uses Google Maps Distance Matrix API for accurate travel times and distances
- Provides step-by-step directions and estimated travel times
- Handles flight inquiries with recommendations for flight booking websites

**API Dependencies:**
- Google Maps Distance Matrix API

### Weather Forecast

The `get_weather_forecast` tool provides weather information for a location on a specific date.

**Features:**
- Current weather conditions for today
- 5-day forecast for future dates
- Temperature, conditions, humidity, and wind information
- Metric units (Celsius, m/s)

**API Dependencies:**
- OpenWeatherMap API

### Attractions

The `get_attractions` tool recommends tourist attractions for a location.

**Features:**
- Top attractions with descriptions
- Ratings and URLs for more information
- Image URLs when available

**API Dependencies:**
- Tavily API for web search and content extraction

### Restaurants

The `get_restaurants` tool recommends restaurants for a location.

**Features:**
- Restaurant recommendations with descriptions
- Cuisine types and ratings
- Contact information and addresses

**API Dependencies:**
- Google Maps Places API

### Hotels

The `get_hotels` tool provides hotel recommendations for a location.

**Features:**
- Hotel listings with descriptions
- Ratings and amenities
- Contact information and addresses

**API Dependencies:**
- Google Maps Places API

### Local Tips

The `get_local_tips` tool provides cultural insights and local advice for a destination.

**Features:**
- Local customs and traditions
- Transportation tips
- Safety information
- Cultural norms

**API Dependencies:**
- Tavily API for web search and content extraction

### Current Date

The `get_current_date` tool provides the current date in various formats.

**Features:**
- Multiple date formats (YYYY-MM-DD, DD-MM-YYYY, MM-DD-YYYY, full text)
- Additional date information (day of week, day of year, week of year)
- Timezone-aware (UTC)

**API Dependencies:**
- None (uses Python's datetime module)

## Dependencies

TravelBuddy relies on the following key dependencies:

- **pydantic-ai**: For building the agent and tool framework
- **httpx**: For asynchronous HTTP requests
- **googlemaps**: For Google Maps API integration
- **requests**: For HTTP requests to weather and other APIs
- **gradio**: For the web interface
- **python-dotenv**: For environment variable management
- **tavily-python**: For web search capabilities

## Troubleshooting

### Common Issues

1. **API Key Errors**:
   - Ensure all required API keys are set in your environment variables
   - Check that the APIs are enabled in your Google Cloud Console

2. **Google Maps API Errors**:
   - "This API project is not authorized to use this API" - Enable the required APIs in Google Cloud Console
   - "REQUEST_DENIED" - Check API key permissions and billing status

3. **Weather Forecast Errors**:
   - "Error making request to OpenWeatherMap API" - Verify your API key and check API usage limits

4. **Gradio Interface Issues**:
   - If the interface doesn't load, check for port conflicts
   - Try running with `demo.launch(share=False)` to use only local access

### Logging

TravelBuddy uses Python's logging module to provide detailed logs. Check the logs for error messages and debugging information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

Planned improvements for TravelBuddy:

1. **Additional Data Sources**:
   - Flight booking API integration
   - Public transportation schedules
   - Event and activity recommendations

2. **User Experience**:
   - User profiles and preference storage
   - Trip history and favorites
   - Multi-language support

3. **Advanced Features**:
   - Budget calculation and expense tracking
   - Packing list generation
   - Travel document requirements
   - Health and safety information

4. **Technical Improvements**:
   - Caching for faster responses
   - Offline mode for basic functionality
   - Mobile application
