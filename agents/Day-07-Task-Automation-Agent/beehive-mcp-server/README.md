# Beehive MCP Server

A Model Context Protocol (MCP) server for [Beehive](https://github.com/muesli/beehive), an event and agent system that allows you to create automated tasks triggered by events and filters.

This MCP server provides tools for AI assistants to interact with Beehive, allowing them to create, configure, and manage event-driven automation.

## What is Beehive?

Beehive is a modular, flexible automation system that allows you to:

- Set up "Bees" (instances of plugins called "Hives") that can trigger events or perform actions
- Connect events from one Bee to actions on another Bee using "Chains"
- Apply filters and transformations to events
- Create sophisticated automation flows between various services

Examples of what Beehive can do:
- Re-post tweets on your Tumblr blog
- Forward incoming chat messages to your email account
- Turn on the heating system if the temperature drops below a certain value
- Run your own IRC bot that lets you trigger builds on a Jenkins CI
- Control your Hue lighting system

## What is MCP?

The Model Context Protocol (MCP) is a standardized way for AI assistants to access external tools and resources. This server implements the MCP specification to provide AI assistants with the ability to interact with Beehive.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/beehive-mcp-server.git
   cd beehive-mcp-server
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file based on the example:
   ```bash
   cp .env.example .env
   ```

4. Edit the `.env` file to configure your server:
   ```
   # Server settings
   PORT=3000

   # Beehive API settings
   BEEHIVE_URL=http://localhost:8181
   
   # MCP server settings
   MCP_SERVER_NAME=beehive
   ```

5. Start the MCP server:
   ```bash
   npm run start:mcp
   ```

   This starts the MCP server using stdio transport, which is compatible with Cline and other MCP clients.

   If you prefer to run the legacy HTTP server (not recommended for Cline integration):
   ```bash
   npm start
   ```

## Authentication

By default, Beehive doesn't require API keys or authentication when accessed from localhost (127.0.0.1). This is because it's designed to only listen on localhost interfaces by default for security.

### Securing Beehive

If you want to secure Beehive for production use, you have several options:

1. **Use a reverse proxy with authentication**: Place Beehive behind a proxy like Nginx or Apache with authentication enabled.

2. **SSH Tunneling**: Access Beehive remotely through an SSH tunnel.

3. **Custom Authentication Implementation**: You could modify Beehive to implement an authentication system, in which case you would use the `BEEHIVE_API_KEY` setting in the `.env` file.

4. **Docker with Network Isolation**: When running Beehive in Docker, use network isolation to restrict access.

The MCP server is already prepared to use API key authentication if you implement it, by adding the API key to the Authorization header of requests.

## Connecting to Beehive

To use this MCP server, you need to have Beehive running. You can:

1. Install Beehive from the [official repository](https://github.com/muesli/beehive)
2. Or use a pre-built binary from the [releases page](https://github.com/muesli/beehive/releases)
3. Or run it using Docker: `docker run --name beehive -d -p 8181:8181 fribbledom/beehive`

Make sure to set the correct Beehive URL in your `.env` file.

## Available Tools

The Beehive MCP server provides the following tools for AI assistants:

### Hives Management

- `list_hives` - List all available Hives (plugins)
- `get_hive_details` - Get detailed information about a specific Hive

### Bees Management

- `list_bees` - List all configured Bees (instances of Hives)
- `get_bee` - Get details of a specific Bee
- `create_bee` - Create a new Bee instance
- `update_bee` - Update an existing Bee
- `delete_bee` - Delete a Bee instance

### Chains Management

- `list_chains` - List all configured Chains
- `get_chain` - Get details of a specific Chain
- `create_chain` - Create a new Chain connecting events to actions
- `update_chain` - Update an existing Chain
- `delete_chain` - Delete a Chain

### Actions

- `trigger_action` - Manually trigger an action on a Bee

## Example Usage

Here's how an AI assistant might use this MCP server:

1. First, it would check what Hives are available:
   ```
   Tool: list_hives
   Arguments: {}
   ```

2. Then, it might create a new Bee for a Twitter Hive:
   ```
   Tool: create_bee
   Arguments: {
     "name": "My Twitter Account",
     "hive": "twitter",
     "options": {
       "consumer_key": "...",
       "consumer_secret": "...",
       "access_token": "...",
       "access_token_secret": "..."
     }
   }
   ```

3. It could then create another Bee for an Email Hive:
   ```
   Tool: create_bee
   Arguments: {
     "name": "My Email Account",
     "hive": "email",
     "options": {
       "username": "user@example.com",
       "password": "...",
       "server": "smtp.example.com",
       "port": 587
     }
   }
   ```

4. Finally, it might create a Chain that forwards tweets to email:
   ```
   Tool: create_chain
   Arguments: {
     "name": "Tweet to Email",
     "event": {
       "bee": "bee_1",  // ID of the Twitter Bee
       "name": "tweet"
     },
     "actions": [
       {
         "bee": "bee_2",  // ID of the Email Bee
         "name": "send",
         "options": {
           "recipient": "recipient@example.com",
           "subject": "New Tweet",
           "text": "{{.user}} tweeted: {{.text}}"
         }
       }
     ]
   }
   ```

## Integration with Cline

To use this MCP server with Cline, you need to add it to your Cline MCP settings:

1. Open Cline and access the MCP settings (typically located at `~/.config/cline-mcp/settings.json` or in the VS Code settings)

2. Add the following configuration to the `mcpServers` object:

```json
"beehive": {
  "autoApprove": [],
  "disabled": false,
  "timeout": 60,
  "command": "node",
  "args": [
    "/path/to/beehive-mcp-server/src/beehive-mcp.js"
  ],
  "env": {
    "BEEHIVE_URL": "http://localhost:8181",
    "MCP_SERVER_NAME": "beehive"
  },
  "transportType": "stdio"
}
```

Make sure to replace `/path/to/beehive-mcp-server` with the actual path to your installation.

## Development

To run the server in development mode with auto-restart on file changes:

```bash
npm run dev
```

This will start the HTTP server, which is useful for development and testing. For MCP integration, use `npm run start:mcp` as described above.

## License

MIT
