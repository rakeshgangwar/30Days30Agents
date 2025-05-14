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

# Run the Beehive MCP example
python examples/beehive_mcp_example.py
```

## Evaluations

The Task Automation Agent includes a comprehensive evaluation framework built on Pydantic Evals. This framework allows you to:

1. Generate test datasets for different types of tasks
2. Run evaluations on the agent's performance
3. Analyze the results using custom evaluators

### Running Evaluations

To run evaluations on the agent:

```bash
# Generate an example dataset
python scripts/generate_example_dataset.py

# Run evaluations using the example dataset
python scripts/run_evals.py

# Run evaluations with custom parameters
python scripts/run_evals.py --dataset data/evals/example_dataset.yaml --output data/evals/report.yaml --concurrency 2
```

### Custom Evaluators

The evaluation framework includes several custom evaluators:

- **SuccessEvaluator**: Checks if the task was completed successfully
- **ToolUsageEvaluator**: Verifies if the expected tools were used
- **PerformanceEvaluator**: Measures the execution time against the expected timeout
- **LLMResultEvaluator**: Uses an LLM to judge the quality of the task result

## Beehive Integration

This agent integrates with Beehive via the MCP server for event-driven task execution. You'll need to have the [beehive-mcp-server](https://github.com/rakeshgangwar/beehive-mcp-server) running to use these features.

### MCP Server Integration

The agent uses the Model Context Protocol (MCP) to communicate with the Beehive server. This is implemented using the `MCPServerStdio` class from PydanticAI, which runs the server as a subprocess and communicates with it over stdin/stdout.

To use the Beehive MCP server:

1. Make sure you have the Beehive MCP server installed and configured
2. Install the MCP dependencies:

```bash
uv add "pydantic-ai-slim[mcp]" "mcp[cli]"
```

3. Run the example:

```bash
python examples/beehive_mcp_example.py
```

The Beehive MCP server configuration is defined in the `BeehiveMCPServer` class in `src/beehive/mcp_server.py`. You can customize this configuration to match your Beehive MCP server setup.

## License

MIT