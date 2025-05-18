import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { MealieAPI } from "./api/client.js";
import { createLogger } from "./utils/logger.js";
import {
  registerRecipeResources,
  registerMealPlanResources,
  registerShoppingResources,
  registerOrganizerResources
} from "./resources/index.js";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

// Determine if we're using stdio transport
const usingStdio = process.env.MCP_TRANSPORT === 'stdio' || process.argv.includes('--stdio');

// Create logger
export const logger = createLogger({
  usingStdio,
  logLevel: process.env.LOG_LEVEL as any || 'info'
});

// Create Mealie API client
export const mealieApi = new MealieAPI({
  baseUrl: process.env.MEALIE_BASE_URL || "http://localhost:9000/api",
  apiKey: process.env.MEALIE_API_KEY || "",
});

/**
 * Creates and configures an MCP server with Mealie resources and tools
 */
export function createMcpServer() {
  const server = new McpServer({
    name: "MealieMCP",
    version: "1.0.0",
    description: "MCP server for Mealie recipe generation and meal planning",
  });

  // Log server creation
  logger.info("Creating MCP Server");
  logger.info(`Mealie API URL: ${mealieApi.baseUrl}`);

  // Register resources and tools
  registerRecipeResources(server);
  registerMealPlanResources(server);
  registerShoppingResources(server);
  registerOrganizerResources(server);

  return server;
}
