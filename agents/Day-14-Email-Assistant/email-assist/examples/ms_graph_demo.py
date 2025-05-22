#!/usr/bin/env python3

"""
Demo script for using the Email Assistant Agent with Microsoft Graph API.

This script demonstrates how to use the Email Assistant Agent programmatically
with Microsoft Graph API for Outlook/Office 365 emails.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the email_assist package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_assist.auth.ms_graph_auth import MSGraphAuth
from email_assist.tools.ms_graph_tools import MSGraphTools
from email_assist.email_agent import EmailAssistant


def ms_graph_demo():
    """
    Demonstrate using the Email Assistant Agent with Microsoft Graph API.
    """
    print("\n=== Microsoft Graph Demo ===")
    
    # Get Microsoft Graph credentials from environment variables
    client_id = os.getenv("MS_CLIENT_ID")
    client_secret = os.getenv("MS_CLIENT_SECRET")
    tenant_id = os.getenv("MS_TENANT_ID")
    
    if not all([client_id, client_secret, tenant_id]):
        print("Error: Microsoft Graph credentials not found in environment variables.")
        print("Please set MS_CLIENT_ID, MS_CLIENT_SECRET, and MS_TENANT_ID in your .env file.")
        return
    
    # Initialize Microsoft Graph authentication
    msgraph_auth = MSGraphAuth(
        client_id=client_id,
        client_secret=client_secret,
        tenant_id=tenant_id,
        token_cache_file="ms_token_cache.json"
    )
    
    # Get authorization URL
    redirect_uri = "http://localhost:8000/auth/callback"
    auth_url = msgraph_auth.get_auth_url(redirect_uri)
    
    print(f"\nPlease visit the following URL to authenticate with Microsoft Graph:")
    print(auth_url)
    print("\nAfter authentication, you will be redirected to a URL containing a code parameter.")
    
    # Get the authorization code from the user
    auth_code = input("\nEnter the code from the redirect URL: ")
    
    # Get token using the authorization code
    token = msgraph_auth.get_token_from_code(auth_code, redirect_uri)
    
    if not token or 'access_token' not in token:
        print("Failed to get access token.")
        return
    
    print("Successfully authenticated with Microsoft Graph!")
    
    # Get the headers for API requests
    headers = msgraph_auth.get_headers()
    
    if not headers:
        print("Failed to get authorization headers.")
        return
    
    # Create Microsoft Graph tools
    msgraph_tools = MSGraphTools(headers)
    
    # Create the Email Assistant Agent
    email_assistant = EmailAssistant(
        email_service=msgraph_tools,
        model_provider="openai",  # or "anthropic"
        enable_reasoning=True
    )
    
    # Demo: List recent emails
    print("\nListing recent emails...")
    recent_emails = msgraph_tools.list_messages(folder="inbox", max_results=3)
    
    if recent_emails:
        # Demo: Summarize the first email
        email_id = recent_emails[0]['id']
        print(f"\nSummarizing email {email_id}...")
        summary = email_assistant.summarize_email(email_id)
        print(f"\nSummary:\n{summary}")
        
        # Demo: Extract action items
        print(f"\nExtracting action items from email {email_id}...")
        action_items = email_assistant.extract_action_items(email_id)
        print(f"\nAction Items:\n{action_items}")
        
        # Demo: Draft a reply
        print(f"\nDrafting a reply to email {email_id}...")
        reply = email_assistant.draft_reply(email_id, "Thank them for their email and ask for more details")
        print(f"\nDraft Reply:\n{reply}")
        
        # Demo: Search for emails
        search_query = "meeting"
        print(f"\nSearching for emails with query: '{search_query}'...")
        search_results = msgraph_tools.search_messages(search_query, max_results=2)
        print(f"Found {len(search_results)} emails matching the query.")
    else:
        print("No emails found.")


def main():
    """
    Main function to run the demo.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if API keys are set
    if not (os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")):
        print("Error: No API key found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file.")
        return
    
    # Run the Microsoft Graph demo
    ms_graph_demo()
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main()
