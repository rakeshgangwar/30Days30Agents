"""
Base platform client module.

This module provides a base class for all platform clients.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class BasePlatformClient(ABC):
    """
    Base class for all social media platform clients.
    
    This abstract class defines the interface that all platform clients must implement.
    """
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate with the platform using provided credentials.
        
        Args:
            credentials: Dictionary containing the necessary credentials for authentication.
            
        Returns:
            True if authentication was successful, False otherwise.
        """
        pass
    
    @abstractmethod
    def post_content(self, content: str, media_urls: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Post content to the platform.
        
        Args:
            content: The text content to post.
            media_urls: Optional list of media URLs to attach to the post.
            **kwargs: Additional platform-specific parameters.
            
        Returns:
            Dictionary containing information about the created post, including its ID.
        """
        pass
    
    @abstractmethod
    def get_interactions(self, since_id: Optional[str] = None, count: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent interactions from the platform.
        
        Args:
            since_id: Optional ID to get interactions newer than this ID.
            count: Maximum number of interactions to retrieve.
            
        Returns:
            List of interaction objects from the platform.
        """
        pass
    
    @abstractmethod
    def respond_to_interaction(self, interaction_id: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        Respond to an interaction.
        
        Args:
            interaction_id: The ID of the interaction to respond to.
            content: The response content.
            **kwargs: Additional platform-specific parameters.
            
        Returns:
            Dictionary containing information about the created response.
        """
        pass

    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get information about the connected account.
        
        Returns:
            Dictionary containing information about the account.
        """
        pass