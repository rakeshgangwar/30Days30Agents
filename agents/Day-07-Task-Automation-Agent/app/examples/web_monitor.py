"""
Task Automation Agent - Web Monitor Example

This example demonstrates how to use the Task Automation Agent to set up a web monitoring task.
"""

import os
import sys
import asyncio

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.dependencies import AppDependencies
from src.main import agent

async def main():
    """Run the example."""
    # Create dependencies
    deps = AppDependencies.from_env()
    
    # Use the agent to set up a web monitor
    print("Asking the agent to set up a web monitor...")
    result = await agent.run(
        "Monitor the website 'https://example.com' for changes to the title element. "
        "When it changes, send me an email at 'user@example.com'.",
        deps=deps
    )
    print(f"Agent response: {result.output}")
    
    # Use the agent to check the status of a monitoring task
    print("\nAsking the agent to check the status of the monitoring task...")
    result = await agent.run(
        "Check the status of my website monitoring tasks.",
        deps=deps
    )
    print(f"Agent response: {result.output}")

if __name__ == "__main__":
    asyncio.run(main())
