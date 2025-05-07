#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Weather API tool for the Personal Assistant.

This module implements a LangChain tool for retrieving weather information
using a weather API service.
"""

import requests
import logging
from typing import Optional, Dict, Any, Type

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from config import WEATHER_API_KEY, WEATHER_API_BASE_URL

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
    
    def _run(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """
        Get current weather information for a location.
        
        Args:
            location (str): The city or location to get weather for
            units (str): Units of measurement (metric or imperial)
            
        Returns:
            Dict[str, Any]: Weather information
        """
        try:
            # API parameters
            params = {
                "q": location,
                "appid": WEATHER_API_KEY,
                "units": units
            }
            
            # Make API request
            logger.info(f"Fetching weather for {location}")
            response = requests.get(WEATHER_API_BASE_URL, params=params)
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"Weather API error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return {
                    "error": True,
                    "message": f"Couldn't get weather for {location}",
                    "status_code": response.status_code
                }
            
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
                "error": False
            }
            
            logger.info(f"Successfully fetched weather for {location}")
            return weather_info
            
        except Exception as e:
            logger.error(f"Error in WeatherTool: {str(e)}")
            return {
                "error": True,
                "message": f"Error getting weather: {str(e)}",
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
        # In a real implementation, this would call a forecast API endpoint
        # For now, we'll return a placeholder message
        return {
            "error": True,
            "message": f"Forecast feature is not yet implemented. Would show {days} day forecast for {location}.",
            "location": location,
            "days": days
        }