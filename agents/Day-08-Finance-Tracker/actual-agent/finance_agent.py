"""
Finance Agent for Actual Finance

This module implements a simple agent that can answer questions about personal finance
and provide information about Actual Finance.
"""

import os
import logging
import json
from typing import Optional, Any, Dict, List
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPServerStdio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("finance_agent_mcp")

# Create a wrapper for MCPServerStdio to log all MCP calls
# class LoggingMCPServerStdio(MCPServerStdio):
#     """
#     A wrapper around MCPServerStdio that logs all MCP calls and handles
#     specific errors gracefully.
#     """

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         logger.info(f"Initialized MCP server with args: {args}, kwargs: {kwargs}")
#         self.server_ready = False
#         self.budget_loaded = False

#     async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
#         """Log tool calls and their responses with enhanced error handling."""
#         logger.info(f"MCP Tool Call: {tool_name} with args: {json.dumps(args, default=str)}")
#         try:
#             # For queries, check if we have a budget loaded
#             if tool_name == "runQuery" and not self.budget_loaded:
#                 # Try to explicitly verify server and budget status
                
#                 if not self.budget_loaded:
#                     logger.error("Cannot run query - no budget is loaded")
#                     return {
#                         "content": [{
#                             "type": "text",
#                             "text": "No budget is currently loaded. Please open a budget in Actual Finance first."
#                         }],
#                         "isError": True
#                     }
            
#             response = await super().call_tool(tool_name, args)
            
#             # Check for error in response
#             if "isError" in response and response["isError"] and "content" in response:
#                 content_text = response["content"][0]["text"] if response["content"] else ""
#                 if "No budget file is open" in content_text:
#                     self.budget_loaded = False
#                     logger.error(f"Budget access error: {content_text}")
                
#             logger.info(f"MCP Tool Response: {json.dumps(response, default=str)}")
#             return response
#         except Exception as e:
#             error_message = str(e)
#             logger.error(f"MCP Tool Error: {tool_name} - {error_message}")
            
#             # Handle specific errors
#             if "No budget file is open" in error_message:
#                 self.budget_loaded = False
#                 return {
#                     "content": [{
#                         "type": "text",
#                         "text": "No budget is currently loaded. Please open a budget in Actual Finance first."
#                     }],
#                     "isError": True
#                 }
            
#             # For any other errors, provide a user-friendly error message
#             return {
#                 "content": [{
#                     "type": "text",
#                     "text": f"Error executing {tool_name}: {error_message}"
#                 }],
#                 "isError": True
#             }

#     async def list_resources(self, uri_template: str) -> List[Dict[str, Any]]:
#         """Log resource listing calls and their responses with enhanced error handling."""
#         logger.info(f"MCP List Resources: {uri_template}")
#         try:
#             resources = await super().list_resources(uri_template)
#             logger.info(f"MCP List Resources Response: {json.dumps(resources, default=str)}")
#             return resources
#         except Exception as e:
#             error_message = str(e)
#             logger.error(f"MCP List Resources Error: {uri_template} - {error_message}")
            
#             # Return empty array instead of raising exception
#             logger.info(f"Returning empty resource list due to error")
#             return []

#     async def get_resource(self, uri: str) -> Dict[str, Any]:
#         """Log resource retrieval calls and their responses with enhanced error handling."""
#         logger.info(f"MCP Get Resource: {uri}")
#         try:
#             resource = await super().get_resource(uri)
#             logger.info(f"MCP Get Resource Response: {json.dumps(resource, default=str)}")
#             return resource
#         except Exception as e:
#             error_message = str(e)
#             logger.error(f"MCP Get Resource Error: {uri} - {error_message}")
            
#             # Return empty resource instead of raising exception
#             return {
#                 "contents": [{
#                     "uri": uri,
#                     "text": f"Error accessing resource: {error_message}. Please ensure you have a budget open in Actual Finance."
#                 }]
#             }

load_dotenv()

# For testing purposes, we'll use a mock model if no API key is available
# In production, you would use a real model like 'anthropic:claude-3-5-sonnet-latest'
# or 'openai:gpt-4o' with proper API keys set in environment variables

# Determine which model to use based on available API keys
model_name = 'test'  # Default to test model

# Check for Anthropic API key
if os.environ.get('ANTHROPIC_API_KEY'):
    model_name = 'anthropic:claude-3-5-sonnet-latest'
# Check for OpenAI API key if Anthropic is not available
elif os.environ.get('OPENAI_API_KEY'):
    model_name = 'openai:gpt-4o'
# Check for OpenRouter API key if neither Anthropic nor OpenAI is available
elif os.environ.get('OPENROUTER_API_KEY'):
    model_name = OpenAIModel(
        model_name="anthropic/claude-3.7-sonnet",
        provider=OpenAIProvider(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"]
        )
    )

