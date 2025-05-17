from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timezone, timedelta
import logging
import json
import requests
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
        api_key = ctx.deps.google_maps_api_key
        if not api_key:
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

        # We'll use the Distance Matrix API directly with location names
        # This is part of the Maps Platform and is more likely to be enabled

        # Define travel modes for the fallback approach
        if mode == "car":
            travel_mode = "driving"
        elif mode == "train":
            travel_mode = "transit"
        else:  # "mixed" or any other option
            travel_mode = "driving"  # Default to driving for mixed mode

        transportation_options = []

        try:
            # Use the Distance Matrix API which is part of the Places API suite
            distance_matrix_url = "https://maps.googleapis.com/maps/api/distancematrix/json"

            # Set up parameters
            params = {
                "origins": from_location,
                "destinations": to_location,
                "mode": travel_mode,
                "key": api_key,
                "units": "metric",
                "language": "en"
            }

            # Make the API request
            response = requests.get(distance_matrix_url, params=params)
            response.raise_for_status()
            route_data = response.json()

            # Check if we got valid results
            if route_data.get("status") == "OK":
                rows = route_data.get("rows", [])
                if rows and rows[0].get("elements"):
                    element = rows[0]["elements"][0]

                    if element.get("status") == "OK":
                        # Extract duration and distance
                        duration_text = element.get("duration", {}).get("text", "Unknown duration")
                        distance_text = element.get("distance", {}).get("text", "Unknown distance")

                        # Create steps based on the information we have
                        steps = [
                            f"Travel from {from_location} to {to_location}",
                            f"Estimated travel time: {duration_text}",
                            f"Estimated distance: {distance_text}"
                        ]

                        # Add additional information based on travel mode
                        if travel_mode == "driving":
                            steps.append("Travel by car following the fastest route")
                        elif travel_mode == "transit":
                            steps.append("Travel by public transportation")
                            steps.append("Check local transit schedules for exact timings")

                        # Add the route to transportation options
                        transportation_options.append({
                            "type": "transportation",
                            "title": f"{travel_mode.title()} from {from_location} to {to_location}",
                            "description": f"Duration: {duration_text}, Distance: {distance_text}",
                            "steps": steps
                        })

            # If we're in mixed mode, try to get transit options as well
            if mode == "mixed" and travel_mode == "driving":
                # Try transit as well
                params["mode"] = "transit"

                try:
                    transit_response = requests.get(distance_matrix_url, params=params)
                    transit_response.raise_for_status()
                    transit_data = transit_response.json()

                    if transit_data.get("status") == "OK":
                        rows = transit_data.get("rows", [])
                        if rows and rows[0].get("elements"):
                            element = rows[0]["elements"][0]

                            if element.get("status") == "OK":
                                # Extract duration and distance
                                duration_text = element.get("duration", {}).get("text", "Unknown duration")
                                distance_text = element.get("distance", {}).get("text", "Unknown distance")

                                # Create steps for transit
                                steps = [
                                    f"Travel from {from_location} to {to_location} by public transportation",
                                    f"Estimated travel time: {duration_text}",
                                    f"Estimated distance: {distance_text}",
                                    "Check local transit schedules for exact timings",
                                    "Consider checking transit apps for real-time updates"
                                ]

                                # Add the transit route to transportation options
                                transportation_options.append({
                                    "type": "transportation",
                                    "title": f"Transit from {from_location} to {to_location}",
                                    "description": f"Duration: {duration_text}, Distance: {distance_text}",
                                    "steps": steps
                                })
                except Exception as e:
                    logger.error(f"Error getting transit directions: {str(e)}", exc_info=True)
        except Exception as e:
            logger.error(f"Error getting directions: {str(e)}", exc_info=True)

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

    try:
        # Check if OpenWeatherMap API key is available
        api_key = ctx.deps.openweathermap_api_key
        if not api_key:
            logger.warning("OpenWeatherMap API key not available, returning dummy data")
            return {
                "location": location,
                "date": date,
                "temperature": "24°C",
                "condition": "Sunny",
                "humidity": "60%",
                "wind": "10 km/h"
            }

        # Parse the date string to a datetime object
        target_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        current_date = datetime.now(timezone.utc)

        # Determine if we need current weather or forecast
        days_difference = (target_date.date() - current_date.date()).days

        # Base URL for OpenWeatherMap API
        base_url = "https://api.openweathermap.org/data/2.5"

        if days_difference == 0:
            # Get current weather
            endpoint = f"{base_url}/weather"
            params = {
                "q": location,
                "appid": api_key,
                "units": "metric"  # Use metric units (Celsius)
            }

            response = requests.get(endpoint, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()

            # Extract weather data
            weather_data = {
                "location": location,
                "date": date,
                "temperature": f"{data['main']['temp']:.1f}°C",
                "condition": data['weather'][0]['description'].capitalize(),
                "humidity": f"{data['main']['humidity']}%",
                "wind": f"{data['wind']['speed']:.1f} m/s"
            }

        elif 0 < days_difference <= 5:  # OWM free tier supports 5-day forecast
            # Get 5-day forecast with 3-hour intervals
            endpoint = f"{base_url}/forecast"
            params = {
                "q": location,
                "appid": api_key,
                "units": "metric"  # Use metric units (Celsius)
            }

            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()

            # Find the forecast closest to the target date
            # Set the target time to noon on the target date
            target_datetime = target_date.replace(hour=12, minute=0, second=0)
            target_timestamp = int(target_datetime.timestamp())

            # Find the forecast item closest to the target time
            closest_forecast = None
            min_time_diff = float('inf')

            for forecast_item in data['list']:
                forecast_time = forecast_item['dt']
                time_diff = abs(forecast_time - target_timestamp)

                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    closest_forecast = forecast_item

            if closest_forecast:
                # Extract weather data from the closest forecast
                weather_data = {
                    "location": location,
                    "date": date,
                    "temperature": f"{closest_forecast['main']['temp']:.1f}°C",
                    "condition": closest_forecast['weather'][0]['description'].capitalize(),
                    "humidity": f"{closest_forecast['main']['humidity']}%",
                    "wind": f"{closest_forecast['wind']['speed']:.1f} m/s"
                }
            else:
                # This should not happen, but just in case
                return {
                    "location": location,
                    "date": date,
                    "temperature": "N/A",
                    "condition": "No forecast data available for the specified date",
                    "humidity": "N/A",
                    "wind": "N/A"
                }

        else:
            # Date is too far in the future for free API
            logger.warning(f"Date {date} is beyond the 5-day forecast limit of the free OpenWeatherMap API")
            return {
                "location": location,
                "date": date,
                "temperature": "N/A",
                "condition": "Forecast unavailable for dates beyond 5 days",
                "humidity": "N/A",
                "wind": "N/A"
            }

        logger.info(f"Successfully retrieved weather forecast for {location} on {date}")
        return weather_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request to OpenWeatherMap API: {str(e)}", exc_info=True)
        return {
            "location": location,
            "date": date,
            "temperature": "N/A",
            "condition": f"Error retrieving forecast: {str(e)}",
            "humidity": "N/A",
            "wind": "N/A"
        }
    except Exception as e:
        logger.error(f"Error getting weather forecast: {str(e)}", exc_info=True)
        return {
            "location": location,
            "date": date,
            "temperature": "N/A",
            "condition": f"Error retrieving forecast: {str(e)}",
            "humidity": "N/A",
            "wind": "N/A"
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


async def get_current_date(
    ctx: RunContext[TravelDependencies],  # ctx is required by the framework but not used in this function
    format: str = "YYYY-MM-DD"
) -> Dict[str, str]:
    """Get the current date in the specified format.

    Args:
        ctx: The context with dependencies.
        format: The format to return the date in. Options:
               - "YYYY-MM-DD" (default): Returns date as 2024-05-15
               - "DD-MM-YYYY": Returns date as 15-05-2024
               - "MM-DD-YYYY": Returns date as 05-15-2024
               - "full": Returns full date with day name, e.g., "Wednesday, May 15, 2024"

    Returns:
        A dictionary containing the current date in the requested format,
        along with additional date information.
    """
    logger.info(f"Getting current date in format: {format}")

    try:
        # Get current date in UTC
        current_date = datetime.now(timezone.utc)

        # Format the date according to the requested format
        if format == "YYYY-MM-DD":
            formatted_date = current_date.strftime("%Y-%m-%d")
        elif format == "DD-MM-YYYY":
            formatted_date = current_date.strftime("%d-%m-%Y")
        elif format == "MM-DD-YYYY":
            formatted_date = current_date.strftime("%m-%d-%Y")
        elif format == "full":
            formatted_date = current_date.strftime("%A, %B %d, %Y")
        else:
            # Default to ISO format if an unknown format is requested
            formatted_date = current_date.strftime("%Y-%m-%d")
            logger.warning(f"Unknown date format '{format}', defaulting to YYYY-MM-DD")

        # Calculate day of week, day of year, and week of year
        day_of_week = current_date.strftime("%A")
        day_of_year = current_date.strftime("%j")
        week_of_year = current_date.strftime("%U")

        # Return comprehensive date information
        return {
            "date": formatted_date,
            "iso_date": current_date.strftime("%Y-%m-%d"),
            "day_of_week": day_of_week,
            "day_of_year": day_of_year,
            "week_of_year": week_of_year,
            "month": current_date.strftime("%B"),
            "year": current_date.strftime("%Y"),
            "timestamp": current_date.isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting current date: {str(e)}", exc_info=True)
        return {
            "date": "Error retrieving date",
            "error": str(e)
        }
