"""
LinkedIn client module.

This module provides integration with the LinkedIn API.
"""

import logging
import json
import requests
from typing import Dict, Any, List, Optional

from app.core.platforms.base import BasePlatformClient

logger = logging.getLogger(__name__)

class LinkedInClient(BasePlatformClient):
    """
    Client for LinkedIn API integration.
    
    This class implements the BasePlatformClient interface for LinkedIn.
    """
    
    # LinkedIn API endpoints
    BASE_URL = "https://api.linkedin.com/v2"
    PROFILE_URL = f"{BASE_URL}/me"
    SHARES_URL = f"{BASE_URL}/shares"
    UGCPOSTS_URL = f"{BASE_URL}/ugcPosts"
    
    def __init__(self):
        """Initialize the LinkedIn client."""
        self.access_token = None
        self.authenticated = False
        self.user_info = None
        self.person_id = None
        self.organization_id = None
    
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate with LinkedIn using provided credentials.
        
        Args:
            credentials: Dictionary containing the necessary credentials:
                - access_token: LinkedIn access token
                - organization_id: Optional LinkedIn organization ID (for company pages)
                
        Returns:
            True if authentication was successful, False otherwise.
        """
        try:
            self.access_token = credentials.get('access_token')
            self.organization_id = credentials.get('organization_id')
            
            if not self.access_token:
                logger.error("LinkedIn access token is required")
                return False
            
            # Verify credentials by fetching profile information
            headers = self._get_auth_headers()
            response = requests.get(
                f"{self.PROFILE_URL}",
                headers=headers,
                params={"projection": "(id,localizedFirstName,localizedLastName,profilePicture,vanityName)"}
            )
            
            if response.status_code == 200:
                self.user_info = response.json()
                self.person_id = self.user_info.get('id')
                self.authenticated = True
                logger.info(f"Successfully authenticated with LinkedIn as {self.user_info.get('localizedFirstName')} {self.user_info.get('localizedLastName')}")
                return True
            else:
                logger.error(f"LinkedIn authentication failed: {response.status_code} - {response.text}")
                self.authenticated = False
                return False
                
        except Exception as e:
            logger.error(f"LinkedIn authentication failed: {e}")
            self.authenticated = False
            return False
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get headers for authenticated API requests.
        
        Returns:
            Dictionary of headers including authorization.
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
    
    def post_content(self, content: str, media_urls: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Post content to LinkedIn.
        
        Args:
            content: The post text.
            media_urls: Optional list of media URLs to attach to the post.
            **kwargs: Additional LinkedIn-specific parameters, such as:
                - title: Post title (for articles)
                - visibility: Post visibility (PUBLIC, CONNECTIONS, etc.)
                
        Returns:
            Dictionary containing information about the created post.
        """
        if not self.authenticated or not self.access_token:
            raise ValueError("LinkedIn client not authenticated")
        
        try:
            visibility = kwargs.get('visibility', 'PUBLIC')
            
            # For simplicity, we're using UGC posts (User Generated Content)
            # rather than the older Shares API
            
            # Prepare the post payload
            post_data = {
                "author": f"urn:li:person:{self.person_id}" if not self.organization_id else f"urn:li:organization:{self.organization_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility
                }
            }
            
            # Add media if provided
            if media_urls and len(media_urls) > 0:
                media_assets = []
                
                # For each media URL, we would need to first upload the media to LinkedIn
                # This is a simplified version - in a real implementation, you'd need to:
                # 1. Request an upload URL from LinkedIn
                # 2. Upload the media to that URL
                # 3. Get the asset ID
                
                # For this example, we'll just attach the first URL as a link
                if media_urls[0]:
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
                    post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                        "status": "READY",
                        "originalUrl": media_urls[0],
                        "title": {
                            "text": kwargs.get('title', 'Shared Article')
                        }
                    }]
            
            # Post to LinkedIn
            headers = self._get_auth_headers()
            response = requests.post(
                self.UGCPOSTS_URL,
                headers=headers,
                json=post_data
            )
            
            if response.status_code in (200, 201):
                post_info = response.json()
                
                # Format the response
                post_data = {
                    'id': post_info.get('id', '').split(':')[-1],
                    'text': content,
                    'created_at': post_info.get('created', {}).get('time', ''),
                    'user': {
                        'id': self.person_id,
                        'name': f"{self.user_info.get('localizedFirstName', '')} {self.user_info.get('localizedLastName', '')}",
                    },
                    'media': [{'url': url} for url in media_urls] if media_urls else [],
                    'platform': 'LinkedIn'
                }
                
                return post_data
            else:
                logger.error(f"Failed to post to LinkedIn: {response.status_code} - {response.text}")
                raise ValueError(f"Failed to post to LinkedIn: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to post to LinkedIn: {e}")
            raise ValueError(f"Failed to post to LinkedIn: {str(e)}")
    
    def get_interactions(self, since_id: Optional[str] = None, count: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent interactions from LinkedIn (comments, reactions).
        
        Note: LinkedIn API has limitations on access to social interactions. 
        This implementation focuses on comments on the user's posts.
        
        Args:
            since_id: Optional parameter (not used in this implementation due to LinkedIn API limitations)
            count: Maximum number of interactions to retrieve.
            
        Returns:
            List of interaction objects from LinkedIn.
        """
        if not self.authenticated or not self.access_token:
            raise ValueError("LinkedIn client not authenticated")
        
        try:
            headers = self._get_auth_headers()
            
            # Get recent posts by the user
            response = requests.get(
                self.UGCPOSTS_URL,
                headers=headers,
                params={
                    "q": "authors",
                    "authors": f"urn:li:person:{self.person_id}" if not self.organization_id else f"urn:li:organization:{self.organization_id}",
                    "count": min(count, 10)  # LinkedIn has lower limits
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to retrieve LinkedIn posts: {response.status_code} - {response.text}")
                return []
                
            posts_data = response.json()
            posts = posts_data.get('elements', [])
            
            # For each post, get the comments
            interactions = []
            
            for post in posts:
                post_urn = post.get('id')
                if not post_urn:
                    continue
                
                # Get comments on this post
                comments_response = requests.get(
                    f"{self.BASE_URL}/socialActions/{post_urn}/comments",
                    headers=headers,
                    params={"count": min(count, 20)}  # LinkedIn has lower limits
                )
                
                if comments_response.status_code != 200:
                    logger.warning(f"Failed to retrieve comments for post {post_urn}: {comments_response.status_code} - {comments_response.text}")
                    continue
                    
                comments_data = comments_response.json()
                comments = comments_data.get('elements', [])
                
                for comment in comments:
                    # Get commenter info
                    actor_urn = comment.get('actor', '')
                    commenter_info = {"name": "Unknown User", "id": actor_urn.split(':')[-1] if actor_urn else "unknown"}
                    
                    try:
                        if actor_urn and actor_urn.startswith('urn:li:person:'):
                            commenter_response = requests.get(
                                f"{self.BASE_URL}/people/{actor_urn.split(':')[-1]}",
                                headers=headers,
                                params={"projection": "(id,localizedFirstName,localizedLastName,profilePicture)"}
                            )
                            if commenter_response.status_code == 200:
                                commenter_data = commenter_response.json()
                                commenter_info = {
                                    "id": commenter_data.get('id'),
                                    "name": f"{commenter_data.get('localizedFirstName', '')} {commenter_data.get('localizedLastName', '')}",
                                    "profile_image_url": commenter_data.get('profilePicture', {}).get('displayImage', '')
                                }
                    except Exception as e:
                        logger.warning(f"Failed to get commenter info: {e}")
                    
                    # Format the interaction
                    interaction = {
                        'id': comment.get('id', '').split(':')[-1],
                        'text': comment.get('message', {}).get('text', ''),
                        'created_at': comment.get('created', {}).get('time', ''),
                        'type': 'comment',
                        'user': commenter_info,
                        'parent_id': post_urn.split(':')[-1],
                        'platform': 'LinkedIn'
                    }
                    
                    interactions.append(interaction)
                    
                    if len(interactions) >= count:
                        break
            
            return interactions
                
        except Exception as e:
            logger.error(f"Failed to retrieve LinkedIn interactions: {e}")
            raise ValueError(f"Failed to retrieve LinkedIn interactions: {str(e)}")
    
    def respond_to_interaction(self, interaction_id: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        Respond to a LinkedIn interaction.
        
        Args:
            interaction_id: The URN of the comment or post to respond to.
            content: The response text.
            **kwargs: Additional LinkedIn-specific parameters.
            
        Returns:
            Dictionary containing information about the created response.
        """
        if not self.authenticated or not self.access_token:
            raise ValueError("LinkedIn client not authenticated")
        
        try:
            parent_urn = kwargs.get('parent_urn')
            
            if not parent_urn:
                # If we just have an ID, we assume it's a comment ID
                # In a real implementation, you'd need to handle different cases
                logger.error("LinkedIn response requires a parent_urn parameter")
                raise ValueError("LinkedIn response requires a parent_urn parameter")
                
            # Create a comment
            comment_data = {
                "actor": f"urn:li:person:{self.person_id}" if not self.organization_id else f"urn:li:organization:{self.organization_id}",
                "message": {
                    "text": content
                }
            }
            
            headers = self._get_auth_headers()
            response = requests.post(
                f"{self.BASE_URL}/socialActions/{parent_urn}/comments",
                headers=headers,
                json=comment_data
            )
            
            if response.status_code in (200, 201):
                comment_info = response.json()
                
                # Format the response
                comment_data = {
                    'id': comment_info.get('id', '').split(':')[-1],
                    'text': content,
                    'created_at': comment_info.get('created', {}).get('time', ''),
                    'user': {
                        'id': self.person_id,
                        'name': f"{self.user_info.get('localizedFirstName', '')} {self.user_info.get('localizedLastName', '')}",
                    },
                    'parent_id': parent_urn.split(':')[-1],
                    'platform': 'LinkedIn'
                }
                
                return comment_data
            else:
                logger.error(f"Failed to respond on LinkedIn: {response.status_code} - {response.text}")
                raise ValueError(f"Failed to respond on LinkedIn: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Failed to respond on LinkedIn: {e}")
            raise ValueError(f"Failed to respond on LinkedIn: {str(e)}")

    def get_account_info(self) -> Dict[str, Any]:
        """
        Get information about the connected LinkedIn account.
        
        Returns:
            Dictionary containing information about the account.
        """
        if not self.authenticated or not self.access_token:
            raise ValueError("LinkedIn client not authenticated")
        
        try:
            headers = self._get_auth_headers()
            
            # Get basic profile information
            profile_response = requests.get(
                f"{self.PROFILE_URL}",
                headers=headers,
                params={"projection": "(id,localizedFirstName,localizedLastName,profilePicture,vanityName)"}
            )
            
            if profile_response.status_code != 200:
                logger.error(f"Failed to retrieve LinkedIn profile: {profile_response.status_code} - {profile_response.text}")
                raise ValueError(f"Failed to retrieve LinkedIn profile: {profile_response.status_code}")
                
            profile_data = profile_response.json()
            
            # Get follower and connection counts
            # Note: These endpoints require additional permissions
            follower_count = 0
            connection_count = 0
            
            try:
                network_response = requests.get(
                    f"{self.BASE_URL}/networkSizes/{self.person_id}?edgeType=CONNECTIONS",
                    headers=headers
                )
                if network_response.status_code == 200:
                    network_data = network_response.json()
                    connection_count = network_data.get('firstDegreeSize', 0)
            except Exception as e:
                logger.warning(f"Failed to retrieve LinkedIn connection count: {e}")
            
            try:
                follower_response = requests.get(
                    f"{self.BASE_URL}/networkSizes/{self.person_id}?edgeType=FOLLOWERS",
                    headers=headers
                )
                if follower_response.status_code == 200:
                    follower_data = follower_response.json()
                    follower_count = follower_data.get('firstDegreeSize', 0)
            except Exception as e:
                logger.warning(f"Failed to retrieve LinkedIn follower count: {e}")
            
            # Format the account info
            account_info = {
                'id': profile_data.get('id'),
                'name': f"{profile_data.get('localizedFirstName', '')} {profile_data.get('localizedLastName', '')}",
                'vanity_name': profile_data.get('vanityName', ''),
                'profile_image_url': profile_data.get('profilePicture', {}).get('displayImage', ''),
                'follower_count': follower_count,
                'connection_count': connection_count,
                'platform': 'LinkedIn'
            }
            
            return account_info
                
        except Exception as e:
            logger.error(f"Failed to retrieve LinkedIn account info: {e}")
            raise ValueError(f"Failed to retrieve LinkedIn account info: {str(e)}")