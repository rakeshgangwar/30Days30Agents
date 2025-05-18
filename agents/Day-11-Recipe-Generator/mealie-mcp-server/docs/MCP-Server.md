# Mealie MCP Server Documentation

## Introduction

The Mealie MCP Server is an implementation of the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) that provides LLMs (Large Language Models) with access to a Mealie recipe management system. This server acts as a bridge between LLMs and the Mealie API, allowing AI assistants to browse, search, create, and manage recipes, meal plans, and shopping lists.

## Architecture Overview

The Mealie MCP Server is built with a modular architecture that consists of the following components:

1. **Core Server**: Creates and configures the MCP server with resources and tools
2. **API Client**: Communicates with the Mealie API
3. **Resources**: Exposes Mealie data through MCP resources
4. **Tools**: Provides functionality for interacting with Mealie
5. **Transports**: Supports different communication methods (HTTP and stdio)

### Directory Structure

```
src/
├── mealie/
│   ├── api/                  # Mealie API client and types
│   │   ├── client.ts         # API client implementation
│   │   ├── index.ts          # API module exports
│   │   └── types.ts          # TypeScript interfaces for API data
│   ├── resources/            # MCP resources and tools
│   │   ├── index.ts          # Resource module exports
│   │   ├── mealplans.ts      # Meal plan resources and tools
│   │   ├── organizers.ts     # Category/tag resources and tools
│   │   ├── recipes.ts        # Recipe resources and tools
│   │   └── shopping.ts       # Shopping list resources and tools
│   ├── transports/           # MCP transport implementations
│   │   ├── http.ts           # HTTP transport
│   │   ├── index.ts          # Transport module exports
│   │   └── stdio.ts          # stdio transport
│   ├── utils/                # Utility functions
│   │   ├── index.ts          # Utility module exports
│   │   └── logger.ts         # Transport-aware logger
│   ├── index.ts              # Main entry point
│   └── server.ts             # MCP server configuration
```

## Installation

### Prerequisites

- Node.js 18 or higher
- npm or yarn
- A running Mealie instance with API access

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/mealie-mcp-server.git
   cd mealie-mcp-server
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file with your Mealie API settings:
   ```
   MEALIE_BASE_URL=http://your-mealie-instance:9000/api
   MEALIE_API_KEY=your-api-key
   PORT=3000
   MCP_TRANSPORT=http
   ```

5. Build the project:
   ```bash
   npm run build
   ```

## Configuration

The server can be configured through environment variables or command-line arguments:

| Variable | Description | Default |
|----------|-------------|---------|
| `MEALIE_BASE_URL` | URL of your Mealie API | `http://localhost:9000/api` |
| `MEALIE_API_KEY` | Your Mealie API key | (required) |
| `PORT` | Port for HTTP transport | `3000` |
| `MCP_TRANSPORT` | Transport type (`http` or `stdio`) | `http` |
| `LOG_LEVEL` | Minimum log level (`debug`, `info`, `warn`, `error`) | `info` |

## Running the Server

The server can be run in different modes depending on your needs:

### HTTP Transport (Default)

HTTP transport is suitable for remote access and integration with web applications.

```bash
# Production (compiled)
npm run start:modular

# Development (with ts-node)
npm run dev:modular
```

The server will be available at `http://localhost:3000/mcp` (or the port you configured).

### stdio Transport

stdio transport is designed for direct integration with LLM tools and command-line applications.

```bash
# Production (compiled)
npm run start:modular:stdio

# Development (with ts-node)
npm run dev:modular:stdio
```

## Available Resources

The server exposes the following MCP resources:

| Resource URI | Description |
|--------------|-------------|
| `mealie://recipes/list` | List all recipes |
| `mealie://recipes/{slug}` | Get recipe by slug |
| `mealie://mealplans/{startDate}/{endDate}` | Get meal plans for date range |
| `mealie://mealplans/today` | Get today's meal plan |
| `mealie://categories` | List recipe categories |
| `mealie://tags` | List recipe tags |
| `mealie://units` | List ingredient units |

## Available Tools

The server provides the following MCP tools:

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `get-recipe` | Get a recipe by slug | `slug`: Recipe slug |
| `create-recipe-from-url` | Create a recipe from a URL | `url`: Recipe URL |
| `parse-ingredients` | Parse ingredient text into structured data | `ingredients`: Array of ingredient strings |
| `create-recipe` | Create a basic recipe | `name`: Recipe name, `description`: Optional description |
| `update-recipe` | Update an existing recipe | `slug`: Recipe slug, plus recipe fields to update |
| `generate-random-meal` | Generate a random meal plan | `date`: Date (YYYY-MM-DD), `mealType`: Optional meal type |
| `create-shopping-list` | Create a new shopping list | `name`: List name, `description`: Optional description |
| `add-recipe-to-shopping-list` | Add a recipe to a shopping list | `listId`: Shopping list ID, `recipeId`: Recipe ID |
| `suggest-recipes` | Get recipe suggestions | `foods`: Optional array of available foods, `limit`: Optional result limit |
| `get-units` | Get all available ingredient units | (none) |

## API Reference

### Recipe Resources

#### List Recipes

```
Resource URI: mealie://recipes/list
```

Returns a list of all recipes in the Mealie database.

#### Get Recipe by Slug

```
Resource URI: mealie://recipes/{slug}
```

Returns detailed information about a specific recipe.

### Meal Plan Resources

#### Get Meal Plans for Date Range

```
Resource URI: mealie://mealplans/{startDate}/{endDate}
```

Returns meal plans for the specified date range. Dates should be in YYYY-MM-DD format.

#### Get Today's Meal Plan

```
Resource URI: mealie://mealplans/today
```

Returns the meal plan for the current day.

### Organizer Resources

#### List Categories

```
Resource URI: mealie://categories
```

Returns a list of all recipe categories.

#### List Tags

```
Resource URI: mealie://tags
```

Returns a list of all recipe tags.

#### List Units

```
Resource URI: mealie://units
```

Returns a list of all ingredient units.

## Examples

### Creating a Recipe from a URL

```javascript
// Using the MCP client
const result = await client.callTool({
  name: "create-recipe-from-url",
  arguments: {
    url: "https://example.com/recipe"
  }
});
```

### Generating a Random Meal Plan

```javascript
// Using the MCP client
const result = await client.callTool({
  name: "generate-random-meal",
  arguments: {
    date: "2023-05-15",
    mealType: "dinner"
  }
});
```

### Parsing Ingredients

```javascript
// Using the MCP client
const result = await client.callTool({
  name: "parse-ingredients",
  arguments: {
    ingredients: [
      "2 cups flour",
      "1 tsp salt",
      "3 tbsp butter, softened"
    ]
  }
});
```

## Troubleshooting

### Common Issues

#### Connection Refused

If you see a "Connection refused" error, check that:
- Your Mealie instance is running
- The `MEALIE_BASE_URL` is correct
- There are no network issues or firewalls blocking the connection

#### Authentication Failed

If you see an "Authentication failed" error, check that:
- Your `MEALIE_API_KEY` is correct
- The API key has not expired
- The API key has the necessary permissions

#### Transport Issues

If you're having issues with the transport:
- For HTTP transport, check that the port is not in use by another application
- For stdio transport, ensure you're not writing to stdout in your application code

## Testing

For testing the MCP server, you can use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

## License

This project is licensed under the MIT License.
