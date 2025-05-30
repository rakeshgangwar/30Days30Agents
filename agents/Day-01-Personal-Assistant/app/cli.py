#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Command-line interface for the Personal Assistant.

This module provides a simple command-line interface for interacting
with the Personal Assistant agent.
"""

import os
import sys
import logging
from dotenv import load_dotenv

from app.agent import create_agent
from app.config import init_user_preferences

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("personal_assistant.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to run the Personal Assistant CLI.
    """
    # Load environment variables
    load_dotenv()
    
    # Check for API keys
    required_apis = ["OPENAI_API_KEY"]
    missing_apis = [api for api in required_apis if not os.getenv(api)]
    
    if missing_apis:
        print("Error: The following required API keys are missing:")
        for api in missing_apis:
            print(f"  - {api}")
        print("\nPlease add them to your .env file or set them as environment variables.")
        sys.exit(1)
    
    # Initialize user preferences
    init_user_preferences()
    
    # Create the agent
    print("Initializing Personal Assistant...")
    agent_executor = create_agent(verbose=False)
    
    # Welcome message
    print("\n" + "="*50)
    print("Welcome to the Personal Assistant!")
    print("="*50)
    print("I can help with:")
    print("  - Weather information")
    print("  - Setting reminders and tasks")
    print("  - Answering general knowledge questions")
    print("  - Finding recent news")
    print("\nType 'exit', 'quit', or 'bye' to end the conversation.")
    print("="*50 + "\n")
    
    # Main conversation loop
    try:
        while True:
            # Get user input
            user_input = input("\nYou: ")
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\nThank you for using the Personal Assistant. Goodbye!")
                break
            
            try:
                # Process the user input
                logger.info(f"User input: {user_input}")
                
                # Run the agent
                response = agent_executor.run(input=user_input)
                
                # Display the response
                print(f"\nPersonal Assistant: {response}")
                
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                continue
                
            except Exception as e:
                logger.error(f"Error processing input: {str(e)}", exc_info=True)
                print(f"\nI'm sorry, I encountered an error while processing your request.")
                print(f"Error details: {str(e)}")
                print("Please try again with a different query.")
    
    except KeyboardInterrupt:
        print("\n\nThank you for using the Personal Assistant. Goodbye!")
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"\nAn unexpected error occurred: {str(e)}")
        print("The application will now exit.")
        sys.exit(1)

if __name__ == "__main__":
    main()