import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import fetch from "node-fetch";

// Get API configuration from environment variables
const WGER_API_BASE_URL = process.env.WGER_API_BASE_URL || "https://wger.de/api/v2";
const WGER_API_TOKEN = process.env.WGER_API_TOKEN || "";

// Helper function to make API requests to wger
async function fetchWgerApi(endpoint: string, params: Record<string, string> = {}, options: { method?: string; body?: any } = {}) {
  const url = new URL(`${WGER_API_BASE_URL}${endpoint}`);

  // Add query parameters
  Object.entries(params).forEach(([key, value]) => {
    url.searchParams.append(key, value);
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

// Register exercise resources and tools with the server
export function registerExerciseResources(server: McpServer) {
  // ==================== RESOURCES ====================

  // Exercise resource - Get exercise information by ID
  server.resource(
    "exercise",
    new ResourceTemplate("exercise://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const exerciseData = await fetchWgerApi(`/exerciseinfo/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(exerciseData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching exercise: ${error}`
          }]
        };
      }
    }
  );

  // Equipment resource - Get all equipment
  server.resource(
    "equipment",
    "equipment://list",
    async (uri) => {
      try {
        const equipmentData = await fetchWgerApi("/equipment/");
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(equipmentData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching equipment: ${error}`
          }]
        };
      }
    }
  );

  // Equipment by ID resource
  server.resource(
    "equipment-by-id",
    new ResourceTemplate("equipment://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const equipmentData = await fetchWgerApi(`/equipment/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(equipmentData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching equipment: ${error}`
          }]
        };
      }
    }
  );

  // Exercise category resource - Get all exercise categories
  server.resource(
    "exercise-categories",
    "exercise-categories://list",
    async (uri) => {
      try {
        const categoriesData = await fetchWgerApi("/exercisecategory/");
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(categoriesData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching exercise categories: ${error}`
          }]
        };
      }
    }
  );

  // Exercise category by ID resource
  server.resource(
    "exercise-category-by-id",
    new ResourceTemplate("exercise-category://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const categoryData = await fetchWgerApi(`/exercisecategory/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(categoryData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching exercise category: ${error}`
          }]
        };
      }
    }
  );

  // Muscle groups resource
  server.resource(
    "muscles",
    "muscles://list",
    async (uri) => {
      try {
        const musclesData = await fetchWgerApi("/muscle/");
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(musclesData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching muscles: ${error}`
          }]
        };
      }
    }
  );

  // Muscle group by ID resource
  server.resource(
    "muscle-by-id",
    new ResourceTemplate("muscle://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const muscleData = await fetchWgerApi(`/muscle/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(muscleData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching muscle: ${error}`
          }]
        };
      }
    }
  );

  // ==================== TOOLS ====================

  // Search exercises tool
  server.tool(
    "search-exercises",
    {
      term: z.string().min(1).describe("Search term for exercise name"),
      language: z.string().default("en").describe("Language code (e.g., 'en', 'de', 'es')")
    },
    async ({ term, language }) => {
      try {
        const searchResults = await fetchWgerApi("/exercise/search/", {
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
            text: `Error searching exercises: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Get exercise details tool
  server.tool(
    "get-exercise-details",
    {
      id: z.number().int().positive().describe("Exercise ID")
    },
    async ({ id }) => {
      try {
        const exerciseData = await fetchWgerApi(`/exerciseinfo/${id}/`);

        return {
          content: [{
            type: "text",
            text: JSON.stringify(exerciseData, null, 2)
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error fetching exercise details: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Filter exercises tool
  server.tool(
    "filter-exercises",
    {
      category: z.number().int().positive().optional().describe("Filter by category ID"),
      equipment: z.array(z.number().int().positive()).optional().describe("Filter by equipment IDs"),
      muscles: z.array(z.number().int().positive()).optional().describe("Filter by primary muscle IDs"),
      muscles_secondary: z.array(z.number().int().positive()).optional().describe("Filter by secondary muscle IDs"),
      limit: z.number().int().positive().max(100).default(20).describe("Number of results to return")
    },
    async ({ category, equipment, muscles, muscles_secondary, limit }) => {
      try {
        const params: Record<string, string> = { limit: limit.toString() };

        if (category) params.category = category.toString();
        if (equipment) params.equipment = equipment.join(',');
        if (muscles) params.muscles = muscles.join(',');
        if (muscles_secondary) params.muscles_secondary = muscles_secondary.join(',');

        const exercisesData = await fetchWgerApi("/exerciseinfo/", params);

        return {
          content: [{
            type: "text",
            text: JSON.stringify(exercisesData, null, 2)
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error filtering exercises: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Get exercises by muscle group tool
  server.tool(
    "get-exercises-by-muscle",
    {
      muscle_id: z.number().int().positive().describe("Muscle ID to filter exercises by"),
      is_primary: z.boolean().default(true).describe("Whether to search in primary muscles (true) or secondary muscles (false)")
    },
    async ({ muscle_id, is_primary }) => {
      try {
        const params: Record<string, string> = {};

        if (is_primary) {
          params.muscles = muscle_id.toString();
        } else {
          params.muscles_secondary = muscle_id.toString();
        }

        const exercisesData = await fetchWgerApi("/exerciseinfo/", params);

        return {
          content: [{
            type: "text",
            text: JSON.stringify(exercisesData, null, 2)
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error fetching exercises by muscle: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Get exercises by equipment tool
  server.tool(
    "get-exercises-by-equipment",
    {
      equipment_id: z.number().int().positive().describe("Equipment ID to filter exercises by")
    },
    async ({ equipment_id }) => {
      try {
        const params: Record<string, string> = {
          equipment: equipment_id.toString()
        };

        const exercisesData = await fetchWgerApi("/exerciseinfo/", params);

        return {
          content: [{
            type: "text",
            text: JSON.stringify(exercisesData, null, 2)
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error fetching exercises by equipment: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Get exercises by category tool
  server.tool(
    "get-exercises-by-category",
    {
      category_id: z.number().int().positive().describe("Category ID to filter exercises by")
    },
    async ({ category_id }) => {
      try {
        const params: Record<string, string> = {
          category: category_id.toString()
        };

        const exercisesData = await fetchWgerApi("/exerciseinfo/", params);

        return {
          content: [{
            type: "text",
            text: JSON.stringify(exercisesData, null, 2)
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error fetching exercises by category: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // ==================== PROMPTS ====================

  // Exercise recommendation prompt
  server.prompt(
    "recommend-exercises",
    "Get exercise recommendations for a specific muscle group",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I'm looking for exercise recommendations for my arms. I have access to dumbbells and a bench. My fitness level is beginner. Can you suggest some appropriate exercises and explain how to do them correctly?"
          }
        }]
      };
    }
  );

  // Exercise form check prompt
  server.prompt(
    "exercise-form-check",
    "Get guidance on proper exercise form and technique",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I need help with my form for squats. Currently, I'm doing it like this: I stand with feet shoulder-width apart, then bend my knees to lower down, but I feel strain in my lower back. I'm experiencing some pain in my knees when I go too low. Can you provide guidance on proper form and technique for this exercise?"
          }
        }]
      };
    }
  );
}