# Get the current directory for relative paths
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # Parent directory of the agent directory

server = MCPServerStdio(
    command="node",
    args=[
        os.path.join(parent_dir, "actual-mcp/dist/server.js")
    ],
    env={
        "ACTUAL_SERVER_URL": "http://localhost:5006",
        "ACTUAL_PASSWORD": "password",
        # Add extra environment variables to help with debugging
        # "DEBUG": "1",
        # "NODE_ENV": "development"
    },
    # cwd=parent_dir  # Set working directory to parent (project root) folder
)
logger.info("Created MCP server for Actual Finance")

# Create a simple finance agent
finance_agent = Agent(
    model_name,
    system_prompt=(
        "You are a helpful financial assistant for Actual Finance, a personal finance app. "
        "Your goal is to provide accurate and helpful information about personal finance "
        "and budgeting. You can also provide information about Actual Finance features. "
        "Be concise, accurate, and helpful in your responses.\n\n"

        "You have access to the Actual Finance MCP (Model Context Protocol) server, which allows you to "
        "interact with the user's budget data. Below is a guide on how to use the available resources and tools:\n\n"

        "## MCP RESOURCES\n"
        "These are accessed using get_resource() with the URI format:\n\n"

        "1. **Accounts**\n"
        "   - List all accounts: `accounts://list`\n"
        "   - Get account details: `accounts://{accountId}` (includes balance)\n\n"

        "2. **Categories**\n"
        "   - List all categories: `categories://list`\n"
        "   - List category groups with nested categories: `category-groups://list`\n\n"

        "3. **Budget Information**\n"
        "   - List all budget months: `budget-months://list`\n"
        "   - Get budget details for a specific month: `budget-month://{month}` (format: YYYY-MM)\n\n"

        "4. **Transactions**\n"
        "   - Get transactions for an account in a date range: `transactions://{accountId}/{startDate}/{endDate}`\n"
        "   - Date format: YYYY-MM-DD\n\n"

        "5. **Payees**\n"
        "   - List all payees: `payees://list`\n\n"

        "## MCP TOOLS\n"
        "These are accessed using call_tool() with the tool name and appropriate parameters:\n\n"

        "1. **Account Management**\n"
        "   - `createAccount`: Create a new account with name, type, and optional initial balance\n"
        "   - `updateAccount`: Update an existing account's properties\n"
        "   - `closeAccount`: Close an account and optionally transfer remaining balance\n"
        "   - `deleteAccount`: Delete an account\n\n"

        "2. **Transaction Management**\n"
        "   - `addTransactions`: Add transactions to an account (limited to 2 transactions per request)\n"
        "   - `importTransactions`: Import transactions with optional imported_id to avoid duplicates\n"
        "   - `updateTransaction`: Update a transaction's properties\n"
        "   - `deleteTransaction`: Delete a transaction\n\n"

        "3. **Category Management**\n"
        "   - `createCategory`: Create a new category in a specified group\n"
        "   - `updateCategory`: Update a category's properties\n"
        "   - `deleteCategory`: Delete a category\n\n"

        "4. **Budget Management**\n"
        "   - `setBudgetAmount`: Set a budget amount for a category in a specific month\n"
        "   - `setBudgetCarryover`: Enable or disable budget carryover for a category\n\n"

        # "5. **Query Tool**\n"
        # "   - `runQuery`: Run an ActualQL query\n"
        # "   - IMPORTANT: When using runQuery, you must use proper ActualQL syntax, NOT resource URIs\n"
        # "   - Correct format: `q('table_name').select('*')` or other valid ActualQL expressions\n"
        # "   - Example: `q('transactions').select('*')` to get all transactions\n"
        # "   - Example: `q('accounts').select('*')` to get all accounts\n"
        # "   - Example: `q('transactions').filter({'category.name': 'Food'}).select('*')` for filtered transactions\n"
        # "   - DO NOT use formats like `accounts://list` with runQuery as they will cause syntax errors\n\n"

        "## IMPORTANT NOTES\n"
        "1. All monetary amounts in the API are in the smallest currency unit (cents/paise)\n"
        "   - Convert to dollars/rupees when presenting to the user (divide by 100)\n"
        "   - Example: 50000 cents = $500.00 or ₹500.00\n\n"

        "2. Date formats:\n"
        "   - Use YYYY-MM-DD for transaction dates\n"
        "   - Use YYYY-MM for budget months\n\n"

        "3. Transaction processing:\n"
        "   - The addTransactions tool can only process 2 transactions per request\n"
        "   - For bulk imports, batch transactions in groups of 2\n\n"

        # "4. Error handling:\n"
        # "   - If you encounter errors with runQuery, check your query syntax\n"
        # "   - For resource access, use resource URIs directly, not through runQuery\n\n"

        "When the user asks about their financial data, use the appropriate MCP resources and tools "
        "to retrieve and present the information. Always format monetary values appropriately and provide "
        "clear, helpful explanations of the financial data."
    ),
    mcp_servers=[server]
)


