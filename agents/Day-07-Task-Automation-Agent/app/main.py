from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from dotenv import load_dotenv
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.providers.openai import OpenAIProvider
import asyncio
import logging
import os
import json
import re
from datetime import datetime
from pydantic_ai.messages import (
    FinalResultEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    PartDeltaEvent,
    PartStartEvent,
    TextPartDelta,
    ToolCallPartDelta,
)

model = OpenAIModel(model_name="deepseek-chat", provider=DeepSeekProvider(api_key=os.getenv("DEEPSEEK_API_KEY")))
openrouter = OpenAIModel(model_name="google/gemini-2.5-flash-preview", provider=OpenAIProvider(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY")))

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
        self.agent = Agent(
            model=openrouter,
            mcp_servers=[server],
            instrument=True
        )
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
        logger.info("Starting new conversation")
        async with self.agent.run_mcp_servers():
            result = await self.agent.run(self.system_prompt)
            self.message_history = result.all_messages()
            self.conversation_started = True
            return result.output
    
    async def chat(self, user_message: str) -> str:
        """Continue a conversation with the agent."""
        logger.info(f"Processing chat message: {user_message[:50]}...")
        if not self.conversation_started:
            await self.start_conversation()
        
        async with self.agent.run_mcp_servers():
            result = await self.agent.run(user_message, message_history=self.message_history)
            self.message_history = result.all_messages()
            return result.output
    
    async def chat_with_streaming(self, user_message: str):
        """Continue a conversation with the agent with streaming output."""
        logger.info(f"Processing streaming chat message: {user_message[:50]}...")
        if not self.conversation_started:
            await self.start_conversation()
        
        async with self.agent.run_mcp_servers():
            # Begin a node-by-node, streaming iteration
            async with self.agent.iter(user_message, message_history=self.message_history) as run:
                print("\nAgent: ", end="", flush=True)
                async for node in run:
                    if Agent.is_user_prompt_node(node):
                        # User prompt node - no need to display this as we already show user input
                        pass
                    elif Agent.is_model_request_node(node):
                        # Model request node - stream tokens from the model's request
                        async with node.stream(run.ctx) as request_stream:
                            async for event in request_stream:
                                if isinstance(event, PartStartEvent):
                                    # A new part is starting (e.g., text or tool call)
                                    pass
                                elif isinstance(event, PartDeltaEvent):
                                    if isinstance(event.delta, TextPartDelta):
                                        # Print text deltas in real-time
                                        print(event.delta.content_delta, end="", flush=True)
                                    elif isinstance(event.delta, ToolCallPartDelta):
                                        # Tool call is being constructed
                                        pass
                                elif isinstance(event, FinalResultEvent):
                                    # Final result from this node
                                    pass
                    elif Agent.is_call_tools_node(node):
                        # Call tools node - the model is calling tools
                        async with node.stream(run.ctx) as handle_stream:
                            async for event in handle_stream:
                                if isinstance(event, FunctionToolCallEvent):
                                    # Tool is being called
                                    print(f"\n[Calling tool: {event.part.tool_name}]", end="", flush=True)
                                elif isinstance(event, FunctionToolResultEvent):
                                    # Tool returned a result
                                    print(f"\n[Tool result received]", end="", flush=True)
                    elif Agent.is_end_node(node):
                        # End node - the agent run is complete
                        self.message_history = run.result.all_messages()
                print("\n", flush=True)  # Add a newline at the end
                return run.result.output
    
    async def process_automation_request(self, description: str) -> str:
        """Process an automation request in a conversational manner."""
        # Start with analyzing the request
        initial_message = f"I want to create this automation: {description}"
        logger.info(f"Processing automation request: {description[:50]}...")
        
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
    
    async def process_automation_request_with_streaming(self, description: str):
        """Process an automation request in a conversational manner with streaming output."""
        # Start with analyzing the request
        initial_message = f"I want to create this automation: {description}"
        logger.info(f"Processing streaming automation request: {description[:50]}...")
        
        if not self.conversation_started:
            await self.start_conversation()
        
        return await self.chat_with_streaming(initial_message)
    
    async def list_available_hives(self) -> str:
        """List all available Hives in Beehive."""
        logger.info("Listing available hives")
        message = "List all available hives in Beehive and explain what each one does."
        return await self.chat(message)
    
    async def list_current_automations(self) -> str:
        """List all current automations (chains) in Beehive."""
        logger.info("Listing current automations")
        message = "List all current automations in Beehive and provide a summary of each one."
        return await self.chat(message)
    
    async def delete_automation(self, automation_id: str) -> str:
        """Delete an automation by its ID."""
        logger.info(f"Deleting automation with ID: {automation_id}")
        message = f"Delete the automation with ID {automation_id}."
        return await self.chat(message)
    
    async def trigger_manual_action(self, bee_id: str, action_name: str, options: Optional[Dict[str, Any]] = None) -> str:
        """Manually trigger an action on a Bee."""
        options_str = json.dumps(options) if options else "{}"
        logger.info(f"Triggering action '{action_name}' on bee '{bee_id}'")
        message = f"Trigger the action '{action_name}' on the Bee with ID '{bee_id}' using these options: {options_str}"
        return await self.chat(message)

# Interactive CLI for the Task Automation Agent
async def interactive_cli():
    """Run an interactive CLI session with the Task Automation Agent."""
    agent = TaskAutomationAgent()
    print("Task Automation Agent - Interactive Mode")
    print("Type 'exit' to quit, 'help' for available commands")
    print("Streaming mode is enabled - you'll see responses as they're generated")
    
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
                print(f"\nAgent: {response}")
            elif user_input.lower() == 'list automations':
                response = await agent.list_current_automations()
                print(f"\nAgent: {response}")
            elif user_input.lower().startswith('delete '):
                automation_id = user_input[7:].strip()
                response = await agent.delete_automation(automation_id)
                print(f"\nAgent: {response}")
            elif user_input.lower().startswith('create automation:'):
                description = user_input[18:].strip()
                await agent.process_automation_request_with_streaming(description)
            else:
                await agent.chat_with_streaming(user_input)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error in interactive CLI: {str(e)}", exc_info=True)
            print(f"\nError: {str(e)}")

async def main():
    """Main function to demonstrate the Task Automation Agent."""
    await interactive_cli()

if __name__ == "__main__":
    asyncio.run(main())
