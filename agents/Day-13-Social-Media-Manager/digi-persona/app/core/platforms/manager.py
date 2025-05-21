"""
Platform manager module.

This module provides a manager for handling multiple platform clients.
"""

import logging
from typing import Dict, Any, List, Optional, Type

from sqlalchemy.orm import Session

from app.core.platforms.base import BasePlatformClient
from app.core.platforms.twitter import TwitterClient
from app.core.platforms.linkedin import LinkedInClient
from app.core.platforms.bluesky import BlueskyClient
from app.db.models.platform import PlatformConnection
from app.core.personas.context import persona_context

logger = logging.getLogger(__name__)

class PlatformManager:
    """
    Manager for platform clients.
    
    This class manages platform clients and provides a unified interface
    for working with multiple social media platforms.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the platform manager.
        
        Args:
            db: Database session.
        """
        self.db = db
        self.platform_clients: Dict[str, Dict[int, BasePlatformClient]] = {
            "twitter": {},
            "linkedin": {},
            "bluesky": {},
        }
    
    def get_client_class(self, platform_name: str) -> Type[BasePlatformClient]:
        """
        Get the client class for a platform.
        
        Args:
            platform_name: Name of the platform.
            
        Returns:
            The platform client class.
            
        Raises:
            ValueError: If the platform is not supported.
        """
        platform_name_lower = platform_name.lower()
        if platform_name_lower == "twitter":
            return TwitterClient
        elif platform_name_lower == "linkedin":
            return LinkedInClient
        elif platform_name_lower == "bluesky":
            return BlueskyClient
        else:
            raise ValueError(f"Unsupported platform: {platform_name}")
    
    def get_client(self, platform_name: str, persona_id: Optional[int] = None) -> BasePlatformClient:
        """
        Get a platform client for a specific persona.
        
        Args:
            platform_name: Name of the platform.
            persona_id: ID of the persona to get client for. If None, uses current persona context.
            
        Returns:
            Platform client.
            
        Raises:
            ValueError: If the platform or platform connection is not found.
        """
        platform_name_lower = platform_name.lower()
        
        # Get persona ID from context if not provided
        if persona_id is None:
            persona_id = persona_context.require_persona()
        
        # Check if we already have an initialized client for this platform and persona
        if platform_name_lower in self.platform_clients and persona_id in self.platform_clients[platform_name_lower]:
            return self.platform_clients[platform_name_lower][persona_id]
            
        # Get platform connection from database
        platform_conn = self.db.query(PlatformConnection).filter(
            PlatformConnection.persona_id == persona_id,
            PlatformConnection.platform_name.ilike(platform_name_lower),
            PlatformConnection.is_active == True
        ).first()
        
        if not platform_conn:
            raise ValueError(f"No active {platform_name} connection found for persona {persona_id}")
        
        # Create and authenticate client
        client_class = self.get_client_class(platform_name_lower)
        client = client_class()
        
        # Get credentials from platform connection
        credentials = {
            # Extract platform-specific credentials from the stored credentials
            **platform_conn.credentials
        }
        
        # Authenticate the client
        success = client.authenticate(credentials)
        
        if not success:
            raise ValueError(f"Failed to authenticate {platform_name} client for persona {persona_id}")
            
        # Store client for reuse
        if platform_name_lower not in self.platform_clients:
            self.platform_clients[platform_name_lower] = {}
            
        self.platform_clients[platform_name_lower][persona_id] = client
        
        return client
    
    def connect_platform(self, persona_id: int, platform_name: str, credentials: Dict[str, Any], username: str) -> PlatformConnection:
        """
        Connect a platform for a persona.
        
        Args:
            persona_id: ID of the persona.
            platform_name: Name of the platform.
            credentials: Platform credentials.
            username: Username on the platform.
            
        Returns:
            Created platform connection.
            
        Raises:
            ValueError: If authentication fails.
        """
        platform_name_lower = platform_name.lower()
        
        # Create client and authenticate
        client_class = self.get_client_class(platform_name_lower)
        client = client_class()
        
        # Try to authenticate
        success = client.authenticate(credentials)
        
        if not success:
            raise ValueError(f"Failed to authenticate {platform_name} client with provided credentials")
        
        # Get account info to verify connection and extract platform-specific identifier
        account_info = client.get_account_info()
        platform_id = account_info.get('id') or account_info.get('did') or username
        
        # Check if connection already exists
        existing_conn = self.db.query(PlatformConnection).filter(
            PlatformConnection.persona_id == persona_id,
            PlatformConnection.platform_name.ilike(platform_name_lower)
        ).first()
        
        if existing_conn:
            # Update existing connection
            existing_conn.credentials = credentials
            existing_conn.username = username
            existing_conn.platform_id = platform_id
            existing_conn.is_active = True
            existing_conn.platform_metadata = account_info
            self.db.commit()
            self.db.refresh(existing_conn)
            platform_conn = existing_conn
        else:
            # Create new connection
            platform_conn = PlatformConnection(
                persona_id=persona_id,
                platform_name=platform_name_lower,
                platform_id=platform_id,
                username=username,
                credentials=credentials,
                is_active=True,
                platform_metadata=account_info
            )
            self.db.add(platform_conn)
            self.db.commit()
            self.db.refresh(platform_conn)
        
        # Store client for reuse
        if platform_name_lower not in self.platform_clients:
            self.platform_clients[platform_name_lower] = {}
            
        self.platform_clients[platform_name_lower][persona_id] = client
        
        return platform_conn
    
    def disconnect_platform(self, persona_id: int, platform_connection_id: int) -> bool:
        """
        Disconnect a platform for a persona.
        
        Args:
            persona_id: ID of the persona.
            platform_connection_id: ID of the platform connection.
            
        Returns:
            True if successful, False otherwise.
        """
        # Find the platform connection
        platform_conn = self.db.query(PlatformConnection).filter(
            PlatformConnection.id == platform_connection_id,
            PlatformConnection.persona_id == persona_id
        ).first()
        
        if not platform_conn:
            return False
            
        # Deactivate the platform connection
        platform_conn.is_active = False
        self.db.commit()
        
        # Remove client if exists
        platform_name_lower = platform_conn.platform_name.lower()
        if platform_name_lower in self.platform_clients and persona_id in self.platform_clients[platform_name_lower]:
            del self.platform_clients[platform_name_lower][persona_id]
        
        return True
    
    def get_platform_connections(self, persona_id: int, active_only: bool = True) -> List[PlatformConnection]:
        """
        Get platform connections for a persona.
        
        Args:
            persona_id: ID of the persona.
            active_only: Whether to only return active connections.
            
        Returns:
            List of platform connections.
        """
        query = self.db.query(PlatformConnection).filter(PlatformConnection.persona_id == persona_id)
        
        if active_only:
            query = query.filter(PlatformConnection.is_active == True)
            
        return query.all()
    
    def post_content(self, persona_id: int, platform_name: str, content: str, media_urls: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Post content to a platform.
        
        Args:
            persona_id: ID of the persona.
            platform_name: Name of the platform.
            content: Content to post.
            media_urls: Optional list of media URLs.
            **kwargs: Additional platform-specific parameters.
            
        Returns:
            Dictionary containing information about the created post.
        """
        client = self.get_client(platform_name, persona_id)
        return client.post_content(content, media_urls, **kwargs)
    
    def get_interactions(self, persona_id: int, platform_name: str, since_id: Optional[str] = None, count: int = 100) -> List[Dict[str, Any]]:
        """
        Get interactions from a platform.
        
        Args:
            persona_id: ID of the persona.
            platform_name: Name of the platform.
            since_id: Optional ID to get interactions newer than this ID.
            count: Maximum number of interactions to retrieve.
            
        Returns:
            List of interaction objects.
        """
        client = self.get_client(platform_name, persona_id)
        return client.get_interactions(since_id, count)
    
    def respond_to_interaction(self, persona_id: int, platform_name: str, interaction_id: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        Respond to an interaction on a platform.
        
        Args:
            persona_id: ID of the persona.
            platform_name: Name of the platform.
            interaction_id: ID of the interaction to respond to.
            content: Response content.
            **kwargs: Additional platform-specific parameters.
            
        Returns:
            Dictionary containing information about the created response.
        """
        client = self.get_client(platform_name, persona_id)
        return client.respond_to_interaction(interaction_id, content, **kwargs)
    
    def get_account_info(self, persona_id: int, platform_name: str) -> Dict[str, Any]:
        """
        Get account information from a platform.
        
        Args:
            persona_id: ID of the persona.
            platform_name: Name of the platform.
            
        Returns:
            Dictionary containing account information.
        """
        client = self.get_client(platform_name, persona_id)
        return client.get_account_info()


def get_platform_manager(db: Session) -> PlatformManager:
    """
    Get a platform manager instance.
    
    Args:
        db: Database session.
        
    Returns:
        Platform manager instance.
    """
    return PlatformManager(db)