# FreshRSS MCP Server

A Model Context Protocol server for interacting with FreshRSS feeds via the Google Reader API.

This TypeScript-based MCP server allows AI assistants to interact with your FreshRSS instance, enabling them to:

- List and browse your RSS feeds
- Fetch unread items
- Mark items as read/unread
- Get items from specific feeds

## Features

### Tools

- `list_feeds` - List all feed subscriptions
- `get_feed_groups` - Get feed groups
- `get_unread` - Get unread items
- `get_feed_items` - Get items from a specific feed
- `mark_item_read` - Mark an item as read
- `mark_item_unread` - Mark an item as unread
- `mark_feed_read` - Mark all items in a feed as read
- `get_items` - Get specific items by their IDs

## Requirements

- A running FreshRSS instance with API access enabled
- API endpoint URL, username, and password for your FreshRSS instance

## Development

Install dependencies:
```bash
npm install
```

Build the server:
```bash
npm run build
```

For development with auto-rebuild:
```bash
npm run watch
```

### Environment Variables

You need to set the following environment variables:

- `FRESHRSS_API_URL`: URL to your FreshRSS instance (e.g., "https://rss.example.com")
- `FRESHRSS_USERNAME`: Your FreshRSS username
- `FRESHRSS_PASSWORD`: Your FreshRSS password

## Installation

To use with Claude Desktop, add the server config:

On MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "freshrss": {
      "command": "node",
      "args": ["/path/to/freshrss-server/build/index.js"],
      "env": {
        "FRESHRSS_API_URL": "https://your-freshrss-instance.com",
        "FRESHRSS_USERNAME": "your-username",
        "FRESHRSS_PASSWORD": "your-password"
      }
    }
  }
}
```

For Cline MCP integration, add to your MCP settings:

```json
{
  "mcpServers": {
    "freshrss": {
      "command": "node",
      "args": ["/path/to/freshrss-server/build/index.js"],
      "env": {
        "FRESHRSS_API_URL": "https://your-freshrss-instance.com",
        "FRESHRSS_USERNAME": "your-username",
        "FRESHRSS_PASSWORD": "your-password"
      }
    }
  }
}
```

### Debugging

Since MCP servers communicate over stdio, debugging can be challenging. We recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector), which is available as a package script:

```bash
npm run inspector
```

The Inspector will provide a URL to access debugging tools in your browser.

## Security Note

This server requires your FreshRSS credentials. For security:
- Never commit your credentials to version control
- Always use environment variables for sensitive information
- Consider using a dedicated FreshRSS account with appropriate permissions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.
