"""
Task Automation Agent - API Tool

This module provides a tool for making API requests.
"""

import json
from typing import Dict, Any, Optional
import requests
from pydantic_ai.tools import Tool

class ApiTool(Tool):
    """
    Tool for making API requests.
    
    This tool provides methods for making HTTP requests to APIs.
    """
    
    name = "ApiTool"
    description = "Tool for making API requests (GET, POST, PUT, DELETE)."
    
    def make_get_request(self, url: str, params: Optional[Dict[str, Any]] = None, 
                         headers: Optional[Dict[str, str]] = None) -> str:
        """
        Make a GET request to an API.
        
        Args:
            url: The URL to make the request to
            params: Optional query parameters
            headers: Optional request headers
            
        Returns:
            Response from the API as a string
        """
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # Raise an exception for 4XX/5XX responses
            
            # Try to parse as JSON, fall back to text if not JSON
            try:
                return json.dumps(response.json(), indent=2)
            except:
                return response.text
        except Exception as e:
            return f"Error making GET request to {url}: {str(e)}"
    
    def make_post_request(self, url: str, data: Optional[Dict[str, Any]] = None,
                          json_data: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, str]] = None) -> str:
        """
        Make a POST request to an API.
        
        Args:
            url: The URL to make the request to
            data: Optional form data
            json_data: Optional JSON data
            headers: Optional request headers
            
        Returns:
            Response from the API as a string
        """
        try:
            response = requests.post(url, data=data, json=json_data, headers=headers)
            response.raise_for_status()
            
            try:
                return json.dumps(response.json(), indent=2)
            except:
                return response.text
        except Exception as e:
            return f"Error making POST request to {url}: {str(e)}"
    
    def make_put_request(self, url: str, data: Optional[Dict[str, Any]] = None,
                         json_data: Optional[Dict[str, Any]] = None,
                         headers: Optional[Dict[str, str]] = None) -> str:
        """
        Make a PUT request to an API.
        
        Args:
            url: The URL to make the request to
            data: Optional form data
            json_data: Optional JSON data
            headers: Optional request headers
            
        Returns:
            Response from the API as a string
        """
        try:
            response = requests.put(url, data=data, json=json_data, headers=headers)
            response.raise_for_status()
            
            try:
                return json.dumps(response.json(), indent=2)
            except:
                return response.text
        except Exception as e:
            return f"Error making PUT request to {url}: {str(e)}"
    
    def make_delete_request(self, url: str, headers: Optional[Dict[str, str]] = None) -> str:
        """
        Make a DELETE request to an API.
        
        Args:
            url: The URL to make the request to
            headers: Optional request headers
            
        Returns:
            Response from the API as a string
        """
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            
            try:
                return json.dumps(response.json(), indent=2)
            except:
                return response.text
        except Exception as e:
            return f"Error making DELETE request to {url}: {str(e)}"
