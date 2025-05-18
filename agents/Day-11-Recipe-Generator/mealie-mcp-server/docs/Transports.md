# Mealie MCP Server Transport Options

The Mealie MCP Server supports multiple transport options for communication between clients and the server. This document explains the available transport options, their use cases, and how to configure them.

## Overview

MCP (Model Context Protocol) servers can communicate with clients through different transport mechanisms. The Mealie MCP Server supports two transport options:

1. **HTTP Transport**: For web-based integrations and remote access
2. **stdio Transport**: For direct integration with LLM tools and command-line applications

## HTTP Transport

HTTP transport is the default option and is suitable for web-based integrations and remote access.

### Configuration

To use HTTP transport, set the `MCP_TRANSPORT` environment variable to `http` or omit it (as HTTP is the default):

```
MCP_TRANSPORT=http
```

You can also configure the port on which the HTTP server listens:

```
PORT=3000
```

### Starting with HTTP Transport

```bash
# Production (compiled)
npm run start:modular

# Development (with ts-node)
npm run dev:modular
```

### How It Works

The HTTP transport uses the Streamable HTTP transport from the MCP SDK, which provides:

1. **Session Management**: Each client gets a unique session ID
2. **Request Handling**: Processes client requests via HTTP POST
3. **Server-to-Client Notifications**: Uses Server-Sent Events (SSE) for server-initiated messages
4. **Connection Management**: Handles connection lifecycle events

The server will be available at `http://localhost:3000/mcp` (or the port you configured).

### Implementation Details

The HTTP transport is implemented in `src/mealie/transports/http.ts` and uses Express.js to handle HTTP requests. It creates a new transport for each client session and manages these transports in a session map.

```typescript
// Example of HTTP transport initialization
const app = express();
app.use(express.json());

// Map to store transports by session ID
const transports: { [sessionId: string]: StreamableHTTPServerTransport } = {};

// Handle POST requests for client-to-server communication
app.post("/mcp", async (req, res) => {
  // Check for existing session ID
  const sessionId = req.headers['mcp-session-id'] as string | undefined;
  let transport: StreamableHTTPServerTransport;

  if (sessionId && transports[sessionId]) {
    // Reuse existing transport
    transport = transports[sessionId];
  } else if (!sessionId && isInitializeRequest(req.body)) {
    // New initialization request
    transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: () => randomUUID(),
      onsessioninitialized: (sessionId) => {
        // Store the transport by session ID
        transports[sessionId] = transport;
      },
    });

    // Create and connect to MCP server
    const server = createServer();
    await server.connect(transport);
  }

  // Handle the request
  await transport.handleRequest(req, res, req.body);
});
```

## stdio Transport

stdio transport is designed for direct integration with LLM tools and command-line applications. It uses standard input/output streams for communication, making it ideal for embedding in other applications or using with tools like the MCP Inspector.

### Configuration

To use stdio transport, set the `MCP_TRANSPORT` environment variable to `stdio`:

```
MCP_TRANSPORT=stdio
```

Alternatively, you can pass the `--stdio` flag when starting the server:

```bash
node dist/mealie/index.js --stdio
```

### Starting with stdio Transport

```bash
# Production (compiled)
npm run start:modular:stdio

# Development (with ts-node)
npm run dev:modular:stdio
```

### How It Works

The stdio transport uses the StdioServerTransport from the MCP SDK, which:

1. **Reads from stdin**: Receives client requests from standard input
2. **Writes to stdout**: Sends responses and notifications to standard output
3. **Logs to stderr**: Redirects all logging to standard error to avoid interfering with the protocol

This transport is particularly useful for:
- Integration with LLM tools that spawn child processes
- Command-line applications that need to communicate with the MCP server
- Testing and debugging with tools like the MCP Inspector

### Implementation Details

The stdio transport is implemented in `src/mealie/transports/stdio.ts`. It redirects all console output to stderr to avoid interfering with the JSON-RPC protocol.

```typescript
// Example of stdio transport initialization
export async function startStdioServer(server: McpServer) {
  // Redirect all console output to stderr
  console.log = (...args) => {
    process.stderr.write(args.map(arg => String(arg)).join(' ') + '\n');
  };

  console.error = (...args) => {
    process.stderr.write('ERROR: ' + args.map(arg => String(arg)).join(' ') + '\n');
  };

  console.warn = (...args) => {
    process.stderr.write('WARNING: ' + args.map(arg => String(arg)).join(' ') + '\n');
  };

  // Create and connect to the transport
  const transport = new StdioServerTransport();
  await server.connect(transport);
}
```

### Important Notes for stdio Transport

When using stdio transport:

1. **stdout is reserved**: Standard output is reserved exclusively for MCP protocol messages
2. **Logging goes to stderr**: All logging is redirected to standard error
3. **No console.log**: Never use `console.log` in your code when using stdio transport
4. **JSON-RPC format**: All messages on stdout must be valid JSON-RPC messages

## Choosing the Right Transport

Choose the transport option based on your integration needs:

| Feature | HTTP Transport | stdio Transport |
|---------|---------------|----------------|
| Remote access | ✅ | ❌ |
| Web integration | ✅ | ❌ |
| Direct LLM tool integration | ❌ | ✅ |
| Command-line usage | ❌ | ✅ |
| Multiple concurrent clients | ✅ | ❌ |
| Session management | ✅ | ❌ |
| Performance | Good | Excellent |
| Simplicity | More complex | Simpler |

### Use HTTP Transport When:

- You need remote access to the MCP server
- You're integrating with web applications
- You need to support multiple concurrent clients
- You need session management

### Use stdio Transport When:

- You're integrating directly with LLM tools
- You're building command-line applications
- You need maximum performance
- You're testing with the MCP Inspector

## Transport Configuration in Code

The transport type is determined in the main entry point (`src/mealie/index.ts`):

```typescript
// Determine transport type from environment variable or command line argument
const useStdio = process.env.MCP_TRANSPORT === 'stdio' || process.argv.includes('--stdio');

// Start the appropriate server based on transport type
if (useStdio) {
  // For stdio transport, create the server and connect it to stdio
  const server = createMcpServer();
  startStdioServer(server);
} else {
  // For HTTP transport, pass the server factory function
  startHttpServer(createMcpServer);
}
```

## Troubleshooting

### HTTP Transport Issues

- **Port already in use**: Change the port in your `.env` file
- **CORS errors**: The server doesn't currently support CORS, so clients must be on the same origin
- **Connection timeouts**: Check network connectivity and firewall settings

### stdio Transport Issues

- **Garbled output**: Make sure you're not writing to stdout in your code
- **Protocol errors**: Ensure all messages are valid JSON-RPC messages
- **Child process issues**: Check that the process is being spawned correctly

## Testing Transports

### Testing HTTP Transport

You can test the HTTP transport using curl:

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"client":{"name":"test-client","version":"1.0.0"}},"id":1}'
```

### Testing stdio Transport

You can test the stdio transport using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector --command "node dist/mealie/index.js --stdio"
```

## Conclusion

The Mealie MCP Server provides flexible transport options to suit different integration needs. Choose HTTP transport for web-based integrations and remote access, or stdio transport for direct integration with LLM tools and command-line applications.