async def run_finance_agent(query: str) -> str:
    """
    Run the finance agent with a given query.

    Args:
        query: The user's question or request

    Returns:
        The agent's response
    """
    logger.info(f"Running finance agent with query: {query}")
    # Start the MCP server before running the agent
    async with finance_agent.run_mcp_servers():
        logger.info("MCP servers started")
        
        try:
            # Give the server more time to initialize
            # import asyncio
            # logger.info("Waiting for MCP server initialization...")
            # await asyncio.sleep(3)  # Increased wait time
            
            # Get the MCP server instance and verify it's ready with retries
            # mcp_server = finance_agent.mcp_servers[0]
            #
            # # Try multiple times to verify server readiness
            # max_retries = 3
            # server_verified = False
            # for attempt in range(max_retries):
            #     try:
            #         logger.info(f"Verifying server ready (attempt {attempt+1}/{max_retries})...")
            #         await mcp_server._verify_server_ready()
            #         server_verified = True
            #         logger.info(f"Server verification succeeded on attempt {attempt+1}")
            #         break
            #     except Exception as init_error:
            #         logger.warning(f"Server verification attempt {attempt+1} failed: {str(init_error)}")
            #         if attempt < max_retries - 1:
            #             logger.info(f"Waiting before retry...")
            #             await asyncio.sleep(1)
            #
            # if not server_verified:
            #     logger.error("Failed to verify server readiness after multiple attempts")
            #     return "I'm having trouble connecting to the Actual Finance server. Please make sure it's running correctly."
            #
            # # Check if we have a budget loaded
            # if not mcp_server.budget_loaded:
            #     logger.warning("No budget is loaded. Queries that require budget access may fail.")
            #     # Expanded detection for finance-related queries
            #     financial_keywords = ["account", "budget", "transaction", "category", "balance", "money",
            #                          "fetch", "show", "get", "list", "display", "find", "spending"]
            #     if any(word in query.lower() for word in financial_keywords):
            #         return "I cannot access your financial data because there is no budget file open. Please open a budget in Actual Finance first."
            #
            # For any query, wrap in try-except to catch budget access errors
            try:
                # Run the agent with the query
                result = await finance_agent.run(query)
                logger.info("Finance agent run completed successfully")
                return result.output
            except Exception as run_error:
                error_message = str(run_error)
                logger.error(f"Error during agent run: {error_message}")
                
                if "No budget file is open" in error_message:
                    return "I cannot access your financial data because there is no budget file open. Please open a budget in Actual Finance first."
                else:
                    return f"Error: {error_message}"
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error running finance agent: {error_message}")
            
            # Handle budget errors gracefully
            if "No budget file is open" in error_message:
                return "I cannot access your financial data because there is no budget file open. Please open a budget in Actual Finance first."
            else:
                return f"Sorry, I encountered an error: {error_message}"
        finally:
            logger.info("MCP servers will be stopped")

def run_finance_agent_sync(query: str) -> str:
    """
    Run the finance agent synchronously with a given query.

    This is a convenience wrapper around run_finance_agent for
    synchronous code.

    Args:
        query: The user's question or request

    Returns:
        The agent's response
    """
    logger.info(f"Running finance agent synchronously with query: {query}")
    import asyncio
    try:
        result = asyncio.run(run_finance_agent(query))
        logger.info("Synchronous finance agent run completed")
        return result
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error in synchronous finance agent run: {error_message}")
        
        # Return a helpful error message instead of raising
        if "No budget file is open" in error_message:
            return "I cannot access your financial data because there is no budget file open. Please open a budget in Actual Finance first."
        else:
            return f"Sorry, I encountered an error: {error_message}"


if __name__ == "__main__":
    # Example usage
    logger.info("Starting finance agent example")
    sample_queries = [
        "What is Actual Finance?",
        "How does compound interest work?",
        "Calculate compound interest on $1000 at 5% for 10 years",
        "What features does Actual Finance have?",
        # MCP-related queries that should trigger MCP calls
        "Show me a list of all my accounts in Actual Finance",
        "What categories do I have in my budget?",
        "Show me my budget for this month",
        "What transactions do I have in my accounts?",
        "Can you create a new budget category for 'Travel' in my 'Usual Expenses' group?",
    ]

    for i, query in enumerate(sample_queries):
        logger.info(f"Processing example query {i+1}/{len(sample_queries)}")
        print(f"\nQuery: {query}")
        print("-" * 50)
        try:
            response = run_finance_agent_sync(query)
            print(response)
        except Exception as e:
            logger.error(f"Error processing example query: {str(e)}")
            print(f"Error: {str(e)}")
        print("=" * 50)

    logger.info("Finance agent example completed")
