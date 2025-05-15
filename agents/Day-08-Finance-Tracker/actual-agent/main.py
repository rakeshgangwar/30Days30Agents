import asyncio

from finance_agent import run_finance_agent

async def main():
    print("Welcome to the Actual Finance Agent!")
    print("Ask a question or type 'exit' to quit.")

    while True:
        user_input = input("\nYour question: ")
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("Goodbye!")
            break

        print("\nConnecting to Actual MCP server and processing your request...")
        # Call the async function directly instead of using the sync wrapper
        response = await run_finance_agent(user_input)
        print("\nResponse:")
        print("-" * 50)
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
