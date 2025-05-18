import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { mealieApi, logger } from "../server.js";

/**
 * Registers all organizer (categories, tags) related resources with the MCP server
 * @param server MCP server instance
 */
export function registerOrganizerResources(server: McpServer) {
  logger.debug("Registering organizer resources");

  // ==================== RESOURCES ====================

  // Resource: Recipe categories
  server.resource("categories", "mealie://categories", async () => {
    try {
      const categories = await mealieApi.getCategories();
      return {
        contents: [
          {
            uri: "mealie://categories",
            text: JSON.stringify(categories, null, 2),
          },
        ],
      };
    } catch (error) {
      logger.error(`Error fetching categories: ${error}`);
      return {
        contents: [
          {
            uri: "mealie://categories",
            text: `Error fetching categories: ${error}`,
          },
        ],
      };
    }
  });

  // Resource: Recipe tags
  server.resource("tags", "mealie://tags", async () => {
    try {
      const tags = await mealieApi.getTags();
      return {
        contents: [
          {
            uri: "mealie://tags",
            text: JSON.stringify(tags, null, 2),
          },
        ],
      };
    } catch (error) {
      logger.error(`Error fetching tags: ${error}`);
      return {
        contents: [
          {
            uri: "mealie://tags",
            text: `Error fetching tags: ${error}`,
          },
        ],
      };
    }
  });

  // Resource: Ingredient units
  server.resource("units", "mealie://units", async () => {
    try {
      const units = await mealieApi.getUnits();
      return {
        contents: [
          {
            uri: "mealie://units",
            text: JSON.stringify(units, null, 2),
          },
        ],
      };
    } catch (error) {
      logger.error(`Error fetching units: ${error}`);
      return {
        contents: [
          {
            uri: "mealie://units",
            text: `Error fetching units: ${error}`,
          },
        ],
      };
    }
  });

  // ==================== TOOLS ====================

  // Tool: Get units
  server.tool(
    "get-units",
    {},
    async () => {
      try {
        const units = await mealieApi.getUnits();
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(units, null, 2),
            },
          ],
        };
      } catch (error: any) {
        logger.error(`Error fetching units: ${error}`);
        return {
          content: [
            {
              type: "text",
              text: `Failed to fetch units: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );

  // Tool: Find unit by name
  server.tool(
    "find-unit",
    { name: z.string() },
    async ({ name }) => {
      try {
        const units = await mealieApi.getUnits();
        const matchedUnit = units.find(u =>
          u.name.toLowerCase() === name.toLowerCase() ||
          (u.abbreviation && u.abbreviation.toLowerCase() === name.toLowerCase())
        );

        if (matchedUnit) {
          return {
            content: [
              {
                type: "text",
                text: JSON.stringify(matchedUnit, null, 2),
              },
            ],
          };
        } else {
          return {
            content: [
              {
                type: "text",
                text: `No unit found with name or abbreviation: ${name}`,
              },
            ],
            isError: true,
          };
        }
      } catch (error: any) {
        logger.error(`Error finding unit: ${error}`);
        return {
          content: [
            {
              type: "text",
              text: `Failed to find unit: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );
}
