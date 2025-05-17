from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timezone
import logging
import json
from pydantic_ai import RunContext, ModelRetry
from dependencies import TravelDependencies

# Configure logging for tools
logger = logging.getLogger(__name__)


async def get_transportation(
    ctx: RunContext[TravelDependencies],
    from_location: str,
    to_location: str,
    travel_date: str,
    mode: str = "mixed"
) -> List[Dict[str, Any]]:
    """Get transportation options between two locations.

    Args:
        ctx: The context with dependencies.
        from_location: Starting location.
        to_location: Destination location.
        travel_date: Date of travel in YYYY-MM-DD format.
        mode: Transportation mode (car, train, mixed).
    """
    logger.info(f"Fetching transportation options from {from_location} to {to_location} with mode {mode}")

    try:
        gmaps = ctx.deps.get_google_maps_client()
        if not gmaps:
            # Return dummy data if no API key
            return [{
                "type": "transportation",
                "title": f"Transportation options from {from_location} to {to_location}",
                "description": "Sample transportation options",
                "steps": [
                    f"Travel from {from_location} to {to_location}",
                    "Check local transportation websites for actual options",
                    f"Estimated travel time: 2-3 hours"
                ]
            }]

        transportation_options = []

        # Handle flight mode separately with a default message
        if mode == "flight":
            return [{
                "type": "transportation",
                "title": f"Flight options from {from_location} to {to_location}",
                "description": "Flight booking is currently not supported in the app",
                "steps": [
                    "Please check popular flight booking websites:",
                    "- Google Flights",
                    "- Skyscanner",
                    "- Kayak",
                    f"Search for flights from {from_location} to {to_location} for {travel_date}"
                ]
            }]

        # Define modes to check based on user preference
        if mode == "car":
            modes_to_check = [("driving", None)]  # Only check driving routes
        elif mode == "train":
            modes_to_check = [("transit", ["rail", "train"])]  # Only check train routes
        else:  # "mixed" or any other option
            modes_to_check = [
                ("transit", ["bus", "train", "subway"]),  # Public transit
                ("driving", None),  # Driving option
            ]

        for travel_mode, transit_modes in modes_to_check:
            try:
                # Configure the request based on mode
                params = {
                    "mode": travel_mode,
                    "alternatives": True,
                }
                if transit_modes:
                    params["transit_mode"] = transit_modes

                directions = gmaps.directions(
                    from_location,
                    to_location,
                    **params
                )

                for route in directions[:2]:  # Limit to 2 routes per mode
                    legs = route.get("legs", [])
                    if not legs:
                        continue

                    leg = legs[0]
                    steps = []
                    for step in leg.get("steps", [])[:5]:  # Limit to 5 steps
                        instruction = step.get("html_instructions", "").replace("<b>", "").replace("</b>", "").replace("<div>", " ").replace("</div>", "")
                        steps.append(instruction)

                    transportation_options.append({
                        "type": "transportation",
                        "title": f"{travel_mode.title()} from {from_location} to {to_location}",
                        "description": f"Duration: {leg.get('duration', {}).get('text', 'Unknown')}",
                        "steps": steps
                    })
            except Exception as e:
                logger.error(f"Error getting {travel_mode} directions: {str(e)}", exc_info=True)

        # If no options found, provide a helpful message
        if not transportation_options:
            return [{
                "type": "transportation",
                "title": f"No direct routes found from {from_location} to {to_location}",
                "description": "Consider checking alternative transportation methods",
                "steps": [
                    "Consider breaking your journey into smaller segments",
                    "Check with local transportation authorities",
                    "Consider alternative travel dates",
                    "Look for multi-modal transportation options"
                ]
            }]

        logger.info(f"Found {len(transportation_options)} transportation options")
        return transportation_options
    except Exception as e:
        logger.error(f"Error getting transportation info: {str(e)}", exc_info=True)
        return [{
            "type": "transportation",
            "title": f"Error finding transportation from {from_location} to {to_location}",
            "description": "Could not retrieve transportation options",
            "steps": [
                "Please try again later",
                "Consider checking directly with transportation providers"
            ]
        }]


