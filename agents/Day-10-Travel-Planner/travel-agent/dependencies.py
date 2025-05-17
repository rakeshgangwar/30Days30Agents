from dataclasses import dataclass
from typing import Optional
from httpx import AsyncClient
from googlemaps import Client as GoogleMapsClient
from tavily import TavilyClient


@dataclass
class TravelDependencies:
    """Dependencies for the travel agent."""
    client: AsyncClient
    openai_api_key: str
    google_maps_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    openweathermap_api_key: Optional[str] = None
    
    def get_google_maps_client(self) -> Optional[GoogleMapsClient]:
        """Get a Google Maps client if the API key is available."""
        if self.google_maps_api_key:
            return GoogleMapsClient(key=self.google_maps_api_key)
        return None
    
    def get_tavily_client(self) -> Optional[TavilyClient]:
        """Get a Tavily client if the API key is available."""
        if self.tavily_api_key:
            return TavilyClient(api_key=self.tavily_api_key)
        return None
