#!/usr/bin/env python3

"""
Test script for the Email Assistant Agent without email API integration.

This script creates a simplified version of the agent that only uses the LLM
without requiring actual email API credentials.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the email_assist package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude
from agno.tools.reasoning import ReasoningTools


def main():
    """
    Main function to test the agent without email API integration.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if API keys are set
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not (openai_api_key or anthropic_api_key):
        print("Error: No API key found. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY in your .env file.")
        return
    
    # Determine which model to use based on available API keys
    if openai_api_key:
        print("Using OpenAI model...")
        model = OpenAIChat(id="gpt-4o")
        model_name = "OpenAI GPT-4o"
    elif anthropic_api_key:
        print("Using Anthropic model...")
        model = Claude(id="claude-3-7-sonnet-latest")
        model_name = "Anthropic Claude"
    
    # Create a simple agent with reasoning tools
    agent = Agent(
        model=model,
        description="You are an email assistant that helps users manage their inbox efficiently.",
        instructions=[
            "Summarize emails concisely, focusing on key information and action items.",
            "Draft professional and contextually appropriate email replies.",
            "Prioritize emails based on importance, urgency, and required actions.",
            "Extract key information and action items from emails.",
            "Generate templates for common email scenarios.",
            "Always respect user privacy and handle email data securely.",
            "When reasoning through tasks, explain your thought process clearly."
        ],
        tools=[ReasoningTools(add_instructions=True)],
        markdown=True,
        show_tool_calls=True,
    )
    
    print(f"\nAgent created with {model_name} model.\n")
    print("This is a test agent without email API integration.")
    print("You can interact with it to test basic functionality.")
    print("Type 'exit' to quit.\n")
    
    # Simple chat loop
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        
        print(f"\nAgent: ", end="")
        response = agent.run(user_input)
        
        # Check if the response is a RunResponse object and extract the content
        if hasattr(response, 'content'):
            response = response.content
        print(response)
        print()


if __name__ == "__main__":
    main()
