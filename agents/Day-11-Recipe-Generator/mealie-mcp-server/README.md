# Mealie MCP Server

An MCP (Model Context Protocol) server for Mealie recipe management and meal planning.

## Overview

This server provides MCP-compatible access to a Mealie recipe management system, allowing LLMs to:
- Browse and search recipes
- Create new recipes
- Generate meal plans
- Create shopping lists
- Parse ingredients
- And more!

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   npm install
   ```
3. Copy `.env.example` to `.env` and configure your Mealie API settings:
   ```
   cp .env.example .env
   ```
4. Build the project:
   ```
   npm run build
   ```

## Configuration

Edit the `.env` file to configure:
- `MEALIE_BASE_URL`: URL of your Mealie API (default: http://localhost:9000/api)
- `MEALIE_API_KEY`: Your Mealie API key
- `PORT`: Port for HTTP transport (default: 3000)
- `MCP_TRANSPORT`: Transport type (`http` or `stdio`)

## Running the Server

This project provides two implementations of the MCP server:
1. **Original Implementation** - A single-file implementation
2. **Modular Implementation** - A modular, more maintainable implementation

### Original Implementation

#### HTTP Transport (Default)

Run the server with HTTP transport (accessible via HTTP endpoints):

```bash
# Production (compiled)
npm start

# Development (with ts-node)
npm run dev
```

The server will be available at `http://localhost:3000/mcp` (or the port you configured).

#### stdio Transport

Run the server with stdio transport (for direct integration with LLM tools):

```bash
# Production (compiled)
npm run start:stdio

# Development (with ts-node)
npm run dev:stdio
```

### Modular Implementation (Recommended)

The modular implementation separates concerns into different files for better maintainability.

#### HTTP Transport (Default)

```bash
# Production (compiled)
npm run start:modular

# Development (with ts-node)
npm run dev:modular
```

#### stdio Transport

```bash
# Production (compiled)
npm run start:modular:stdio

# Development (with ts-node)
npm run dev:modular:stdio
```

### Transport Configuration

You can also set the transport type in your `.env` file:
```
MCP_TRANSPORT=stdio
```

Or pass it as a command-line argument:
```
node dist/index.js --stdio
# or for modular implementation
node dist/mealie/index.js --stdio
```

#### Notes on stdio Transport

When using stdio transport:
- All console output is redirected to stderr to avoid interfering with the JSON-RPC protocol
- stdout is reserved exclusively for MCP protocol messages
- You can still see logs in the terminal, but they come from stderr instead of stdout
- This is necessary because the MCP client expects only valid JSON messages on stdout

## Available Resources

- `mealie://recipes/list` - List all recipes
- `mealie://recipes/{slug}` - Get recipe by slug
- `mealie://mealplans/{startDate}/{endDate}` - Get meal plans for date range
- `mealie://mealplans/today` - Get today's meal plan
- `mealie://categories` - List recipe categories
- `mealie://tags` - List recipe tags

## Available Tools

- `create-recipe-from-url` - Create a recipe from a URL
- `parse-ingredients` - Parse ingredient text into structured data
- `generate-random-meal` - Generate a random meal plan for a date
- `create-shopping-list` - Create a new shopping list
- `add-recipe-to-shopping-list` - Add a recipe to a shopping list
- `suggest-recipes` - Get recipe suggestions based on ingredients

## Testing

For testing the MCP server, you can use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).
