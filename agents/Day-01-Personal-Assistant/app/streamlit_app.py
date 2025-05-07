#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Streamlit interface for the Personal Assistant.

This module provides a web interface using Streamlit for interacting
with the Personal Assistant agent.
"""

import os
import sys
import logging
import json
import streamlit as st
from dotenv import load_dotenv

# Import from the app package
from app.agent import create_agent
from app.memory import HierarchicalMemory
from app.interface_adapter import InterfaceAdapter
from app.config import UI_PORT, UI_THEME, init_user_preferences, USER_PREFERENCES_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("streamlit_interface.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Function to load user preferences
def load_user_preferences():
    try:
        if os.path.exists(USER_PREFERENCES_PATH):
            with open(USER_PREFERENCES_PATH, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading user preferences: {str(e)}")
        return {}

# Function to save user preferences
def save_user_preferences(preferences):
    try:
        os.makedirs(os.path.dirname(USER_PREFERENCES_PATH), exist_ok=True)
        with open(USER_PREFERENCES_PATH, 'w') as f:
            json.dump(preferences, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving user preferences: {str(e)}")
        return False

def main():
    # Load environment variables
    load_dotenv()

    # Check for required API keys
    required_apis = ["OPENAI_API_KEY"]
    missing_apis = [api for api in required_apis if not os.getenv(api)]

    if missing_apis:
        st.error("Error: The following required API keys are missing:")
        for api in missing_apis:
            st.error(f"  - {api}")
        st.error("Please add them to your .env file or set them as environment variables.")
        st.stop()

    # Initialize user preferences
    init_user_preferences()

    # Set page configuration
    st.set_page_config(
        page_title="Personal Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Create the interface adapter
    interface_adapter = InterfaceAdapter()

    # Initialize session state
    if "memory" not in st.session_state:
        st.session_state.memory = HierarchicalMemory()

    if "agent" not in st.session_state:
        st.session_state.agent = create_agent(verbose=False)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "session_id" not in st.session_state:
        # Generate a simple session ID
        import uuid
        st.session_state.session_id = str(uuid.uuid4())

    # Title and introduction
    st.title("Personal Assistant")
    st.markdown("""
    I can help with:
    - Weather information
    - Setting reminders and tasks
    - Answering general knowledge questions
    - Finding recent news
    """)
    
    # Sidebar for settings
    with st.sidebar:
        st.header("Settings")
        
        # Load current preferences
        preferences = load_user_preferences()
        
        # Default location preference
        default_location = st.text_input(
            "Default Location",
            value=preferences.get("default_location", "New York")
        )
        
        # Temperature unit preference
        temp_unit = st.selectbox(
            "Temperature Unit",
            options=["celsius", "fahrenheit"],
            index=0 if preferences.get("temperature_unit", "celsius") == "celsius" else 1
        )
        
        # News topics preference
        news_topics = st.multiselect(
            "News Topics of Interest",
            options=["technology", "science", "business", "health", "entertainment", "sports", "politics"],
            default=preferences.get("news_topics", ["technology", "science"])
        )
        
        # Save preferences button
        if st.button("Save Preferences"):
            updated_preferences = {
                "default_location": default_location,
                "temperature_unit": temp_unit,
                "news_topics": news_topics
            }
            
            # Preserve any other preferences not in the UI
            for key, value in preferences.items():
                if key not in updated_preferences:
                    updated_preferences[key] = value
            
            # Save the updated preferences
            if save_user_preferences(updated_preferences):
                st.success("Preferences saved successfully!")
            else:
                st.error("Failed to save preferences!")
    
    # Chat interface
    st.header("Chat")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Input area
    if prompt := st.chat_input("How can I help you today?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant thinking
        with st.chat_message("assistant"):
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("Thinking...")
            
            try:
                # Prepare input for the agent
                standardized_input = interface_adapter.standardize_input(
                    {"message": prompt, "session_id": st.session_state.session_id},
                    "streamlit"
                )
                
                # Run the agent to get a response
                agent_response = st.session_state.agent.run(input=standardized_input["message"])
                
                # Format the response for streamlit
                formatted_response = interface_adapter.format_output(
                    {"text": agent_response},
                    "streamlit"
                )
                
                # Display the response
                thinking_placeholder.markdown(formatted_response["text"])
                
                # Add assistant message to chat history
                st.session_state.messages.append({"role": "assistant", "content": formatted_response["text"]})
                
            except Exception as e:
                logger.error(f"Error processing request: {str(e)}", exc_info=True)
                error_message = f"I'm sorry, I encountered an error while processing your request: {str(e)}"
                thinking_placeholder.markdown(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

if __name__ == "__main__":
    main()