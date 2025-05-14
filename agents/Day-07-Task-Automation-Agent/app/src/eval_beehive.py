"""
Beehive MCP Integration Evaluation

This script evaluates the Task Automation Agent's ability to use the Beehive MCP server.
"""

import os
import json
import asyncio
from pydantic_ai import Agent, RunContext, ModelRetry, AgentEval
from pydantic_ai.mcp import MCPServerStdio
from models.dependencies import AppDependencies

# Create the MCP server configuration
beehive_config = {
    "autoApprove": [],
    "disabled": False,
    "timeout": 60,
    "command": "node",
    "args": ["/Users/rakeshgangwar/Projects/beehive-mcp-server/src/beehive-mcp.js"],
    "env": {
        "BEEHIVE_URL": "http://localhost:8181",
        "MCP_SERVER_NAME": "beehive"
    },
    "transportType": "stdio"
}

# Create the MCP server
command = beehive_config.get("command", "node")
args = beehive_config.get("args", [])
env_vars = beehive_config.get("env", {})

# Merge with current environment
full_env = os.environ.copy()
full_env.update(env_vars)

# Create the MCP server
beehive_server = MCPServerStdio(
    command=command,
    args=args,
    env=full_env
)

# Create the agent
agent = Agent(
    os.getenv("MODEL_NAME", "openai:gpt-4o"),
    deps_type=AppDependencies,
    output_type=str,
    system_prompt="You are a task automation agent that helps users automate repetitive tasks. "
                 "You can interact with files, APIs, and set up automated workflows using Beehive. "
                 "You have access to Beehive MCP tools like list_hives, get_hive_details, list_bees, "
                 "create_bee, update_bee, delete_bee, list_chains, create_chain, update_chain, "
                 "delete_chain, and trigger_action. Use these tools to interact with the Beehive system.",
    mcp_servers=[beehive_server]
)

# Create the eval
eval = AgentEval(
    agent=agent,
    log_level="DEBUG",  # Set to DEBUG for detailed logs
    log_to_stdout=True  # Print logs to stdout
)

# Test cases
test_cases = [
    {
        "input": "List all available hives in Beehive",
        "expected_output": None  # We don't know what the output should be yet
    },
    {
        "input": "What tools are available through the Beehive MCP server?",
        "expected_output": None
    }
]

async def run_eval():
    """Run the evaluation."""
    print("Starting Beehive MCP integration evaluation...")
    
    # Create dependencies
    deps = AppDependencies.from_env()
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest case {i+1}: {test_case['input']}")
        
        try:
            # Run the agent with the MCP server
            async with agent.run_mcp_servers():
                result = await eval.evaluate_single(
                    test_case["input"],
                    expected_output=test_case["expected_output"],
                    deps=deps
                )
                
                print(f"Result: {result.output}")
                print(f"Tool calls: {result.tool_calls}")
                print(f"Success: {result.success}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_eval())
