# Task Automation Agent

This is a Task Automation Agent that combines PydanticAI for intelligent processing and Beehive for event-driven task execution, integrated via an MCP server.

## Features

- Natural language understanding of task descriptions
- Task decomposition into smaller steps
- Interaction with APIs or web interfaces
- Workflow execution and monitoring
- Scheduling of automated tasks

## Installation

1. Clone the repository
2. Navigate to the app directory
3. Create a virtual environment and install dependencies:

```bash
cd agents/Day-07-Task-Automation-Agent/app
uv init
uv add pydantic-ai pydantic requests python-dotenv streamlit
```

4. Copy the `.env.example` file to `.env` and fill in your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

## PydanticAI Implementation

This project uses PydanticAI's recommended patterns:

- **Agent Definition**: We define a single agent with tools as decorators
- **RunContext**: Tools receive a `RunContext` object for dependency injection
- **ModelRetry**: We use `ModelRetry` for proper error handling and self-correction
- **Async Support**: All tools support async operation for better performance

## Usage

### Command Line Interface

Run the agent from the command line:

```bash
python src/main.py
```

### Streamlit UI

Run the Streamlit UI:

```bash
streamlit run src/ui/streamlit_app.py
```

## Project Structure

- `src/`: Main source code
  - `models/`: Pydantic models for task representation
  - `beehive/`: Beehive integration components
  - `ui/`: User interface components
  - `main.py`: Main entry point with agent definition and tools
- `examples/`: Example scripts demonstrating agent usage
  - `file_operations.py`: Example of file operations
  - `web_monitor.py`: Example of web monitoring

## Example Tasks

- "Check my unread emails, summarize important ones, and draft replies."
- "Monitor this website for price drops on product X and notify me."
- "Every morning, get the weather forecast and send it to my Slack channel."
- "Extract data from this PDF table and save it to a CSV file."
- "Rename all files in this folder to include today's date."

## Running Examples

Try out the examples to see the agent in action:

```bash
# Run the file operations example
python examples/file_operations.py

# Run the web monitor example
python examples/web_monitor.py
```

## Beehive Integration

This agent integrates with Beehive via the MCP server for event-driven task execution. You'll need to have the [beehive-mcp-server](https://github.com/rakeshgangwar/beehive-mcp-server) running to use these features.

## License

MIT