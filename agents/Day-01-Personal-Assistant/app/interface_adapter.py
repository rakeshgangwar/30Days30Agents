#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface Adapter for Personal Assistant.

This module provides a uniform API layer between interfaces (Streamlit, Telegram)
and the core agent, handling message standardization and response formatting.
"""

import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterfaceAdapter:
    """
    Provides a uniform API layer between interfaces and core agent.
    
    This adapter:
    1. Standardizes input from different sources
    2. Formats responses for different targets
    3. Manages session information
    """
    
    def __init__(self):
        """Initialize the interface adapter."""
        self.sessions = {}  # Maps session_id to user data
    
    def standardize_input(self, raw_input: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Convert interface-specific input to standard format.
        
        Args:
            raw_input (Dict[str, Any]): The raw input from the interface
            source (str): The source interface ("telegram" or "streamlit")
            
        Returns:
            Dict[str, Any]: Standardized input
        """
        logger.info(f"Standardizing input from {source}")
        
        if source == "telegram":
            return self._process_telegram_input(raw_input)
        elif source == "streamlit":
            return self._process_streamlit_input(raw_input)
        else:
            logger.warning(f"Unknown source: {source}")
            return {"message": str(raw_input), "user_id": "unknown"}
    
    def _process_telegram_input(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input from Telegram.
        
        Args:
            raw_input (Dict[str, Any]): Telegram update object
            
        Returns:
            Dict[str, Any]: Standardized input
        """
        # Extract message and user info from Telegram update
        message = raw_input.get("message", {})
        user = message.get("from", {})
        
        # Handle commands
        text = message.get("text", "")
        is_command = text.startswith("/")
        command = text[1:] if is_command else None
        
        return {
            "message": text,
            "user_id": str(user.get("id")),
            "username": user.get("username"),
            "is_command": is_command,
            "command": command,
            "platform_data": raw_input
        }
    
    def _process_streamlit_input(self, raw_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input from Streamlit.
        
        Args:
            raw_input (Dict[str, Any]): Input from Streamlit
            
        Returns:
            Dict[str, Any]: Standardized input
        """
        # For Streamlit, we expect a simpler structure
        return {
            "message": raw_input.get("message", ""),
            "user_id": raw_input.get("session_id", "unknown"),
            "is_command": False,
            "command": None,
            "platform_data": raw_input
        }
    
    def format_output(self, response: Dict[str, Any], target: str) -> Dict[str, Any]:
        """
        Format response for specific interface.
        
        Args:
            response (Dict[str, Any]): The standardized response
            target (str): The target interface ("telegram" or "streamlit")
            
        Returns:
            Dict[str, Any]: Formatted response
        """
        logger.info(f"Formatting output for {target}")
        
        if target == "telegram":
            return self._format_for_telegram(response)
        elif target == "streamlit":
            return self._format_for_streamlit(response)
        else:
            logger.warning(f"Unknown target: {target}")
            return {"text": response.get("text", "")}
    
    def _format_for_telegram(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format response for Telegram.
        
        Args:
            response (Dict[str, Any]): The standardized response
            
        Returns:
            Dict[str, Any]: Telegram-formatted response
        """
        # Basic text response
        result = {
            "text": response.get("text", ""),
            "parse_mode": "Markdown"
        }
        
        # Handle additional response types
        if "weather" in response:
            weather = response["weather"]
            # Format weather data nicely for Telegram
            result["text"] = f"*Weather in {weather.get('location')}*\n" \
                            f"🌡️ Temperature: {weather.get('temperature')}°{weather.get('unit', 'C')}\n" \
                            f"💧 Humidity: {weather.get('humidity')}%\n" \
                            f"🌤️ Conditions: {weather.get('conditions')}"
        
        elif "reminder" in response:
            reminder = response["reminder"]
            # Format reminder confirmation
            result["text"] = f"✅ *Reminder set*\n" \
                            f"I'll remind you to: {reminder.get('text')}\n" \
                            f"When: {reminder.get('time')}"
        
        return result
    
    def _format_for_streamlit(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format response for Streamlit.
        
        Args:
            response (Dict[str, Any]): The standardized response
            
        Returns:
            Dict[str, Any]: Streamlit-formatted response
        """
        # Basic text response
        result = {
            "text": response.get("text", ""),
            "type": "text"
        }
        
        # Handle additional response types
        if "weather" in response:
            weather = response["weather"]
            # Include structured data for potential visualization
            result["type"] = "weather"
            result["data"] = weather
        
        elif "reminder" in response:
            reminder = response["reminder"]
            # Include structured data
            result["type"] = "reminder"
            result["data"] = reminder
        
        return result
    
    def get_session(self, user_id: str, platform: str) -> Dict[str, Any]:
        """
        Get or create a session for a user.
        
        Args:
            user_id (str): The user's ID
            platform (str): The platform the user is on
            
        Returns:
            Dict[str, Any]: Session data
        """
        session_key = f"{platform}:{user_id}"
        
        if session_key not in self.sessions:
            self.sessions[session_key] = {
                "user_id": user_id,
                "platform": platform,
                "data": {}
            }
        
        return self.sessions[session_key]
    
    def update_session(self, user_id: str, platform: str, data: Dict[str, Any]) -> None:
        """
        Update a user's session data.
        
        Args:
            user_id (str): The user's ID
            platform (str): The platform the user is on
            data (Dict[str, Any]): The data to update
        """
        session = self.get_session(user_id, platform)
        session["data"].update(data)