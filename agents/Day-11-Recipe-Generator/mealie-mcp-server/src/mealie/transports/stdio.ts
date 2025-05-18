import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { logger } from "../server.js";

/**
 * Starts the MCP server with stdio transport
 * @param server MCP server instance
 */
export async function startStdioServer(server: McpServer) {
  // Redirect all console output to stderr to avoid interfering with the JSON-RPC protocol
  console.log = (...args) => {
    process.stderr.write(args.map(arg => String(arg)).join(' ') + '\n');
  };

  console.error = (...args) => {
    process.stderr.write('ERROR: ' + args.map(arg => String(arg)).join(' ') + '\n');
  };

  console.warn = (...args) => {
    process.stderr.write('WARNING: ' + args.map(arg => String(arg)).join(' ') + '\n');
  };

  logger.info('Initializing stdio transport');

  const transport = new StdioServerTransport();

  // Connect to the transport
  try {
    await server.connect(transport);
    logger.info('MCP Server connected to stdio transport');
  } catch (error) {
    logger.error(`Error connecting to stdio transport: ${error}`);
    process.exit(1);
  }
}
