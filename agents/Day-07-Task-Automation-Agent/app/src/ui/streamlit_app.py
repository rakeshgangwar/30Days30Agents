"""
Task Automation Agent - Streamlit UI

This module provides a Streamlit-based user interface for the Task Automation Agent.
"""

import os
import sys
import asyncio
import streamlit as st
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user_task import TaskResult
from models.dependencies import AppDependencies
from main import agent, process_user_input

# Load environment variables
load_dotenv()

async def run_agent(user_input: str) -> TaskResult:
    """Run the agent with the given user input."""
    return await process_user_input(user_input)

def main():
    """Main function for the Streamlit app."""
    st.set_page_config(
        page_title="Task Automation Agent",
        page_icon="🤖",
        layout="wide",
    )

    st.title("Task Automation Agent")
    st.markdown("""
    This agent can automate various tasks based on your instructions.
    It can interact with files, APIs, and set up automated workflows.
    """)

    # Input for task description
    user_input = st.text_area(
        "What task would you like me to automate?",
        height=100,
        placeholder="E.g., 'Check my unread emails and summarize them' or 'Monitor this website for price drops'"
    )

    # Process the task when the user submits
    if st.button("Process Task"):
        if not user_input:
            st.error("Please enter a task description.")
        else:
            with st.spinner("Processing your task..."):
                try:
                    # Use asyncio to run the async function
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(run_agent(user_input))

                    # Display the results
                    st.subheader("Task Results")
                    st.write(f"Success: {result.success}")
                    st.write(f"Summary: {result.summary}")

                    if result.error:
                        st.error(f"Error: {result.error}")

                    # Display detailed results if available
                    if result.results:
                        st.subheader("Detailed Results")
                        for i, res in enumerate(result.results):
                            st.write(f"Result {i+1}:")
                            st.code(str(res))

                except Exception as e:
                    st.error(f"Error processing task: {str(e)}")

if __name__ == "__main__":
    main()