async def get_weather_forecast(
    ctx: RunContext[TravelDependencies],
    location: str,
    date: str
) -> Dict[str, Any]:
    """Get weather forecast for a location on a specific date.

    Args:
        ctx: The context with dependencies.
        location: The location to get weather for.
        date: The date in YYYY-MM-DD format.
    """
    logger.info(f"Fetching weather forecast for {location} on {date}")

    # For now, return dummy data
    # In a real implementation, we would use the OpenWeatherMap API
    return {
        "location": location,
        "date": date,
        "temperature": "24°C",
        "condition": "Sunny",
        "humidity": "60%",
        "wind": "10 km/h"
    }


async def get_attractions(
    ctx: RunContext[TravelDependencies],
    location: str
) -> List[Dict[str, Any]]:
    """Get attractions for a location.

    Args:
        ctx: The context with dependencies.
        location: The location to get attractions for.
    """
    logger.info(f"Fetching attractions for {location}")

    try:
        tavily_client = ctx.deps.get_tavily_client()
        if not tavily_client:
            # Return dummy data if no API key
            return [
                {
                    "name": f"Famous Museum in {location}",
                    "description": "A world-renowned museum with extensive collections.",
                    "rating": 4.5,
                    "url": "https://example.com/museum"
                },
                {
                    "name": f"{location} Historical Site",
                    "description": "An important historical landmark.",
                    "rating": 4.3,
                    "url": "https://example.com/historical-site"
                }
            ]

        search_query = f"top tourist attractions in {location}"
        response = tavily_client.search(
            query=search_query,
            search_depth="advanced",
            include_images=True,
            include_raw_content=True
        )

        attractions = []
        for result in response.get("results", [])[:5]:  # Limit to 5 attractions
            attractions.append({
                "name": result.get("title", "Unknown Attraction"),
                "description": result.get("content", "No description available"),
                "url": result.get("url", ""),
                "image": result.get("image_url", ""),
                "location": location
            })

        logger.info(f"Found {len(attractions)} attractions for {location}")
        return attractions
    except Exception as e:
        logger.error(f"Error getting attractions: {str(e)}", exc_info=True)
        return [
            {
                "name": f"Popular Attraction in {location}",
                "description": "A must-visit attraction in the area.",
                "rating": 4.2,
                "url": "https://example.com/attraction"
            }
        ]


async def get_restaurants(
    ctx: RunContext[TravelDependencies],
    location: str
) -> List[Dict[str, Any]]:
    """Get restaurant recommendations for a location.

    Args:
        ctx: The context with dependencies.
        location: The location to get restaurants for.
    """
    logger.info(f"Fetching restaurants for {location}")

    try:
        gmaps = ctx.deps.get_google_maps_client()
        if not gmaps:
            # Return dummy data if no API key
            return [
                {
                    "name": f"Local Restaurant in {location}",
                    "description": "A popular local restaurant with great reviews.",
                    "cuisine": "Local",
                    "rating": 4.5
                },
                {
                    "name": f"Fine Dining in {location}",
                    "description": "An upscale dining experience.",
                    "cuisine": "International",
                    "rating": 4.7
                }
            ]

        # First, get the location coordinates
        geocode_result = gmaps.geocode(location)
        if not geocode_result:
            return []

        location_coords = geocode_result[0]['geometry']['location']
        lat = location_coords['lat']
        lng = location_coords['lng']

        # Search for restaurants
        places_result = gmaps.places_nearby(
            location=(lat, lng),
            radius=5000,  # 5km radius
            type='restaurant'
        )

        restaurants = []
        for place in places_result.get('results', [])[:5]:  # Limit to 5 restaurants
            # Get detailed information for each place
            detail_result = gmaps.place(place['place_id'], fields=['name', 'formatted_address', 'rating', 'price_level', 'website', 'formatted_phone_number'])
            detail = detail_result.get('result', {})

            restaurants.append({
                "name": detail.get('name', ''),
                "description": f"Located at: {detail.get('formatted_address', '')}",
                "url": detail.get('website', ''),
                "rating": detail.get('rating', 4.0),
                "price_level": detail.get('price_level', 2),
                "location": location
            })

        logger.info(f"Found {len(restaurants)} restaurants for {location}")
        return restaurants
    except Exception as e:
        logger.error(f"Error getting restaurants: {str(e)}", exc_info=True)
        return [
            {
                "name": f"Restaurant in {location}",
                "description": "A restaurant in the area.",
                "cuisine": "Various",
                "rating": 4.0
            }
        ]


