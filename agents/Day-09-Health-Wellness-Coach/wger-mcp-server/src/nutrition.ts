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

// Register nutrition resources and tools with the server
export function registerNutritionResources(server: McpServer) {
  // ==================== RESOURCES ====================

  // Nutrition Diary List Resource
  server.resource(
    "nutritiondiary-list",
    new ResourceTemplate("nutritiondiary://list{?amount,datetime,datetime__date,datetime__gt,datetime__gte,datetime__lt,datetime__lte,ingredient,limit,offset,ordering,plan,weight_unit}", { list: undefined }),
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

        const nutritionDiaryData = await fetchWgerApi("/nutritiondiary/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(nutritionDiaryData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching nutrition diary: ${error}`
          }]
        };
      }
    }
  );

  // Nutrition Diary Item Resource
  server.resource(
    "nutritiondiary-item",
    new ResourceTemplate("nutritiondiary://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const nutritionDiaryItemData = await fetchWgerApi(`/nutritiondiary/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(nutritionDiaryItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching nutrition diary item: ${error}`
          }]
        };
      }
    }
  );

  // Nutrition Diary Nutritional Values Resource
  server.resource(
    "nutritiondiary-nutritional-values",
    new ResourceTemplate("nutritiondiary://{id}/nutritional_values", { list: undefined }),
    async (uri, { id }) => {
      try {
        const nutritionalValuesData = await fetchWgerApi(`/nutritiondiary/${id}/nutritional_values/`);
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
            text: `Error fetching nutrition diary nutritional values: ${error}`
          }]
        };
      }
    }
  );

  // Nutrition Plan List Resource
  server.resource(
    "nutritionplan-list",
    new ResourceTemplate("nutritionplan://list{?creation_date,description,has_goal_calories,limit,offset,ordering}", { list: undefined }),
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

        const nutritionPlanData = await fetchWgerApi("/nutritionplan/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(nutritionPlanData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching nutrition plans: ${error}`
          }]
        };
      }
    }
  );

  // Nutrition Plan Item Resource
  server.resource(
    "nutritionplan-item",
    new ResourceTemplate("nutritionplan://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const nutritionPlanItemData = await fetchWgerApi(`/nutritionplan/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(nutritionPlanItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching nutrition plan: ${error}`
          }]
        };
      }
    }
  );

  // Nutrition Plan Nutritional Values Resource
  server.resource(
    "nutritionplan-nutritional-values",
    new ResourceTemplate("nutritionplan://{id}/nutritional_values", { list: undefined }),
    async (uri, { id }) => {
      try {
        const nutritionalValuesData = await fetchWgerApi(`/nutritionplan/${id}/nutritional_values/`);
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
            text: `Error fetching nutrition plan nutritional values: ${error}`
          }]
        };
      }
    }
  );

  // Nutrition Plan Info List Resource
  server.resource(
    "nutritionplaninfo-list",
    new ResourceTemplate("nutritionplaninfo://list{?creation_date,description,has_goal_calories,limit,offset,ordering}", { list: undefined }),
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

        const nutritionPlanInfoData = await fetchWgerApi("/nutritionplaninfo/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(nutritionPlanInfoData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching nutrition plan info: ${error}`
          }]
        };
      }
    }
  );

  // Nutrition Plan Info Item Resource
  server.resource(
    "nutritionplaninfo-item",
    new ResourceTemplate("nutritionplaninfo://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const nutritionPlanInfoItemData = await fetchWgerApi(`/nutritionplaninfo/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(nutritionPlanInfoItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching nutrition plan info: ${error}`
          }]
        };
      }
    }
  );

  // Nutrition Plan Info Nutritional Values Resource
  server.resource(
    "nutritionplaninfo-nutritional-values",
    new ResourceTemplate("nutritionplaninfo://{id}/nutritional_values", { list: undefined }),
    async (uri, { id }) => {
      try {
        const nutritionalValuesData = await fetchWgerApi(`/nutritionplaninfo/${id}/nutritional_values/`);
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
            text: `Error fetching nutrition plan info nutritional values: ${error}`
          }]
        };
      }
    }
  );

  // ==================== TOOLS ====================

  // Create Nutrition Diary Entry Tool
  server.tool(
    "create-nutrition-diary-entry",
    {
      plan: z.number().int().positive().describe("Nutrition plan ID"),
      ingredient: z.number().int().positive().describe("Ingredient ID"),
      amount: z.string().describe("Amount of the ingredient"),
      datetime: z.string().describe("Date and time of consumption (ISO format)"),
      meal: z.number().int().positive().optional().describe("Meal ID (optional)"),
      weight_unit: z.number().int().positive().optional().describe("Weight unit ID (optional)")
    },
    async ({ plan, ingredient, amount, datetime, meal, weight_unit }) => {
      try {
        const requestBody = {
          plan,
          ingredient,
          amount,
          datetime,
          ...(meal && { meal }),
          ...(weight_unit && { weight_unit })
        };

        const response = await fetchWgerApi("/nutritiondiary/", {}, {
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
            text: `Error creating nutrition diary entry: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Update Nutrition Diary Entry Tool
  server.tool(
    "update-nutrition-diary-entry",
    {
      id: z.number().int().positive().describe("Nutrition diary entry ID"),
      plan: z.number().int().positive().describe("Nutrition plan ID"),
      ingredient: z.number().int().positive().describe("Ingredient ID"),
      amount: z.string().describe("Amount of the ingredient"),
      datetime: z.string().describe("Date and time of consumption (ISO format)"),
      meal: z.number().int().positive().optional().describe("Meal ID (optional)"),
      weight_unit: z.number().int().positive().optional().describe("Weight unit ID (optional)")
    },
    async ({ id, plan, ingredient, amount, datetime, meal, weight_unit }) => {
      try {
        const requestBody = {
          plan,
          ingredient,
          amount,
          datetime,
          ...(meal && { meal }),
          ...(weight_unit && { weight_unit })
        };

        const response = await fetchWgerApi(`/nutritiondiary/${id}/`, {}, {
          method: 'PUT',
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
            text: `Error updating nutrition diary entry: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Nutrition Diary Entry Tool
  server.tool(
    "delete-nutrition-diary-entry",
    {
      id: z.number().int().positive().describe("Nutrition diary entry ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/nutritiondiary/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted nutrition diary entry with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting nutrition diary entry: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Create Nutrition Plan Tool
  server.tool(
    "create-nutrition-plan",
    {
      description: z.string().max(80).optional().describe("Description of the nutrition plan"),
      only_logging: z.boolean().optional().describe("Whether the plan is only for logging"),
      goal_energy: z.number().int().optional().describe("Goal energy in kcal"),
      goal_protein: z.number().int().optional().describe("Goal protein in g"),
      goal_carbohydrates: z.number().int().optional().describe("Goal carbohydrates in g"),
      goal_fat: z.number().int().optional().describe("Goal fat in g"),
      goal_fiber: z.number().int().optional().describe("Goal fiber in g")
    },
    async (params) => {
      try {
        const response = await fetchWgerApi("/nutritionplan/", {}, {
          method: 'POST',
          body: params
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
            text: `Error creating nutrition plan: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Update Nutrition Plan Tool
  server.tool(
    "update-nutrition-plan",
    {
      id: z.number().int().positive().describe("Nutrition plan ID"),
      description: z.string().max(80).optional().describe("Description of the nutrition plan"),
      only_logging: z.boolean().optional().describe("Whether the plan is only for logging"),
      goal_energy: z.number().int().optional().describe("Goal energy in kcal"),
      goal_protein: z.number().int().optional().describe("Goal protein in g"),
      goal_carbohydrates: z.number().int().optional().describe("Goal carbohydrates in g"),
      goal_fat: z.number().int().optional().describe("Goal fat in g"),
      goal_fiber: z.number().int().optional().describe("Goal fiber in g")
    },
    async ({ id, ...params }) => {
      try {
        const response = await fetchWgerApi(`/nutritionplan/${id}/`, {}, {
          method: 'PATCH',
          body: params
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
            text: `Error updating nutrition plan: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Nutrition Plan Tool
  server.tool(
    "delete-nutrition-plan",
    {
      id: z.number().int().positive().describe("Nutrition plan ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/nutritionplan/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted nutrition plan with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting nutrition plan: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // // Get Nutrition Plan Nutritional Values Tool
  // server.tool(
  //   "get-nutrition-plan-nutritional-values",
  //   {
  //     id: z.number().int().positive().describe("Nutrition plan ID")
  //   },
  //   async ({ id }) => {
  //     try {
  //       const nutritionalValuesData = await fetchWgerApi(`/nutritionplan/${id}/nutritional_values/`);

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
  //           text: `Error fetching nutrition plan nutritional values: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // // Get Nutrition Plan Info Nutritional Values Tool
  // server.tool(
  //   "get-nutrition-plan-info-nutritional-values",
  //   {
  //     id: z.number().int().positive().describe("Nutrition plan ID")
  //   },
  //   async ({ id }) => {
  //     try {
  //       const nutritionalValuesData = await fetchWgerApi(`/nutritionplaninfo/${id}/nutritional_values/`);

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
  //           text: `Error fetching nutrition plan info nutritional values: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // ==================== PROMPTS ====================

  // Create Nutrition Plan Prompt
  server.prompt(
    "create-nutrition-plan",
    "Create a personalized nutrition plan based on your goals",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I want to create a nutrition plan to help me lose weight. I'm 35 years old, 180cm tall, and weigh 85kg. I exercise 3 times a week doing moderate cardio and some weight training. I don't have any dietary restrictions, but I prefer to eat more protein and fewer carbs. Can you help me create a nutrition plan with appropriate calorie and macronutrient targets?"
          }
        }]
      };
    }
  );

  // Track Nutrition Diary Prompt
  server.prompt(
    "track-nutrition-diary",
    "Track your daily food intake in a nutrition diary",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I want to log my food intake for today. For breakfast, I had 2 eggs, 1 slice of whole wheat toast, and a cup of coffee with a splash of milk. For lunch, I had a chicken salad with mixed greens, cherry tomatoes, cucumber, and olive oil dressing. For dinner, I had grilled salmon with steamed broccoli and a small portion of brown rice. I also had an apple as a snack in the afternoon. Can you help me track this in my nutrition diary?"
          }
        }]
      };
    }
  );
}