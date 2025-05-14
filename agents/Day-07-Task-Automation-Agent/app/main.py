from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv
import asyncio
import logging
import os
import json
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize MCP server connection
server = MCPServerStdio(
    'node',
    args=[
        "/Users/rakeshgangwar/Projects/beehive-mcp-server/src/beehive-mcp.js"
    ],
    env={
        "BEEHIVE_URL": "http://localhost:8181",
        "MCP_SERVER_NAME": "beehive"
    }
)

class TaskAutomationAgent:
    """
    Task Automation Agent that utilizes Beehive MCP tools to create and manage automations.
    """
    
    def __init__(self):
        """Initialize the Task Automation Agent with the PydanticAI agent and MCP server."""
        self.agent = Agent('openai:gpt-4o', mcp_servers=[server])
        self.system_prompt = """
        You are a Task Automation Agent that helps users create and manage automations using Beehive.
        
        Available tools through the Beehive MCP server:
        
        1. Hives Management:
           - list_hives: List all available Hives (plugins)
           - get_hive_details: Get detailed information about a specific Hive
        
        2. Bees Management:
           - list_bees: List all configured Bees (instances of Hives)
           - get_bee: Get details of a specific Bee
           - create_bee: Create a new Bee instance
           - update_bee: Update an existing Bee
           - delete_bee: Delete a Bee instance
        
        3. Chains Management:
           - list_chains: List all configured Chains
           - get_chain: Get details of a specific Chain
           - create_chain: Create a new Chain connecting events to actions
           - delete_chain: Delete a Chain
        
        4. Actions:
           - trigger_action: Manually trigger an action on a Bee
        
        5. Logs:
           - get_logs: Retrieve logs from the system
        
        When a user asks to create an automation, you should:
        1. Analyze what they're trying to automate
        2. Identify any missing parameters or information
        3. Ask clarifying questions to collect all required details
        4. Use the appropriate tools to create the automation
        5. Confirm the automation was created successfully
        
        Be conversational and helpful. Guide the user through the process step by step.
        """
        
        # Initialize message history
        self.message_history = []
        self.conversation_started = False
        
    async def start_conversation(self):
        """Start a new conversation with the agent."""
        async with self.agent.run_mcp_servers():
            result = await self.agent.run(self.system_prompt)
            self.message_history = result.all_messages()
            self.conversation_started = True
            return result.output
    
    async def chat(self, user_message: str) -> str:
        """Continue a conversation with the agent."""
        if not self.conversation_started:
            await self.start_conversation()
        
        async with self.agent.run_mcp_servers():
            result = await self.agent.run(user_message, message_history=self.message_history)
            self.message_history = result.all_messages()
            return result.output
    
    async def process_automation_request(self, description: str) -> str:
        """Process an automation request in a conversational manner."""
        # Start with analyzing the request
        initial_message = f"I want to create this automation: {description}"
        
        if not self.conversation_started:
            await self.start_conversation()
        
        async with self.agent.run_mcp_servers():
            # First, provide guidance on how to approach this automation
            guidance = """
            I'll help you create this automation. Let me analyze what you're trying to do and what information we'll need.
            
            First, I need to understand:
            1. What should trigger this automation (the event)?
            2. What action should happen when triggered?
            3. Any specific parameters needed for both the trigger and action
            
            Let me analyze your request and I'll ask for any missing details.
            """
            
            # Send the initial request and guidance to the agent
            result = await self.agent.run(
                initial_message,
                message_history=self.message_history
            )
            
            self.message_history = result.all_messages()
            return result.output
    
    async def list_available_hives(self) -> str:
        """List all available Hives in Beehive."""
        message = "List all available hives in Beehive and explain what each one does."
        return await self.chat(message)
    
    async def list_current_automations(self) -> str:
        """List all current automations (chains) in Beehive."""
        message = "List all current automations in Beehive and provide a summary of each one."
        return await self.chat(message)
    
    async def delete_automation(self, automation_id: str) -> str:
        """Delete an automation by its ID."""
        message = f"Delete the automation with ID {automation_id}."
        return await self.chat(message)
    
    async def trigger_manual_action(self, bee_id: str, action_name: str, options: Optional[Dict[str, Any]] = None) -> str:
        """Manually trigger an action on a Bee."""
        options_str = json.dumps(options) if options else "{}"
        message = f"Trigger the action '{action_name}' on the Bee with ID '{bee_id}' using these options: {options_str}"
        return await self.chat(message)

# Interactive CLI for the Task Automation Agent
async def interactive_cli():
    """Run an interactive CLI session with the Task Automation Agent."""
    agent = TaskAutomationAgent()
    print("Task Automation Agent - Interactive Mode")
    print("Type 'exit' to quit, 'help' for available commands")
    
    # Start the conversation
    print("\nInitializing agent...")
    await agent.start_conversation()
    print("Agent ready! How can I help you automate tasks today?")
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            if user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("  help - Show this help message")
                print("  exit - Exit the program")
                print("  list hives - List available hives")
                print("  list automations - List current automations")
                print("  delete [id] - Delete an automation by ID")
                print("  Any other input will be processed as a conversation with the agent")
                continue
            
            if user_input.lower() == 'list hives':
                response = await agent.list_available_hives()
            elif user_input.lower() == 'list automations':
                response = await agent.list_current_automations()
            elif user_input.lower().startswith('delete '):
                automation_id = user_input[7:].strip()
                response = await agent.delete_automation(automation_id)
            elif user_input.lower().startswith('create automation:'):
                description = user_input[18:].strip()
                response = await agent.process_automation_request(description)
            else:
                response = await agent.chat(user_input)
            
            print(f"\nAgent: {response}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")

async def main():
    """Main function to demonstrate the Task Automation Agent."""
    await interactive_cli()

if __name__ == "__main__":
    asyncio.run(main())