async def get_hotels(
    ctx: RunContext[TravelDependencies],
    location: str,
    check_in: str
) -> List[Dict[str, Any]]:
    """Get hotel recommendations for a location.

    Args:
        ctx: The context with dependencies.
        location: The location to get hotels for.
        check_in: The check-in date in YYYY-MM-DD format.
    """
    logger.info(f"Fetching hotels for {location} with check-in on {check_in}")

    try:
        gmaps = ctx.deps.get_google_maps_client()
        if not gmaps:
            # Return dummy data if no API key
            return [
                {
                    "name": f"Luxury Hotel in {location}",
                    "description": "A 5-star hotel with excellent amenities.",
                    "rating": 4.8,
                    "amenities": ["Pool", "Spa", "Restaurant"]
                },
                {
                    "name": f"Budget Hotel in {location}",
                    "description": "An affordable option with good value.",
                    "rating": 4.0,
                    "amenities": ["Free WiFi", "Breakfast"]
                }
            ]

        # First, get the location coordinates
        geocode_result = gmaps.geocode(location)
        if not geocode_result:
            return []

        location_coords = geocode_result[0]['geometry']['location']
        lat = location_coords['lat']
        lng = location_coords['lng']

        # Search for hotels
        places_result = gmaps.places_nearby(
            location=(lat, lng),
            radius=5000,  # 5km radius
            type='lodging'
        )

        hotels = []
        for place in places_result.get('results', [])[:5]:  # Limit to 5 hotels
            # Get detailed information for each place
            detail_result = gmaps.place(place['place_id'], fields=['name', 'formatted_address', 'rating', 'price_level', 'website', 'formatted_phone_number'])
            detail = detail_result.get('result', {})

            hotels.append({
                "name": detail.get('name', ''),
                "description": f"Located at: {detail.get('formatted_address', '')}",
                "url": detail.get('website', ''),
                "rating": detail.get('rating', 4.0),
                "location": location,
                "amenities": [amenity.replace('_', ' ').title() for amenity in place.get('types', [])]
            })

        logger.info(f"Found {len(hotels)} hotels for {location}")
        return hotels
    except Exception as e:
        logger.error(f"Error getting hotels: {str(e)}", exc_info=True)
        return [
            {
                "name": f"Hotel in {location}",
                "description": "A hotel in the area.",
                "rating": 4.0,
                "amenities": ["WiFi", "Parking"]
            }
        ]


async def get_local_tips(
    ctx: RunContext[TravelDependencies],
    location: str
) -> List[Dict[str, Any]]:
    """Get local tips for a location.

    Args:
        ctx: The context with dependencies.
        location: The location to get local tips for.
    """
    logger.info(f"Fetching local tips for {location}")

    try:
        tavily_client = ctx.deps.get_tavily_client()
        if not tavily_client:
            # Return dummy data if no API key
            return [
                {
                    "title": f"Local Customs in {location}",
                    "content": "Respect local traditions and customs when visiting."
                },
                {
                    "title": f"Getting Around {location}",
                    "content": "Public transportation is efficient and affordable."
                }
            ]

        search_query = f"local tips and customs in {location}"
        response = tavily_client.search(
            query=search_query,
            search_depth="advanced",
            include_raw_content=True
        )

        tips = []
        for result in response.get("results", [])[:5]:  # Limit to 5 tips
            tips.append({
                "title": result.get("title", "Local Tip"),
                "content": result.get("content", "No content available"),
                "url": result.get("url", ""),
                "location": location
            })

        logger.info(f"Found {len(tips)} local tips for {location}")
        return tips
    except Exception as e:
        logger.error(f"Error getting local tips: {str(e)}", exc_info=True)
        return [
            {
                "title": f"Tip for Visiting {location}",
                "content": "Always check local weather before planning your day."
            }
        ]
