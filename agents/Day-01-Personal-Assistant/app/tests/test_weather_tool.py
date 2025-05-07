#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests for the weather tool of the Personal Assistant.
"""

import unittest
import os
from unittest.mock import patch, MagicMock

from app.tools.weather_tool import WeatherTool

class TestWeatherTool(unittest.TestCase):
    """Test cases for the weather tool."""

    def setUp(self):
        """Set up test environment."""
        # Set a dummy API key for testing
        os.environ["WEATHER_API_KEY"] = "fake_weather_api_key"

    @patch('app.tools.weather_tool.requests.get')
    def test_successful_weather_request(self, mock_get):
        """Test successful weather API request."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {
                "temp": 22.5,
                "feels_like": 23.0,
                "humidity": 65,
                "pressure": 1012
            },
            "weather": [
                {
                    "description": "scattered clouds",
                    "icon": "03d"
                }
            ],
            "wind": {
                "speed": 3.5
            }
        }
        mock_get.return_value = mock_response

        # Create weather tool
        weather_tool = WeatherTool()

        # Test the tool
        result = weather_tool._run(location="New York", units="metric")

        # Verify result structure and content
        self.assertFalse(result.get("error", True))
        self.assertEqual(result["location"], "New York")
        self.assertEqual(result["temperature"], 22.5)
        self.assertEqual(result["humidity"], 65)
        self.assertEqual(result["conditions"], "scattered clouds")
        self.assertEqual(result["unit"], "C")

    @patch('app.tools.weather_tool.requests.get')
    def test_api_error_handling(self, mock_get):
        """Test handling of API errors."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "City not found"
        mock_get.return_value = mock_response

        # Create weather tool
        weather_tool = WeatherTool()

        # Test the tool
        result = weather_tool._run(location="NonExistentCity", units="metric")

        # Verify error handling
        self.assertTrue(result.get("error", False))
        self.assertIn("message", result)
        self.assertIn("Geocoding API error", result["message"])
        # Status code might not be included in the response

    @patch('app.tools.weather_tool.requests.get')
    def test_exception_handling(self, mock_get):
        """Test handling of exceptions."""
        # Configure mock to raise an exception
        mock_get.side_effect = Exception("Test exception")

        # Create weather tool
        weather_tool = WeatherTool()

        # Test the tool
        result = weather_tool._run(location="New York", units="metric")

        # Verify exception handling
        self.assertTrue(result.get("error", False))
        self.assertIn("message", result)
        self.assertIn("Geocoding error", result["message"])

    @patch('app.tools.weather_tool.requests.get')
    def test_imperial_units(self, mock_get):
        """Test weather with imperial units."""
        # Configure mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {
                "temp": 72.5,
                "feels_like": 73.0,
                "humidity": 65,
                "pressure": 1012
            },
            "weather": [
                {
                    "description": "clear sky",
                    "icon": "01d"
                }
            ],
            "wind": {
                "speed": 8.5
            }
        }
        mock_get.return_value = mock_response

        # Create weather tool
        weather_tool = WeatherTool()

        # Test the tool with imperial units
        result = weather_tool._run(location="New York", units="imperial")

        # Verify result
        self.assertFalse(result.get("error", True))
        self.assertEqual(result["unit"], "F")
        self.assertEqual(result["temperature"], 72.5)

if __name__ == "__main__":
    unittest.main()