from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from dotenv import load_dotenv

load_dotenv()

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
agent = Agent('openai:gpt-4o', mcp_servers=[server])

async def main():
    async with agent.run_mcp_servers():
        result = await agent.run("List all the hives available on Beehive")
    print(result.output)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
