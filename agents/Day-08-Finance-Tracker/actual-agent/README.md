# Actual Finance Agent

A simple AI agent for Actual Finance that can answer questions about personal finance and provide information about Actual Finance features.

## Features

- Answer general questions about personal finance
- Provide information about Actual Finance features and capabilities
- Calculate compound interest with customizable parameters
- Interactive command-line interface

## Usage

### Running the Agent

To run the agent interactively:

```bash
python main.py
```

This will start an interactive session where you can ask questions and get responses from the agent.

### Using the Agent in Your Code

You can also import and use the agent in your own Python code:

```python
from finance_agent import run_finance_agent

# Ask a question
response = run_finance_agent("What is Actual Finance?")
print(response)

# Calculate compound interest
response = run_finance_agent("Calculate compound interest on $1000 at 5% for 10 years")
print(response)
```

## Available Tools

The agent has the following tools available:

### Compound Interest Calculator

Calculate compound interest with various parameters:

- Principal amount (initial investment)
- Interest rate (as a decimal, e.g., 0.05 for 5%)
- Time period (in years)
- Compounding frequency (number of times per year)

Example query: "Calculate compound interest on $5000 at 7% for 15 years compounded quarterly"

### Actual Finance Information

Get information about Actual Finance and its features:

- General information
- Features
- Self-hosting
- Budgeting approach

Example query: "Tell me about Actual Finance's features"

## Development

### Adding New Tools

To add new tools to the agent, edit the `finance_agent.py` file and add new functions decorated with `@finance_agent.tool`.

Example:

```python
@finance_agent.tool
def new_tool(ctx: RunContext[None], param1: str, param2: int) -> str:
    """
    Description of what the tool does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of the return value
    """
    # Tool implementation
    return "Result"
```

## Requirements

- Python 3.12+
- pydantic-ai>=0.2.4

## Development Notes

### Test Mode vs. Production Mode

The agent is currently configured to use a test model for development purposes. In test mode, the agent will return all tool outputs as a JSON object rather than intelligently selecting which tool to use based on the query.

To use a real model in production:

1. Set up the appropriate API keys as environment variables:
   - For OpenAI: `OPENAI_API_KEY`
   - For Anthropic: `ANTHROPIC_API_KEY`

2. Update the model in `finance_agent.py`:
   ```python
   finance_agent = Agent(
       'anthropic:claude-3-5-sonnet-latest',  # or 'openai:gpt-4o'
       system_prompt=(
           # system prompt here
       )
   )
   ```

The test model is useful for development and testing the structure of your agent without incurring API costs.