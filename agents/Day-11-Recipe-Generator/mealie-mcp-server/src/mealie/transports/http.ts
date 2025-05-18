import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { randomUUID } from "node:crypto";
import express from "express";
import { logger } from "../server.js";

/**
 * Starts the MCP server with HTTP transport
 * @param createServer Function that creates an MCP server instance
 */
export function startHttpServer(createServer: () => McpServer) {
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
      logger.debug(`Using existing transport for session ${sessionId}`);
    } else if (!sessionId && isInitializeRequest(req.body)) {
      // New initialization request
      transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: () => randomUUID(),
        onsessioninitialized: (sessionId) => {
          // Store the transport by session ID
          transports[sessionId] = transport;
          logger.info(`Initialized new session: ${sessionId}`);
        },
      });
  
      // Clean up transport when closed
      transport.onclose = () => {
        if (transport.sessionId) {
          logger.info(`Closing session: ${transport.sessionId}`);
          delete transports[transport.sessionId];
        }
      };
  
      // Create and connect to MCP server
      const server = createServer();
      await server.connect(transport);
      logger.debug('Connected server to transport');
    } else {
      // Invalid request
      logger.warn('Invalid request: No valid session ID provided');
      res
        .status(400)
        .json({
          jsonrpc: "2.0",
          error: {
            code: -32000,
            message: "Bad Request: No valid session ID provided",
          },
          id: null,
        });
      return;
    }
  
    // Handle the request
    await transport.handleRequest(req, res, req.body);
  });
  
  // Reusable handler for GET and DELETE requests
  const handleSessionRequest = async (
    req: express.Request,
    res: express.Response
  ) => {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    if (!sessionId || !transports[sessionId]) {
      logger.warn(`Invalid or missing session ID: ${sessionId}`);
      res.status(400).send("Invalid or missing session ID");
      return;
    }
  
    const transport = transports[sessionId];
    await transport.handleRequest(req, res);
  };
  
  // Handle GET requests for server-to-client notifications via SSE
  app.get("/mcp", handleSessionRequest);
  
  // Handle DELETE requests for session termination
  app.delete("/mcp", handleSessionRequest);
  
  // Start server
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => {
    logger.info(`MCP Server running on HTTP transport, port ${PORT}`);
  });
}
