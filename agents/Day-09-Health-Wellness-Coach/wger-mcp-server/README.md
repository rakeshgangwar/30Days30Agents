# wger MCP Server

This is an MCP (Model Context Protocol) server that provides access to wger fitness data through resources and tools. It allows LLM applications to access exercise information, equipment details, and more.

## Overview

The wger MCP Server exposes the [wger](https://wger.de/) fitness API through the Model Context Protocol, making it easy for LLM applications to access fitness data and provide workout recommendations.

## Features

- Access exercise information, including details about muscles worked and equipment needed
- Search and filter exercises by various criteria
- Access nutrition information, including ingredients, meals, and nutrition plans
- Track food consumption through nutrition diary entries
- Create and manage workout routines with specific days and exercises
- Track workout sessions and log exercise performance
- Generate workout plans and exercise recommendations

## Documentation

Detailed documentation is available in the `@docs` directory:

- [Overview](@docs/overview.md) - General overview of the project
- [Resources](@docs/resources.md) - Documentation for all resources
- [Tools](@docs/tools.md) - Documentation for all tools
- [Prompts](@docs/prompts.md) - Documentation for predefined prompts
- [Models](@docs/models.md) - Documentation for data models
- [Usage](@docs/usage.md) - Usage examples

## Resources

The server provides various resources for accessing fitness data. See the [Resources documentation](@docs/resources.md) for a complete list.

### Exercise Resources

- `exercise://{id}` - Get detailed information about a specific exercise by ID
- `exercise://list` - Get a list of exercises with optional filtering

### Nutrition Resources

- `nutritionplan://{id}` - Get a specific nutrition plan by ID
- `nutritiondiary://list` - Get a list of nutrition diary entries

### Workout Resources

- `routine://{id}` - Get a specific workout routine by ID
- `workoutsession://{id}` - Get a specific workout session by ID
- `workoutlog://list` - Get a list of workout logs

## Tools

The server provides various tools for creating and managing fitness data. See the [Tools documentation](@docs/tools.md) for a complete list.

### Nutrition Tools

- `create-nutrition-plan` - Create a new nutrition plan
- `create-nutrition-diary-entry` - Create a new nutrition diary entry

### Workout Tools

- `create-routine` - Create a new workout routine
- `create-workout-session` - Create a new workout session
- `create-workout-log` - Create a new workout log entry

## Prompts

The server provides predefined prompts for common user interactions. See the [Prompts documentation](@docs/prompts.md) for a complete list.

- `create-workout-plan` - Create a personalized workout plan based on goals and availability
- `create-workout-routine` - Create a personalized workout routine
- `track-workout-session` - Track a workout session with exercises and performance

## Development

- Install dependencies: `npm install`
- Build: `npm run build`
- Run: `npm start`

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

## Usage

### Connecting to the Server

You can connect to the server using any MCP client. For example, using the MCP Inspector:

```bash
# Without environment variables
npx @modelcontextprotocol/inspector --command "node dist/server.js"

# With environment variables
WGER_API_TOKEN=your_token npx @modelcontextprotocol/inspector --command "node dist/server.js"
```

## License

This project is licensed under the MIT License.

## Acknowledgements

- [wger Workout Manager](https://wger.de/) for providing the fitness data API
- [Model Context Protocol](https://modelcontextprotocol.io/) for the protocol specification
