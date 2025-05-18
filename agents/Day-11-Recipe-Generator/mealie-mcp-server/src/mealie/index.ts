/**
 * Main entry point for the Mealie MCP server
 */
import { createMcpServer, logger } from "./server.js";
import { startStdioServer } from "./transports/stdio.js";
import { startHttpServer } from "./transports/http.js";

// Determine transport type from environment variable or command line argument
const useStdio = process.env.MCP_TRANSPORT === 'stdio' || process.argv.includes('--stdio');

// Log startup
logger.info(`Starting Mealie MCP server with ${useStdio ? 'stdio' : 'HTTP'} transport`);

// Start the appropriate server based on transport type
if (useStdio) {
  // For stdio transport, create the server and connect it to stdio
  const server = createMcpServer();
  startStdioServer(server);
} else {
  // For HTTP transport, pass the server factory function
  startHttpServer(createMcpServer);
}
