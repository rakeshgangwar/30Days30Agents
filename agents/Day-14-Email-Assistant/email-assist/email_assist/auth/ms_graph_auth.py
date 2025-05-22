import os
import json
from typing import Optional, List, Dict, Any

import msal
from microsoftgraph.client import Client

class MSGraphAuth:
    """
    Handles authentication with the Microsoft Graph API using OAuth 2.0 and provides
    access to the Microsoft Graph client.
    """
    
    def __init__(self, 
                 client_id: str, 
                 client_secret: str, 
                 tenant_id: str,
                 scopes: Optional[List[str]] = None,
                 token_cache_file: Optional[str] = None):
        """
        Initialize the Microsoft Graph authentication handler.
        
        Args:
            client_id: Application (client) ID from Azure portal
            client_secret: Client secret from Azure portal
            tenant_id: Directory (tenant) ID from Azure portal
            scopes: List of API scopes to request access to
            token_cache_file: Path to save/load the token cache
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        
        # Default scopes for email operations if none provided
        self.scopes = scopes or [
            'https://graph.microsoft.com/.default'
        ]
        
        self.token_cache_file = token_cache_file
        self.app = None
        self.token_cache = msal.SerializableTokenCache()
        self.graph_client = None
        
        # Load token cache from file if it exists
        if token_cache_file and os.path.exists(token_cache_file):
            try:
                with open(token_cache_file, 'r') as cache_file:
                    self.token_cache.deserialize(cache_file.read())
            except Exception as e:
                print(f"Error loading token cache: {e}")
        
        # Initialize the MSAL application
        self._init_app()
    
    def _init_app(self):
        """
        Initialize the MSAL confidential client application.
        """
        self.app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            token_cache=self.token_cache
        )
    
    def _save_cache(self):
        """
        Save the token cache to file if a cache file path is specified.
        """
        if self.token_cache_file:
            try:
                with open(self.token_cache_file, 'w') as cache_file:
                    cache_file.write(self.token_cache.serialize())
            except Exception as e:
                print(f"Error saving token cache: {e}")
    
    def get_auth_url(self, redirect_uri: str) -> str:
        """
        Get the authorization URL for user consent.
        
        Args:
            redirect_uri: The redirect URI registered in the Azure portal
            
        Returns:
            Authorization URL for the user to visit
        """
        return self.app.get_authorization_request_url(
            scopes=self.scopes,
            redirect_uri=redirect_uri,
            state="state",  # You can use a random state for CSRF protection
        )
    
    def get_token_from_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Get an access token using the authorization code.
        
        Args:
            code: Authorization code received from the authorization response
            redirect_uri: The redirect URI registered in the Azure portal
            
        Returns:
            Token response containing access token and other information
        """
        result = self.app.acquire_token_by_authorization_code(
            code=code,
            scopes=self.scopes,
            redirect_uri=redirect_uri
        )
        
        self._save_cache()
        
        # Initialize the Microsoft Graph client if we have a token
        if result and 'access_token' in result:
            self._init_graph_client(result['access_token'])
            
        return result
    
    def get_token_silent(self) -> Optional[Dict[str, Any]]:
        """
        Get an access token silently from the cache if available.
        
        Returns:
            Token response or None if no token is available in the cache
        """
        accounts = self.app.get_accounts()
        if accounts:
            result = self.app.acquire_token_silent(
                scopes=self.scopes,
                account=accounts[0]
            )
            
            # Initialize the Microsoft Graph client if we have a token
            if result and 'access_token' in result:
                self._init_graph_client(result['access_token'])
                
            return result
        
        return None
    
    def _init_graph_client(self, access_token: str):
        """
        Initialize the Microsoft Graph client with the access token.
        
        Args:
            access_token: The access token for Microsoft Graph API
        """
        # The microsoftgraph-python Client requires client_id and client_secret
        self.graph_client = Client(client_id=self.client_id, client_secret=self.client_secret)
        
        # The client expects a token dictionary, not just the access token string
        token_dict = {
            'access_token': access_token,
            'token_type': 'Bearer'
        }
        self.graph_client.token = token_dict  # Set the token directly as a dictionary
    
    def get_graph_client(self) -> Optional[Client]:
        """
        Get the Microsoft Graph client.
        
        Returns:
            Microsoft Graph client or None if not authenticated
        """
        # If we don't have a client yet, try to get a token silently
        if not self.graph_client:
            token = self.get_token_silent()
            if not token or 'access_token' not in token:
                return None
        
        return self.graph_client
    
    def get_headers(self) -> Optional[Dict[str, str]]:
        """
        Get the authorization headers for Microsoft Graph API requests.
        
        Returns:
            Headers dictionary with Authorization header or None if no token is available
        """
        token = self.get_token_silent()
        if token and 'access_token' in token:
            return {
                'Authorization': f"Bearer {token['access_token']}",
                'Content-Type': 'application/json'
            }
        
        return None
