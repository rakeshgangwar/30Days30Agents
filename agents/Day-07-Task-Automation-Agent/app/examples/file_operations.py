"""
Task Automation Agent - File Operations Example

This example demonstrates how to use the Task Automation Agent to perform file operations.
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
    
    # Create a sample file
    with open("sample.txt", "w") as f:
        f.write("This is a sample file.\nIt has multiple lines.\nWe will use it for testing.")
    
    print("Created sample.txt file.")
    
    # Use the agent to read the file
    print("\nAsking the agent to read the file...")
    result = await agent.run(
        "Read the contents of the file 'sample.txt' and tell me how many lines it has.",
        deps=deps
    )
    print(f"Agent response: {result.output}")
    
    # Use the agent to write to a file
    print("\nAsking the agent to create a new file...")
    result = await agent.run(
        "Create a new file called 'output.txt' with the current date and time.",
        deps=deps
    )
    print(f"Agent response: {result.output}")
    
    # Use the agent to list files
    print("\nAsking the agent to list files in the current directory...")
    result = await agent.run(
        "List all the text files in the current directory.",
        deps=deps
    )
    print(f"Agent response: {result.output}")
    
    # Clean up
    if os.path.exists("sample.txt"):
        os.remove("sample.txt")
    if os.path.exists("output.txt"):
        os.remove("output.txt")
    
    print("\nCleaned up test files.")

if __name__ == "__main__":
    asyncio.run(main())
