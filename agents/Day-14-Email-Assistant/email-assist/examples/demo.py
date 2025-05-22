#!/usr/bin/env python3

"""
Demo script for using the Email Assistant Agent without the Streamlit UI.

This script demonstrates how to use the Email Assistant Agent programmatically
with both Gmail and Microsoft Graph APIs.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the email_assist package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_assist.auth.gmail_auth import GmailAuth
from email_assist.tools.gmail_tools import GmailTools
from email_assist.email_agent import EmailAssistant


def gmail_demo():
    """
    Demonstrate using the Email Assistant Agent with Gmail.
    """
    print("\n=== Gmail Demo ===")
    
    # Initialize Gmail authentication
    # You need to have credentials.json in the current directory
    # or specify the path to it
    gmail_auth = GmailAuth(
        credentials_file="credentials.json",
        token_file="token.pickle"
    )
    
    # Authenticate with Gmail
    if not gmail_auth.authenticate():
        print("Failed to authenticate with Gmail.")
        return
    
    print("Successfully authenticated with Gmail!")
    
    # Get the Gmail service
    gmail_service = gmail_auth.get_service()
    
    # Create Gmail tools
    gmail_tools = GmailTools(gmail_service)
    
    # Create the Email Assistant Agent
    email_assistant = EmailAssistant(
        email_service=gmail_tools,
        model_provider="openai",  # or "anthropic"
        enable_reasoning=True
    )
    
    # Demo: List recent emails
    print("\nListing recent emails...")
    recent_emails = gmail_tools.list_messages(max_results=3)
    
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
    
    # Run the Gmail demo
    gmail_demo()
    
    print("\nDemo completed!")


if __name__ == "__main__":
    main()
