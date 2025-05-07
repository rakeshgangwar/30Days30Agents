#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weather API tool for the Personal Assistant.

This module implements a LangChain tool for retrieving weather information
using a weather API service with a backup API option.
"""

import requests
import logging
from typing import Optional, Dict, Any, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from config import WEATHER_API_KEY, WEATHER_API_BASE_URL, OPEN_METEO_API_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherInput(BaseModel):
    """Input schema for the weather tool."""
    location: str = Field(description="The city or location to get weather for")
    units: str = Field(default="metric", description="Units of measurement (metric or imperial)")

class WeatherTool(BaseTool):
    """Tool for fetching weather information."""
    
    name: str = "weather_tool"
    description: str = "Useful for getting weather information for a specific location"
    args_schema: Type[BaseModel] = WeatherInput
    
    def _get_coordinates_from_location(self, location: str) -> Dict[str, Any]:
        """
        Get latitude and longitude for a location using OpenMeteo Geocoding API.
        
        Args:
            location (str): The city or location name
            
        Returns:
            Dict[str, Any]: Dictionary with lat, lon and name if successful, or error information
        """
        try:
            # Geocoding API endpoint
            geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {"name": location, "count": 1, "language": "en", "format": "json"}
            
            response = requests.get(geocoding_url, params=params)
            
            if response.status_code != 200:
                return {"error": True, "message": f"Geocoding API error: {response.status_code}"}
                
            data = response.json()
            
            if not data.get("results"):
                return {"error": True, "message": f"Location '{location}' not found"}
                
            result = data["results"][0]
            return {
                "error": False,
                "lat": result["latitude"],
                "lon": result["longitude"],
                "name": result["name"],
                "country": result.get("country", "")
            }
            
        except Exception as e:
            logger.error(f"Error in geocoding: {str(e)}")
            return {"error": True, "message": f"Geocoding error: {str(e)}"}
    
    def _get_weather_from_open_meteo(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get weather information using Open-Meteo API (backup service).
        
        Args:
            location (str): The city or location to get weather for
            units (str): Units of measurement (metric or imperial)
            
        Returns:
            Dict[str, Any]: Weather information
        """
        try:
            # First get coordinates
            coords = self._get_coordinates_from_location(location)
            
            if coords.get("error"):
                return coords
                
            # Set up parameters for Open-Meteo API
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", 
                           "weather_code", "pressure_msl", "wind_speed_10m"],
                "temperature_unit": "fahrenheit" if units == "imperial" else "celsius"
            }
            
            logger.info(f"Fetching weather from Open-Meteo for {coords['name']}")
            response = requests.get(OPEN_METEO_API_URL, params=params)
            
            if response.status_code != 200:
                return {
                    "error": True,
                    "message": f"Open-Meteo API error: {response.status_code}",
                    "location": location
                }
                
            data = response.json()
            
            # Map weather codes to conditions
            # Based on WMO Weather interpretation codes (WW)
            weather_codes = {
                0: "Clear sky",
                1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Fog", 48: "Depositing rime fog",
                51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
                61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
                77: "Snow grains",
                80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
                85: "Slight snow showers", 86: "Heavy snow showers",
                95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
            }
            
            weather_code = data["current"]["weather_code"]
            conditions = weather_codes.get(weather_code, "Unknown")
            
            # Extract relevant information
            weather_info = {
                "location": f"{coords['name']}, {coords['country']}",
                "temperature": data["current"]["temperature_2m"],
                "feels_like": data["current"]["apparent_temperature"],
                "humidity": data["current"]["relative_humidity_2m"],
                "pressure": data["current"]["pressure_msl"],
                "conditions": conditions,
                "precipitation": data["current"]["precipitation"],
                "wind_speed": data["current"]["wind_speed_10m"],
                "unit": "F" if units == "imperial" else "C",
                "error": False,
                "source": "Open-Meteo API (backup)"
            }
            
            logger.info(f"Successfully fetched weather from Open-Meteo for {coords['name']}")
            return weather_info
            
        except Exception as e:
            logger.error(f"Error in Open-Meteo weather: {str(e)}")
            return {
                "error": True,
                "message": f"Error getting weather from backup service: {str(e)}",
                "location": location
            }
    
    def _run(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get current weather information for a location.
        Will try OpenWeather API first, then fall back to Open-Meteo if needed.
        
        Args:
            location (str): The city or location to get weather for
            units (str): Units of measurement (metric or imperial)
            
        Returns:
            Dict[str, Any]: Weather information
        """
        try:
            # Only try OpenWeather if API key is available
            if WEATHER_API_KEY:
                # API parameters
                params = {
                    "q": location,
                    "appid": WEATHER_API_KEY,
                    "units": units
                }
                
                # Make API request
                logger.info(f"Fetching weather from OpenWeather for {location}")
                response = requests.get(WEATHER_API_BASE_URL, params=params)
                
                # Check for errors
                if response.status_code == 200:
                    # Parse response
                    data = response.json()
                    
                    # Extract relevant information
                    weather_info = {
                        "location": location,
                        "temperature": data["main"]["temp"],
                        "feels_like": data["main"]["feels_like"],
                        "humidity": data["main"]["humidity"],
                        "pressure": data["main"]["pressure"],
                        "conditions": data["weather"][0]["description"],
                        "icon": data["weather"][0]["icon"],
                        "wind_speed": data["wind"]["speed"],
                        "unit": "C" if units == "metric" else "F",
                        "error": False,
                        "source": "OpenWeather API"
                    }
                    
                    logger.info(f"Successfully fetched weather from OpenWeather for {location}")
                    return weather_info
                else:
                    error_msg = f"OpenWeather API error: {response.status_code}, {response.text}"
                    logger.warning(error_msg)
                    logger.info("Falling back to Open-Meteo API")
            else:
                logger.warning("No OpenWeather API key available, using Open-Meteo API")
                
            # If we get here, either there was an error with OpenWeather or no API key
            # Try the backup service
            return self._get_weather_from_open_meteo(location, units)
            
        except Exception as e:
            logger.error(f"Error in WeatherTool: {str(e)}")
            # Try backup on any exception
            logger.info("Trying backup weather service due to exception")
            try:
                return self._get_weather_from_open_meteo(location, units)
            except Exception as backup_e:
                logger.error(f"Backup weather service also failed: {str(backup_e)}")
                return {
                    "error": True,
                    "message": f"Error getting weather from both services: {str(e)}",
                    "location": location
                }
    
    def _arun(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """Async implementation of the weather tool."""
        # This is just a placeholder - for actual async implementation,
        # we would use aiohttp or similar library
        return self._run(location, units)


class ForecastInput(BaseModel):
    """Input schema for the forecast tool."""
    location: str = Field(description="The city or location to get forecast for")
    days: int = Field(default=5, description="Number of days for the forecast (1-7)")
    units: str = Field(default="metric", description="Units of measurement (metric or imperial)")

class ForecastTool(BaseTool):
    """Tool for fetching weather forecasts."""
    
    name: str = "forecast_tool"
    description: str = "Useful for getting weather forecast for the next few days"
    args_schema: Type[BaseModel] = ForecastInput
    
    def _get_coordinates_from_location(self, location: str) -> Dict[str, Any]:
        """Get coordinates using Open-Meteo Geocoding API."""
        try:
            geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
            params = {"name": location, "count": 1, "language": "en", "format": "json"}
            
            response = requests.get(geocoding_url, params=params)
            
            if response.status_code != 200:
                return {"error": True, "message": f"Geocoding API error: {response.status_code}"}
                
            data = response.json()
            
            if not data.get("results"):
                return {"error": True, "message": f"Location '{location}' not found"}
                
            result = data["results"][0]
            return {
                "error": False,
                "lat": result["latitude"],
                "lon": result["longitude"],
                "name": result["name"],
                "country": result.get("country", "")
            }
            
        except Exception as e:
            logger.error(f"Error in geocoding: {str(e)}")
            return {"error": True, "message": f"Geocoding error: {str(e)}"}
    
    def _get_forecast_from_open_meteo(self, location: str, days: int = 5, units: str = "metric") -> Dict[str, Any]:
        """Get forecast using Open-Meteo API."""
        try:
            # First get coordinates
            coords = self._get_coordinates_from_location(location)
            
            if coords.get("error"):
                return coords
                
            # Limit days to 1-7 range
            days = max(1, min(days, 7))
                
            # Set up parameters for Open-Meteo API
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", 
                         "precipitation_sum", "precipitation_probability_max"],
                "timezone": "auto",
                "forecast_days": days,
                "temperature_unit": "fahrenheit" if units == "imperial" else "celsius"
            }
            
            logger.info(f"Fetching {days}-day forecast from Open-Meteo for {coords['name']}")
            response = requests.get(OPEN_METEO_API_URL, params=params)
            
            if response.status_code != 200:
                return {
                    "error": True,
                    "message": f"Open-Meteo API error: {response.status_code}",
                    "location": location
                }
                
            data = response.json()
            
            # Map weather codes to conditions
            weather_codes = {
                0: "Clear sky",
                1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Fog", 48: "Depositing rime fog",
                51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
                61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
                77: "Snow grains",
                80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
                85: "Slight snow showers", 86: "Heavy snow showers",
                95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
            }
            
            # Process daily forecast
            daily_forecasts = []
            for i in range(days):
                weather_code = data["daily"]["weather_code"][i]
                conditions = weather_codes.get(weather_code, "Unknown")
                
                daily_forecasts.append({
                    "date": data["daily"]["time"][i],
                    "conditions": conditions,
                    "max_temp": data["daily"]["temperature_2m_max"][i],
                    "min_temp": data["daily"]["temperature_2m_min"][i],
                    "precipitation": data["daily"]["precipitation_sum"][i],
                    "precipitation_probability": data["daily"]["precipitation_probability_max"][i]
                })
            
            forecast_info = {
                "location": f"{coords['name']}, {coords['country']}",
                "days": days,
                "unit": "F" if units == "imperial" else "C",
                "forecast": daily_forecasts,
                "error": False,
                "source": "Open-Meteo API"
            }
            
            logger.info(f"Successfully fetched forecast from Open-Meteo for {coords['name']}")
            return forecast_info
            
        except Exception as e:
            logger.error(f"Error in Open-Meteo forecast: {str(e)}")
            return {
                "error": True,
                "message": f"Error getting forecast: {str(e)}",
                "location": location,
                "days": days
            }
    
    def _run(self, location: str, days: int = 5, units: str = "metric") -> Dict[str, Any]:
        """
        Get weather forecast for a location.
        
        Args:
            location (str): The city or location to get forecast for
            days (int): Number of days for the forecast (1-7)
            units (str): Units of measurement (metric or imperial)
            
        Returns:
            Dict[str, Any]: Forecast information
        """
        # We'll implement the forecast using Open-Meteo API
        return self._get_forecast_from_open_meteo(location, days, units)