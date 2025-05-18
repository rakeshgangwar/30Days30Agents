import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { mealieApi, logger } from "../server.js";

/**
 * Registers all shopping list related resources and tools with the MCP server
 * @param server MCP server instance
 */
export function registerShoppingResources(server: McpServer) {
  logger.debug("Registering shopping resources and tools");

  // ==================== TOOLS ====================

  // Tool: Create shopping list
  server.tool(
    "create-shopping-list",
    { name: z.string(), description: z.string().optional() },
    async ({ name, description }) => {
      try {
        const shoppingList = await mealieApi.createShoppingList({
          name,
          description,
        });
        return {
          content: [
            {
              type: "text",
              text: `Shopping list created with ID: ${shoppingList.id}\nName: ${shoppingList.name}`,
            },
          ],
        };
      } catch (error: any) {
        logger.error(`Error creating shopping list: ${error}`);
        return {
          content: [
            {
              type: "text",
              text: `Failed to create shopping list: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );

  // Tool: Add recipe to shopping list
  server.tool(
    "add-recipe-to-shopping-list",
    {
      listId: z.string(),
      recipeId: z.string(),
      servings: z.number().positive().optional(),
    },
    async ({ listId, recipeId, servings }) => {
      try {
        const result = await mealieApi.addRecipeToShoppingList(
          listId,
          recipeId,
          servings
        );
        return {
          content: [
            {
              type: "text",
              text: `Recipe added to shopping list: ${JSON.stringify(
                result,
                null,
                2
              )}`,
            },
          ],
        };
      } catch (error: any) {
        logger.error(`Error adding recipe to shopping list: ${error}`);
        return {
          content: [
            {
              type: "text",
              text: `Failed to add recipe to shopping list: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );
}
