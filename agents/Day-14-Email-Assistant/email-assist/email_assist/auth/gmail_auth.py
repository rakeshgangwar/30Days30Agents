import os
import pickle
from pathlib import Path
from typing import Optional, List

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class GmailAuth:
    """
    Handles authentication with the Gmail API using OAuth 2.0.
    """
    
    def __init__(self, credentials_file: str, token_file: str, scopes: Optional[List[str]] = None):
        """
        Initialize the Gmail authentication handler.
        
        Args:
            credentials_file: Path to the client secrets JSON file downloaded from Google Cloud Console
            token_file: Path to save/load the user's access and refresh tokens
            scopes: List of API scopes to request access to (defaults to Gmail read/send/modify)
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        
        # Default scopes for email operations if none provided
        self.scopes = scopes or [
            'https://www.googleapis.com/auth/gmail.readonly',  # Read emails
            'https://www.googleapis.com/auth/gmail.send',      # Send emails
            'https://www.googleapis.com/auth/gmail.modify',    # Modify emails (e.g., mark as read)
        ]
        
        self.creds = None
        self.service = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with the Gmail API.
        
        Returns:
            True if authentication was successful, False otherwise
        """
        # Check if token file exists and load credentials
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If credentials don't exist or are invalid, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # Create the flow using client secrets file
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.scopes)
                
                # Run the OAuth flow in a local server
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
        
        # Build the Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=self.creds)
            return True
        except Exception as e:
            print(f"Error building Gmail service: {e}")
            return False
    
    def get_service(self):
        """
        Get the authenticated Gmail service.
        
        Returns:
            The Gmail service object or None if not authenticated
        """
        if not self.service:
            self.authenticate()
        
        return self.service
