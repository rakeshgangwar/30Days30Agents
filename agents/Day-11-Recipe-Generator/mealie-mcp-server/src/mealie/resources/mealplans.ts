import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { mealieApi, logger } from "../server.js";

/**
 * Registers all meal plan related resources and tools with the MCP server
 * @param server MCP server instance
 */
export function registerMealPlanResources(server: McpServer) {
  logger.debug("Registering meal plan resources and tools");

  // ==================== RESOURCES ====================

  // Resource: Get meal plan for date range
  server.resource(
    "meal-plans",
    new ResourceTemplate("mealie://mealplans/{startDate}/{endDate}", {
      list: undefined,
    }),
    async (uri, { startDate, endDate }) => {
      try {
        const mealPlans = await mealieApi.getMealPlans(
          Array.isArray(startDate) ? startDate[0] : startDate,
          Array.isArray(endDate) ? endDate[0] : endDate
        );
        return {
          contents: [{ uri: uri.href, text: JSON.stringify(mealPlans, null, 2) }],
        };
      } catch (error) {
        logger.error(`Error fetching meal plans: ${error}`);
        return {
          contents: [
            {
              uri: uri.href,
              text: `Error fetching meal plans: ${error}`,
            },
          ],
        };
      }
    }
  );

  // Resource: Today's meal plan
  server.resource("todays-meals", "mealie://mealplans/today", async () => {
    try {
      const today = new Date().toISOString().split("T")[0];
      const todaysMeals = await mealieApi.getMealPlans(today, today);
      return {
        contents: [
          {
            uri: "mealie://mealplans/today",
            text: JSON.stringify(todaysMeals, null, 2),
          },
        ],
      };
    } catch (error) {
      logger.error(`Error fetching today's meal plans: ${error}`);
      return {
        contents: [
          {
            uri: "mealie://mealplans/today",
            text: `Error fetching today's meal plans: ${error}`,
          },
        ],
      };
    }
  });

  // ==================== TOOLS ====================

  // Tool: Generate random meal plan
  server.tool(
    "generate-random-meal",
    {
      date: z.string().regex(/^\d{4}-\d{2}-\d{2}/),
      mealType: z.enum(["breakfast", "lunch", "dinner", "snack"]).optional(),
    },
    async ({ date, mealType }) => {
      try {
        const randomMeal = await mealieApi.createRandomMealPlan({
          date,
          mealType: mealType || "dinner",
        });
        return {
          content: [
            { type: "text", text: JSON.stringify(randomMeal, null, 2) },
          ],
        };
      } catch (error: any) {
        logger.error(`Error generating random meal: ${error}`);
        return {
          content: [
            {
              type: "text",
              text: `Failed to generate random meal: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );
}
