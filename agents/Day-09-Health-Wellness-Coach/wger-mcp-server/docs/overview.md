# wger MCP Server

## Overview

The wger MCP Server is an implementation of the Model Context Protocol (MCP) that provides access to the wger fitness API. It allows LLM applications to access fitness data, nutrition information, and workout tracking functionality through standardized resources and tools.

## Project Structure

The project is organized into several TypeScript modules, each responsible for a specific domain of the wger API:

- `server.ts`: Main server configuration and initialization
- `exercises.ts`: Exercise-related resources and tools
- `nutrition.ts`: Nutrition plan and diary resources and tools
- `ingredients.ts`: Ingredient resources and tools
- `meals.ts`: Meal resources and tools
- `routines.ts`: Workout routines, sessions, and logs resources and tools
- `settings.ts`: User settings and configuration resources

## Configuration

The server can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `WGER_API_BASE_URL` | Base URL for the wger API | `https://wger.de/api/v2` |
| `WGER_API_TOKEN` | API token for authenticated requests to wger | `""` (empty string) |

You can set these variables in a `.env` file or directly in your environment.

To use a `.env` file:

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your actual values:
   ```
   WGER_API_BASE_URL=https://wger.de/api/v2
   WGER_API_TOKEN=your_actual_token_here
   ```

## Features

The wger MCP Server provides the following features:

- Access to exercise information, including details about muscles worked and equipment needed
- Search and filter exercises by various criteria
- Access to nutrition information, including ingredients, meals, and nutrition plans
- Tracking of food consumption through nutrition diary entries
- Access to workout routines, sessions, and logs
- Creation and management of workout plans
- Tracking of workout performance

## Installation

To install the wger MCP Server:

```bash
# Clone the repository
git clone https://github.com/your-username/wger-mcp-server.git
cd wger-mcp-server

# Install dependencies
npm install

# Build the project
npm run build
```

## Running the Server

To run the server:

```bash
# Start the server
npm start
```

You can also run the server with environment variables:

```bash
# With environment variables
WGER_API_TOKEN=your_token npm start
```

## Connecting to the Server

You can connect to the server using any MCP client. For example, using the MCP Inspector:

```bash
# Without environment variables
npx @modelcontextprotocol/inspector --command "node dist/server.js"

# With environment variables
WGER_API_TOKEN=your_token npx @modelcontextprotocol/inspector --command "node dist/server.js"
```

## Documentation

For more detailed documentation, see:

- [Resources](@docs/resources.md): Documentation for all resources
- [Tools](@docs/tools.md): Documentation for all tools
- [Prompts](@docs/prompts.md): Documentation for predefined prompts
- [Models](@docs/models.md): Documentation for data models
- [Usage](@docs/usage.md): Usage examples
