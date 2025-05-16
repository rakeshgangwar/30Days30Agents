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

// Register ingredient resources and tools with the server
export function registerIngredientResources(server: McpServer) {
  // ==================== RESOURCES ====================

  // Ingredient List Resource
  server.resource(
    "ingredient-list",
    new ResourceTemplate("ingredient://list{?carbohydrates,carbohydrates_sugar,code,created,created__gt,created__lt,energy,fat,fat_saturated,fiber,id,id__in,language,language__in,last_imported,last_imported__gt,last_imported__lt,last_update,last_update__gt,last_update__lt,license,license_author,limit,name,offset,ordering,protein,sodium,source_name,uuid}", { list: undefined }),
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

        const ingredientData = await fetchWgerApi("/ingredient/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(ingredientData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching ingredients: ${error}`
          }]
        };
      }
    }
  );

  // Ingredient Item Resource
  server.resource(
    "ingredient-item",
    new ResourceTemplate("ingredient://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const ingredientItemData = await fetchWgerApi(`/ingredient/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(ingredientItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching ingredient: ${error}`
          }]
        };
      }
    }
  );

  // Ingredient Get Values Resource
  server.resource(
    "ingredient-get-values",
    new ResourceTemplate("ingredient://{id}/get_values{?amount,unit}", { list: undefined }),
    async (uri, { id, amount, unit }) => {
      try {
        const queryParams: Record<string, string | undefined> = {};
        if (amount) queryParams.amount = typeof amount === 'string' ? amount : Array.isArray(amount) ? amount[0] : undefined;
        if (unit) queryParams.unit = typeof unit === 'string' ? unit : Array.isArray(unit) ? unit[0] : undefined;

        const ingredientValuesData = await fetchWgerApi(`/ingredient/${id}/get_values/`, queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(ingredientValuesData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching ingredient values: ${error}`
          }]
        };
      }
    }
  );

  // Ingredient Image List Resource
  server.resource(
    "ingredient-image-list",
    new ResourceTemplate("ingredient-image://list{?ingredient__uuid,ingredient_id,limit,offset,ordering,uuid}", { list: undefined }),
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

        const ingredientImageData = await fetchWgerApi("/ingredient-image/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(ingredientImageData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching ingredient images: ${error}`
          }]
        };
      }
    }
  );

  // Ingredient Image Item Resource
  server.resource(
    "ingredient-image-item",
    new ResourceTemplate("ingredient-image://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const ingredientImageItemData = await fetchWgerApi(`/ingredient-image/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(ingredientImageItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching ingredient image: ${error}`
          }]
        };
      }
    }
  );

  // Ingredient Info List Resource
  server.resource(
    "ingredientinfo-list",
    new ResourceTemplate("ingredientinfo://list{?carbohydrates,carbohydrates_sugar,code,created,created__gt,created__lt,energy,fat,fat_saturated,fiber,id,id__in,language,language__in,last_imported,last_imported__gt,last_imported__lt,last_update,last_update__gt,last_update__lt,license,license_author,limit,name,offset,ordering,protein,sodium,source_name,uuid}", { list: undefined }),
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

        const ingredientInfoData = await fetchWgerApi("/ingredientinfo/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(ingredientInfoData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching ingredient info: ${error}`
          }]
        };
      }
    }
  );

  // Ingredient Info Item Resource
  server.resource(
    "ingredientinfo-item",
    new ResourceTemplate("ingredientinfo://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const ingredientInfoItemData = await fetchWgerApi(`/ingredientinfo/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(ingredientInfoItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching ingredient info: ${error}`
          }]
        };
      }
    }
  );

  // Ingredient Info Get Values Resource
  server.resource(
    "ingredientinfo-get-values",
    new ResourceTemplate("ingredientinfo://{id}/get_values{?amount,unit}", { list: undefined }),
    async (uri, { id, amount, unit }) => {
      try {
        const queryParams: Record<string, string | undefined> = {};
        if (amount) queryParams.amount = typeof amount === 'string' ? amount : Array.isArray(amount) ? amount[0] : undefined;
        if (unit) queryParams.unit = typeof unit === 'string' ? unit : Array.isArray(unit) ? unit[0] : undefined;

        const ingredientInfoValuesData = await fetchWgerApi(`/ingredientinfo/${id}/get_values/`, queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(ingredientInfoValuesData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching ingredient info values: ${error}`
          }]
        };
      }
    }
  );

  // Ingredient Weight Unit List Resource
  server.resource(
    "ingredientweightunit-list",
    new ResourceTemplate("ingredientweightunit://list{?amount,gram,ingredient,limit,offset,ordering,unit}", { list: undefined }),
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

        const ingredientWeightUnitData = await fetchWgerApi("/ingredientweightunit/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(ingredientWeightUnitData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching ingredient weight units: ${error}`
          }]
        };
      }
    }
  );

  // Ingredient Weight Unit Item Resource
  server.resource(
    "ingredientweightunit-item",
    new ResourceTemplate("ingredientweightunit://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const ingredientWeightUnitItemData = await fetchWgerApi(`/ingredientweightunit/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(ingredientWeightUnitItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching ingredient weight unit: ${error}`
          }]
        };
      }
    }
  );

  // ==================== TOOLS ====================

  // Search Ingredients Tool
  server.tool(
    "search-ingredients",
    {
      term: z.string().min(1).describe("Search term for ingredient name"),
      language: z.string().describe("Comma separated list of language codes to search")
    },
    async ({ term, language }) => {
      try {
        const searchResults = await fetchWgerApi("/ingredient/search/", {
          term,
          language
        });

        return {
          content: [{
            type: "text",
            text: JSON.stringify(searchResults, null, 2)
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error searching ingredients: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // // Get Ingredient Details Tool
  // server.tool(
  //   "get-ingredient-details",
  //   {
  //     id: z.number().int().positive().describe("Ingredient ID")
  //   },
  //   async ({ id }) => {
  //     try {
  //       const ingredientData = await fetchWgerApi(`/ingredientinfo/${id}/`);

  //       return {
  //         content: [{
  //           type: "text",
  //           text: JSON.stringify(ingredientData, null, 2)
  //         }]
  //       };
  //     } catch (error) {
  //       return {
  //         content: [{
  //           type: "text",
  //           text: `Error fetching ingredient details: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // // Calculate Ingredient Nutritional Values Tool
  // server.tool(
  //   "calculate-ingredient-nutritional-values",
  //   {
  //     id: z.number().int().positive().describe("Ingredient ID"),
  //     amount: z.number().positive().describe("Amount of the ingredient"),
  //     unit: z.number().int().positive().optional().describe("Weight unit ID (optional)")
  //   },
  //   async ({ id, amount, unit }) => {
  //     try {
  //       const params: Record<string, string | undefined> = {
  //         amount: amount.toString()
  //       };

  //       if (unit) {
  //         params.unit = unit.toString();
  //       }

  //       const nutritionalValuesData = await fetchWgerApi(`/ingredientinfo/${id}/get_values/`, params);

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
  //           text: `Error calculating ingredient nutritional values: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // // Filter Ingredients Tool
  // server.tool(
  //   "filter-ingredients",
  //   {
  //     name: z.string().optional().describe("Filter by ingredient name"),
  //     energy: z.number().int().optional().describe("Filter by energy content"),
  //     protein: z.number().optional().describe("Filter by protein content"),
  //     carbohydrates: z.number().optional().describe("Filter by carbohydrates content"),
  //     fat: z.number().optional().describe("Filter by fat content"),
  //     limit: z.number().int().positive().max(100).default(20).describe("Number of results to return")
  //   },
  //   async (params) => {
  //     try {
  //       const queryParams: Record<string, string | undefined> = {
  //         limit: params.limit.toString()
  //       };

  //       if (params.name) queryParams.name = params.name;
  //       if (params.energy) queryParams.energy = params.energy.toString();
  //       if (params.protein) queryParams.protein = params.protein.toString();
  //       if (params.carbohydrates) queryParams.carbohydrates = params.carbohydrates.toString();
  //       if (params.fat) queryParams.fat = params.fat.toString();

  //       const ingredientsData = await fetchWgerApi("/ingredientinfo/", queryParams);

  //       return {
  //         content: [{
  //           type: "text",
  //           text: JSON.stringify(ingredientsData, null, 2)
  //         }]
  //       };
  //     } catch (error) {
  //       return {
  //         content: [{
  //           type: "text",
  //           text: `Error filtering ingredients: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // ==================== PROMPTS ====================

  // Find Ingredient Prompt
  server.prompt(
    "find-ingredient",
    "Find an ingredient and its nutritional information",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I'm looking for nutritional information about chicken breast. Can you help me find it and tell me about its protein, fat, and calorie content per 100g?"
          }
        }]
      };
    }
  );

  // Calculate Recipe Nutrition Prompt
  server.prompt(
    "calculate-recipe-nutrition",
    "Calculate the nutritional information for a recipe",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I want to calculate the nutritional information for my pasta recipe. It includes 100g of pasta, 150g of ground beef, 200g of tomato sauce, 30g of olive oil, and 50g of parmesan cheese. Can you help me calculate the total calories, protein, carbs, and fat?"
          }
        }]
      };
    }
  );
}
