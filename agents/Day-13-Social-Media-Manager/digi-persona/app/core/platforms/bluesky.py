"""
Bluesky client module.

This module provides integration with the Bluesky API (AT Protocol).
"""

import logging
import json
import httpx
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.core.platforms.base import BasePlatformClient

logger = logging.getLogger(__name__)

class BlueskyClient(BasePlatformClient):
    """
    Client for Bluesky API integration.

    This class implements the BasePlatformClient interface for Bluesky using AT Protocol.
    """

    # Bluesky API endpoints
    BASE_URL = "https://bsky.social/xrpc"

    def __init__(self):
        """Initialize the Bluesky client."""
        self.client = httpx.AsyncClient()
        self.authenticated = False
        self.user_info = None
        self.access_jwt = None
        self.refresh_jwt = None
        self.did = None
        self.handle = None

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate with Bluesky using provided credentials.

        Args:
            credentials: Dictionary containing the necessary credentials:
                - handle: Bluesky handle (username)
                - app_password: App password for Bluesky

        Returns:
            True if authentication was successful, False otherwise.
        """
        try:
            handle = credentials.get('handle')
            password = credentials.get('app_password')

            if not handle or not password:
                logger.error("Bluesky handle and app_password are required")
                return False

            # Create a synchronous client for authentication
            with httpx.Client() as client:
                # Authenticate
                response = client.post(
                    f"{self.BASE_URL}/com.atproto.server.createSession",
                    json={
                        "identifier": handle,
                        "password": password
                    }
                )

                if response.status_code == 200:
                    auth_data = response.json()
                    self.access_jwt = auth_data.get('accessJwt')
                    self.refresh_jwt = auth_data.get('refreshJwt')
                    self.did = auth_data.get('did')
                    self.handle = auth_data.get('handle')
                    self.authenticated = True

                    # Get additional user info
                    profile_response = client.get(
                        f"{self.BASE_URL}/com.atproto.repo.describeRepo",
                        params={"repo": self.did},
                        headers={"Authorization": f"Bearer {self.access_jwt}"}
                    )

                    if profile_response.status_code == 200:
                        self.user_info = profile_response.json()

                    logger.info(f"Successfully authenticated with Bluesky as {self.handle}")
                    return True
                else:
                    logger.error(f"Bluesky authentication failed: {response.status_code} - {response.text}")
                    self.authenticated = False
                    return False

        except Exception as e:
            logger.error(f"Bluesky authentication failed: {e}")
            self.authenticated = False
            return False

    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get headers for authenticated API requests.

        Returns:
            Dictionary of headers including authorization.
        """
        return {
            "Authorization": f"Bearer {self.access_jwt}",
            "Content-Type": "application/json",
        }

    def post_content(self, content: str, media_urls: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Post content to Bluesky.

        Args:
            content: The post text.
            media_urls: Optional list of media URLs to attach to the post.
            **kwargs: Additional Bluesky-specific parameters.
                - reply_to: Optional reply reference (record URI)

        Returns:
            Dictionary containing information about the created post.
        """
        if not self.authenticated or not self.access_jwt:
            raise ValueError("Bluesky client not authenticated")

        try:
            # Prepare the post payload
            post_data = {
                "repo": self.did,
                "collection": "app.bsky.feed.post",
                "record": {
                    "$type": "app.bsky.feed.post",
                    "text": content,
                    "createdAt": datetime.now(timezone.utc).isoformat()
                }
            }

            # Add reply reference if provided
            reply_to = kwargs.get('reply_to')
            if reply_to:
                reply_ref = json.loads(reply_to)
                post_data["record"]["reply"] = reply_ref

            # Add media if provided
            # Note: This is a simplified version. In a real implementation,
            # you would need to first upload the images to Bluesky's BLOB storage
            if media_urls and len(media_urls) > 0:
                # In a real implementation, this would involve:
                # 1. Uploading each image using com.atproto.repo.uploadBlob
                # 2. Getting the blob refs
                # 3. Adding them to the post record
                logger.warning("Media upload not implemented in this sample implementation")

            # Post to Bluesky with retries and timeout
            max_retries = 3
            retry_count = 0

            while retry_count < max_retries:
                try:
                    with httpx.Client(timeout=30.0) as client:  # Increase timeout to 30 seconds
                        logger.info(f"Attempting to post to Bluesky (attempt {retry_count + 1}/{max_retries})")
                        response = client.post(
                            f"{self.BASE_URL}/com.atproto.repo.createRecord",
                            headers=self._get_auth_headers(),
                            json=post_data,
                            timeout=30.0  # Explicit timeout
                        )

                        # Check response status code
                        if response.status_code in (200, 201):
                            post_info = response.json()

                            # Get the post URI
                            post_uri = post_info.get('uri', '')
                            post_cid = post_info.get('cid', '')

                            # Format the response
                            result_data = {
                                'id': post_uri.split('/')[-1],
                                'uri': post_uri,
                                'cid': post_cid,
                                'text': content,
                                'created_at': post_data['record']['createdAt'],
                                'user': {
                                    'did': self.did,
                                    'handle': self.handle,
                                },
                                'platform': 'Bluesky'
                            }

                            logger.info(f"Successfully posted to Bluesky: {post_uri}")
                            return result_data
                        else:
                            error_msg = f"Failed to post to Bluesky: {response.status_code} - {response.text}"
                            logger.error(error_msg)
                            raise ValueError(error_msg)

                except Exception as e:
                    retry_count += 1
                    logger.warning(f"Bluesky post attempt {retry_count}/{max_retries} failed: {e}")
                    if retry_count >= max_retries:
                        raise ValueError(f"Failed to post to Bluesky after {max_retries} attempts: {str(e)}")
                    # Add exponential backoff
                    import time
                    time.sleep(2 ** retry_count)  # 2, 4, 8 seconds

        except Exception as e:
            logger.error(f"Failed to post to Bluesky: {e}")
            raise ValueError(f"Failed to post to Bluesky: {str(e)}")

    def get_interactions(self, since_id: Optional[str] = None, count: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent interactions from Bluesky (mentions, replies).

        Args:
            since_id: Optional cursor to get interactions newer than this cursor.
            count: Maximum number of interactions to retrieve.

        Returns:
            List of interaction objects from Bluesky.
        """
        if not self.authenticated or not self.access_jwt:
            raise ValueError("Bluesky client not authenticated")

        try:
            # Get notifications (mentions, replies, etc.)
            params = {"limit": min(count, 50)}  # Bluesky has lower limits
            if since_id:
                params["cursor"] = since_id

            with httpx.Client() as client:
                response = client.get(
                    f"{self.BASE_URL}/app.bsky.notification.listNotifications",
                    headers=self._get_auth_headers(),
                    params=params
                )

                if response.status_code != 200:
                    logger.error(f"Failed to retrieve Bluesky notifications: {response.status_code} - {response.text}")
                    return []

                notifications_data = response.json()
                notifications = notifications_data.get('notifications', [])

                # Format the interactions
                interactions = []

                for notification in notifications:
                    # Only handle certain notification types
                    reason = notification.get('reason')
                    if reason not in ('mention', 'reply', 'quote'):
                        continue

                    record = notification.get('record', {})
                    author = notification.get('author', {})

                    interaction_type = 'mention' if reason == 'mention' else 'reply' if reason == 'reply' else 'quote'

                    # Format the interaction
                    interaction = {
                        'id': notification.get('uri', '').split('/')[-1],
                        'uri': notification.get('uri', ''),
                        'cid': notification.get('cid', ''),
                        'text': record.get('text', ''),
                        'created_at': record.get('createdAt', ''),
                        'type': interaction_type,
                        'user': {
                            'did': author.get('did', ''),
                            'handle': author.get('handle', ''),
                            'display_name': author.get('displayName', ''),
                            'avatar': author.get('avatar', '')
                        },
                        'platform': 'Bluesky'
                    }

                    # Add reply context if available
                    if 'reply' in record:
                        interaction['reply_to'] = {
                            'uri': record['reply'].get('parent', {}).get('uri', ''),
                            'cid': record['reply'].get('parent', {}).get('cid', '')
                        }

                    interactions.append(interaction)

                return interactions

        except Exception as e:
            logger.error(f"Failed to retrieve Bluesky interactions: {e}")
            raise ValueError(f"Failed to retrieve Bluesky interactions: {str(e)}")

    def respond_to_interaction(self, interaction_id: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        Respond to a Bluesky interaction.

        Args:
            interaction_id: The URI or record of the post to respond to.
            content: The response text.
            **kwargs: Additional Bluesky-specific parameters.

        Returns:
            Dictionary containing information about the created response.
        """
        if not self.authenticated or not self.access_jwt:
            raise ValueError("Bluesky client not authenticated")

        try:
            # Extract record information
            reply_uri = kwargs.get('uri') or interaction_id
            reply_cid = kwargs.get('cid')

            if not reply_uri or not reply_cid:
                # If we just have the URI, we need to fetch the CID
                with httpx.Client() as client:
                    record_response = client.get(
                        f"{self.BASE_URL}/com.atproto.repo.getRecord",
                        headers=self._get_auth_headers(),
                        params={
                            "repo": reply_uri.split('/')[0],
                            "collection": "app.bsky.feed.post",
                            "rkey": reply_uri.split('/')[-1]
                        }
                    )

                    if record_response.status_code == 200:
                        record_data = record_response.json()
                        reply_cid = record_data.get('cid')
                    else:
                        logger.error(f"Failed to fetch record info: {record_response.status_code} - {record_response.text}")
                        raise ValueError("Could not get record information for reply")

            # Prepare reply reference
            reply_ref = {
                "root": {
                    "uri": reply_uri,
                    "cid": reply_cid
                },
                "parent": {
                    "uri": reply_uri,
                    "cid": reply_cid
                }
            }

            # Use the post_content method with the reply reference
            return self.post_content(content, reply_to=json.dumps(reply_ref))

        except Exception as e:
            logger.error(f"Failed to respond on Bluesky: {e}")
            raise ValueError(f"Failed to respond on Bluesky: {str(e)}")

    def get_account_info(self) -> Dict[str, Any]:
        """
        Get information about the connected Bluesky account.

        Returns:
            Dictionary containing information about the account.
        """
        if not self.authenticated or not self.access_jwt:
            raise ValueError("Bluesky client not authenticated")

        try:
            with httpx.Client() as client:
                # Get profile information
                profile_response = client.get(
                    f"{self.BASE_URL}/app.bsky.actor.getProfile",
                    headers=self._get_auth_headers(),
                    params={"actor": self.did}
                )

                if profile_response.status_code != 200:
                    logger.error(f"Failed to retrieve Bluesky profile: {profile_response.status_code} - {profile_response.text}")
                    raise ValueError(f"Failed to retrieve Bluesky profile: {profile_response.status_code}")

                profile_data = profile_response.json()

                # Format the account info
                account_info = {
                    'did': profile_data.get('did'),
                    'handle': profile_data.get('handle'),
                    'display_name': profile_data.get('displayName'),
                    'description': profile_data.get('description'),
                    'following_count': profile_data.get('followsCount', 0),
                    'follower_count': profile_data.get('followersCount', 0),
                    'posts_count': profile_data.get('postsCount', 0),
                    'avatar_url': profile_data.get('avatar'),
                    'platform': 'Bluesky'
                }

                return account_info

        except Exception as e:
            logger.error(f"Failed to retrieve Bluesky account info: {e}")
            raise ValueError(f"Failed to retrieve Bluesky account info: {str(e)}")