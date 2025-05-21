"""
Twitter client module.

This module provides integration with the Twitter API.
"""

import logging
from typing import Dict, Any, List, Optional
import tweepy
from tweepy.errors import TweepyException
from tweepy.client import Response

from app.core.platforms.base import BasePlatformClient

logger = logging.getLogger(__name__)

class TwitterClient(BasePlatformClient):
    """
    Client for Twitter API integration.

    This class implements the BasePlatformClient interface for Twitter.
    """

    def __init__(self):
        """Initialize the Twitter client."""
        self.api = None  # v1.1 API client (for limited operations)
        self.client = None  # v2 API client (for posting)
        self.authenticated = False
        self.user_info = None

    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate with Twitter using provided credentials.

        Args:
            credentials: Dictionary containing the necessary credentials:
                - api_key: Twitter API key
                - api_secret: Twitter API secret
                - access_token: Twitter access token
                - access_token_secret: Twitter access token secret
                - bearer_token: Twitter bearer token (optional, for v2 API)

        Returns:
            True if authentication was successful, False otherwise.
        """
        try:
            # Set up v1.1 API client (for limited operations)
            auth = tweepy.OAuth1UserHandler(
                credentials.get('api_key'),
                credentials.get('api_secret'),
                credentials.get('access_token'),
                credentials.get('access_token_secret')
            )
            self.api = tweepy.API(auth)

            # Set up v2 API client (for posting)
            self.client = tweepy.Client(
                consumer_key=credentials.get('api_key'),
                consumer_secret=credentials.get('api_secret'),
                access_token=credentials.get('access_token'),
                access_token_secret=credentials.get('access_token_secret'),
                bearer_token=credentials.get('bearer_token')  # Optional
            )

            # Verify credentials
            self.user_info = self.api.verify_credentials()
            self.authenticated = True
            logger.info(f"Successfully authenticated with Twitter as @{self.user_info.screen_name}")
            return True

        except TweepyException as e:
            logger.error(f"Twitter authentication failed: {e}")
            self.authenticated = False
            return False

    def post_content(self, content: str, media_urls: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Post content to Twitter using v2 API.

        Args:
            content: The tweet text.
            media_urls: Optional list of media URLs to attach to the tweet.
            **kwargs: Additional Twitter-specific parameters, such as:
                - in_reply_to_tweet_id: ID of the tweet to reply to

        Returns:
            Dictionary containing information about the created tweet.
        """
        if not self.authenticated or not self.client:
            raise ValueError("Twitter client not authenticated")

        try:
            media_ids = []
            if media_urls:
                for media_url in media_urls:
                    try:
                        # Upload media using v1.1 API (still allowed in free tier)
                        media = self.api.media_upload(media_url)
                        media_ids.append(media.media_id)
                    except TweepyException as e:
                        logger.error(f"Failed to upload media {media_url}: {e}")

            # Post the tweet using v2 API
            response = self.client.create_tweet(
                text=content,
                media_ids=media_ids if media_ids else None,
                in_reply_to_tweet_id=kwargs.get('in_reply_to_status_id') or kwargs.get('in_reply_to_tweet_id')
            )

            # Extract tweet data from response
            if isinstance(response, Response) and hasattr(response, 'data'):
                tweet_data = response.data

                # Format the response
                formatted_data = {
                    'id': str(tweet_data.get('id')),
                    'text': tweet_data.get('text', ''),
                    'created_at': tweet_data.get('created_at', ''),  # v2 API might not include this
                    'user': {
                        'id': str(self.user_info.id),
                        'name': self.user_info.name,
                        'screen_name': self.user_info.screen_name,
                    },
                    'media': [],  # v2 API handles media differently
                    'platform': 'Twitter',
                    'url': f"https://twitter.com/user/status/{tweet_data.get('id')}"
                }

                return formatted_data
            else:
                # Fallback for unexpected response format
                return {
                    'id': str(getattr(response, 'id', 'unknown')),
                    'text': content,
                    'created_at': '',
                    'user': {
                        'id': str(self.user_info.id),
                        'name': self.user_info.name,
                        'screen_name': self.user_info.screen_name,
                    },
                    'platform': 'Twitter'
                }

        except TweepyException as e:
            logger.error(f"Failed to post tweet: {e}")
            raise ValueError(f"Failed to post tweet: {str(e)}")

    def get_interactions(self, since_id: Optional[str] = None, count: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent interactions from Twitter (mentions, replies).

        Args:
            since_id: Optional tweet ID to get mentions newer than this ID.
            count: Maximum number of mentions to retrieve.

        Returns:
            List of mention objects.
        """
        if not self.authenticated or not self.api:
            raise ValueError("Twitter client not authenticated")

        try:
            # Get mentions
            mentions = self.api.mentions_timeline(
                since_id=since_id,
                count=count
            )

            # Convert mentions to dictionaries
            interactions = []
            for mention in mentions:
                interaction = {
                    'id': mention.id_str,
                    'text': mention.text,
                    'created_at': mention.created_at.isoformat(),
                    'type': 'mention',
                    'user': {
                        'id': mention.user.id_str,
                        'name': mention.user.name,
                        'screen_name': mention.user.screen_name,
                        'profile_image_url': mention.user.profile_image_url_https,
                    },
                    'platform': 'Twitter'
                }
                interactions.append(interaction)

            return interactions

        except TweepyException as e:
            logger.error(f"Failed to retrieve Twitter mentions: {e}")
            raise ValueError(f"Failed to retrieve Twitter mentions: {str(e)}")

    def respond_to_interaction(self, interaction_id: str, content: str, **kwargs) -> Dict[str, Any]:
        """
        Respond to a Twitter interaction using v2 API.

        Args:
            interaction_id: The ID of the tweet to respond to.
            content: The response tweet text.
            **kwargs: Additional Twitter-specific parameters.

        Returns:
            Dictionary containing information about the created response tweet.
        """
        if not self.authenticated or not self.client:
            raise ValueError("Twitter client not authenticated")

        try:
            # Create a reply using v2 API
            response = self.client.create_tweet(
                text=content,
                in_reply_to_tweet_id=interaction_id
            )

            # Extract tweet data from response
            if isinstance(response, Response) and hasattr(response, 'data'):
                tweet_data = response.data

                # Format the response
                formatted_data = {
                    'id': str(tweet_data.get('id')),
                    'text': tweet_data.get('text', ''),
                    'created_at': tweet_data.get('created_at', ''),
                    'user': {
                        'id': str(self.user_info.id),
                        'name': self.user_info.name,
                        'screen_name': self.user_info.screen_name,
                    },
                    'in_reply_to_status_id': interaction_id,
                    'platform': 'Twitter',
                    'url': f"https://twitter.com/user/status/{tweet_data.get('id')}"
                }

                return formatted_data
            else:
                # Fallback for unexpected response format
                return {
                    'id': str(getattr(response, 'id', 'unknown')),
                    'text': content,
                    'created_at': '',
                    'user': {
                        'id': str(self.user_info.id),
                        'name': self.user_info.name,
                        'screen_name': self.user_info.screen_name,
                    },
                    'in_reply_to_status_id': interaction_id,
                    'platform': 'Twitter'
                }

        except TweepyException as e:
            logger.error(f"Failed to respond to tweet: {e}")
            raise ValueError(f"Failed to respond to tweet: {str(e)}")

    def get_account_info(self) -> Dict[str, Any]:
        """
        Get information about the connected Twitter account.

        Returns:
            Dictionary containing information about the account.
        """
        if not self.authenticated or not self.api or not self.user_info:
            raise ValueError("Twitter client not authenticated")

        try:
            user = self.user_info

            # Get follower and following counts
            follower_count = user.followers_count
            following_count = user.friends_count

            # Get tweet count
            tweet_count = user.statuses_count

            account_info = {
                'id': user.id_str,
                'name': user.name,
                'screen_name': user.screen_name,
                'profile_image_url': user.profile_image_url_https,
                'follower_count': follower_count,
                'following_count': following_count,
                'tweet_count': tweet_count,
                'created_at': user.created_at.isoformat(),
                'description': user.description,
                'platform': 'Twitter'
            }

            return account_info

        except TweepyException as e:
            logger.error(f"Failed to retrieve Twitter account info: {e}")
            raise ValueError(f"Failed to retrieve Twitter account info: {str(e)}")