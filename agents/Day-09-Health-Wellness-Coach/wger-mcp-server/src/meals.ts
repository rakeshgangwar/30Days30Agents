import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import fetch from "node-fetch";

// Helper function to make API requests to wger
async function fetchWgerApi(endpoint: string, params: Record<string, string | undefined> = {}, options: any = {}) {
  const WGER_API_BASE_URL = process.env.WGER_API_BASE_URL || "https://wger.de/api/v2";
  const WGER_API_TOKEN = process.env.WGER_API_TOKEN || "";

  const url = new URL(`${WGER_API_BASE_URL}${endpoint}`);

  // Add query parameters
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.append(key, value.toString());
    }
  });

  // Prepare headers
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Add authorization token if available
  if (WGER_API_TOKEN) {
    headers['Authorization'] = `Token ${WGER_API_TOKEN}`;
  }

  try {
    const response = await fetch(url.toString(), {
      method: options.method || 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`Error fetching from wger API: ${error}`);
    throw error;
  }
}

// Register meal resources and tools with the server
export function registerMealResources(server: McpServer) {
  // ==================== RESOURCES ====================

  // Meal List Resource
  server.resource(
    "meal-list",
    new ResourceTemplate("meal://list{?limit,offset,order,ordering,plan,time}", { list: undefined }),
    async (uri, params) => {
      try {
        // Convert params to Record<string, string | undefined>
        const queryParams: Record<string, string | undefined> = {};
        Object.entries(params).forEach(([key, value]) => {
          if (Array.isArray(value)) {
            queryParams[key] = value.join(',');
          } else {
            queryParams[key] = value;
          }
        });

        const mealData = await fetchWgerApi("/meal/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(mealData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching meals: ${error}`
          }]
        };
      }
    }
  );

  // Meal Item Resource
  server.resource(
    "meal-item",
    new ResourceTemplate("meal://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const mealItemData = await fetchWgerApi(`/meal/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(mealItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching meal: ${error}`
          }]
        };
      }
    }
  );

  // Meal Nutritional Values Resource
  server.resource(
    "meal-nutritional-values",
    new ResourceTemplate("meal://{id}/nutritional_values", { list: undefined }),
    async (uri, { id }) => {
      try {
        const nutritionalValuesData = await fetchWgerApi(`/meal/${id}/nutritional_values/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(nutritionalValuesData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching meal nutritional values: ${error}`
          }]
        };
      }
    }
  );

  // Meal Item List Resource
  server.resource(
    "mealitem-list",
    new ResourceTemplate("mealitem://list{?amount,ingredient,limit,meal,offset,order,ordering,weight_unit}", { list: undefined }),
    async (uri, params) => {
      try {
        // Convert params to Record<string, string | undefined>
        const queryParams: Record<string, string | undefined> = {};
        Object.entries(params).forEach(([key, value]) => {
          if (Array.isArray(value)) {
            queryParams[key] = value.join(',');
          } else {
            queryParams[key] = value;
          }
        });

        const mealItemData = await fetchWgerApi("/mealitem/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(mealItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching meal items: ${error}`
          }]
        };
      }
    }
  );

  // Meal Item Item Resource
  server.resource(
    "mealitem-item",
    new ResourceTemplate("mealitem://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const mealItemItemData = await fetchWgerApi(`/mealitem/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(mealItemItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching meal item: ${error}`
          }]
        };
      }
    }
  );

  // Meal Item Nutritional Values Resource
  server.resource(
    "mealitem-nutritional-values",
    new ResourceTemplate("mealitem://{id}/nutritional_values", { list: undefined }),
    async (uri, { id }) => {
      try {
        const nutritionalValuesData = await fetchWgerApi(`/mealitem/${id}/nutritional_values/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(nutritionalValuesData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching meal item nutritional values: ${error}`
          }]
        };
      }
    }
  );

  // ==================== TOOLS ====================

  // Create Meal Tool
  server.tool(
    "create-meal",
    {
      plan: z.number().int().positive().describe("Nutrition plan ID"),
      name: z.string().max(25).optional().describe("Name of the meal (e.g., 'Breakfast', 'Lunch')"),
      time: z.string().optional().describe("Time of the meal in HH:MM format (optional)")
    },
    async ({ plan, name, time }) => {
      try {
        const requestBody = {
          plan,
          ...(name && { name }),
          ...(time && { time })
        };

        const response = await fetchWgerApi("/meal/", {}, {
          method: 'POST',
          body: requestBody
        });

        return {
          content: [{
            type: "text",
            text: JSON.stringify(response, null, 2)
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error creating meal: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Update Meal Tool
  server.tool(
    "update-meal",
    {
      id: z.number().int().positive().describe("Meal ID"),
      plan: z.number().int().positive().optional().describe("Nutrition plan ID"),
      name: z.string().max(25).optional().describe("Name of the meal (e.g., 'Breakfast', 'Lunch')"),
      time: z.string().optional().describe("Time of the meal in HH:MM format (optional)")
    },
    async ({ id, plan, name, time }) => {
      try {
        const requestBody: Record<string, any> = {};
        if (plan) requestBody.plan = plan;
        if (name) requestBody.name = name;
        if (time !== undefined) requestBody.time = time;

        const response = await fetchWgerApi(`/meal/${id}/`, {}, {
          method: 'PATCH',
          body: requestBody
        });

        return {
          content: [{
            type: "text",
            text: JSON.stringify(response, null, 2)
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error updating meal: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Meal Tool
  server.tool(
    "delete-meal",
    {
      id: z.number().int().positive().describe("Meal ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/meal/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted meal with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting meal: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // // Get Meal Nutritional Values Tool
  // server.tool(
  //   "get-meal-nutritional-values",
  //   {
  //     id: z.number().int().positive().describe("Meal ID")
  //   },
  //   async ({ id }) => {
  //     try {
  //       const nutritionalValuesData = await fetchWgerApi(`/meal/${id}/nutritional_values/`);

  //       return {
  //         content: [{
  //           type: "text",
  //           text: JSON.stringify(nutritionalValuesData, null, 2)
  //         }]
  //       };
  //     } catch (error) {
  //       return {
  //         content: [{
  //           type: "text",
  //           text: `Error fetching meal nutritional values: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // Create Meal Item Tool
  server.tool(
    "create-meal-item",
    {
      meal: z.number().int().positive().describe("Meal ID"),
      ingredient: z.number().int().positive().describe("Ingredient ID"),
      amount: z.string().describe("Amount of the ingredient"),
      weight_unit: z.number().int().positive().optional().describe("Weight unit ID (optional)")
    },
    async ({ meal, ingredient, amount, weight_unit }) => {
      try {
        const requestBody = {
          meal,
          ingredient,
          amount,
          ...(weight_unit && { weight_unit })
        };

        const response = await fetchWgerApi("/mealitem/", {}, {
          method: 'POST',
          body: requestBody
        });

        return {
          content: [{
            type: "text",
            text: JSON.stringify(response, null, 2)
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error creating meal item: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Update Meal Item Tool
  server.tool(
    "update-meal-item",
    {
      id: z.number().int().positive().describe("Meal item ID"),
      meal: z.number().int().positive().optional().describe("Meal ID"),
      ingredient: z.number().int().positive().optional().describe("Ingredient ID"),
      amount: z.string().optional().describe("Amount of the ingredient"),
      weight_unit: z.number().int().positive().optional().describe("Weight unit ID (optional)")
    },
    async ({ id, meal, ingredient, amount, weight_unit }) => {
      try {
        const requestBody: Record<string, any> = {};
        if (meal) requestBody.meal = meal;
        if (ingredient) requestBody.ingredient = ingredient;
        if (amount) requestBody.amount = amount;
        if (weight_unit !== undefined) requestBody.weight_unit = weight_unit;

        const response = await fetchWgerApi(`/mealitem/${id}/`, {}, {
          method: 'PATCH',
          body: requestBody
        });

        return {
          content: [{
            type: "text",
            text: JSON.stringify(response, null, 2)
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error updating meal item: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Meal Item Tool
  server.tool(
    "delete-meal-item",
    {
      id: z.number().int().positive().describe("Meal item ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/mealitem/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted meal item with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting meal item: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // // Get Meal Item Nutritional Values Tool
  // server.tool(
  //   "get-meal-item-nutritional-values",
  //   {
  //     id: z.number().int().positive().describe("Meal item ID")
  //   },
  //   async ({ id }) => {
  //     try {
  //       const nutritionalValuesData = await fetchWgerApi(`/mealitem/${id}/nutritional_values/`);

  //       return {
  //         content: [{
  //           type: "text",
  //           text: JSON.stringify(nutritionalValuesData, null, 2)
  //         }]
  //       };
  //     } catch (error) {
  //       return {
  //         content: [{
  //           type: "text",
  //           text: `Error fetching meal item nutritional values: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // ==================== PROMPTS ====================

  // Plan Meal Prompt
  server.prompt(
    "plan-meal",
    "Plan a meal with specific nutritional goals",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I want to plan a high-protein breakfast meal. I'm aiming for about 30g of protein, moderate carbs, and low fat. Can you suggest some ingredients and amounts that would make a good breakfast meal?"
          }
        }]
      };
    }
  );

  // Analyze Meal Nutrition Prompt
  server.prompt(
    "analyze-meal-nutrition",
    "Analyze the nutritional content of a meal",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I've created a meal with 2 eggs, 100g of oatmeal, 200ml of milk, and a banana. Can you analyze the nutritional content of this meal and tell me the total calories, protein, carbs, and fat?"
          }
        }]
      };
    }
  );
}
