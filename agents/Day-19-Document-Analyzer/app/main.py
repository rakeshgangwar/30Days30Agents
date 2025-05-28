import asyncio

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

from dotenv import load_dotenv

load_dotenv()

server = MCPServerStdio(  
    'markitdown-mcp',
    args=[]
)

agent = Agent('openai:gpt-4o', mcp_servers=[server])


async def main():
    async with agent.run_mcp_servers():
        result = await agent.run('Provide me transcipt of this video https://www.youtube.com/watch?v=PVwmBhYIQ8A')
    print(result.output)
    #> There are 9,208 days between January 1, 2000, and March 18, 2025.


if __name__ == '__main__':
    asyncio.run(main())