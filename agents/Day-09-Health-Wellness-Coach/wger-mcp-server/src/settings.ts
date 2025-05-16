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

// Register settings resources and tools with the server
export function registerSettingsResources(server: McpServer) {
  // ==================== RESOURCES ====================

  // Sets Config List Resource
  server.resource(
    "sets-config-list",
    new ResourceTemplate("sets-config://list{?limit,offset,ordering}", { list: undefined }),
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

        const setsConfigData = await fetchWgerApi("/sets-config/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(setsConfigData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching sets config: ${error}`
          }]
        };
      }
    }
  );

  // Sets Config Item Resource
  server.resource(
    "sets-config-item",
    new ResourceTemplate("sets-config://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const setsConfigItemData = await fetchWgerApi(`/sets-config/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(setsConfigItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching sets config: ${error}`
          }]
        };
      }
    }
  );

  // Setting Repetition Unit List Resource
  server.resource(
    "setting-repetitionunit-list",
    new ResourceTemplate("setting-repetitionunit://list{?limit,name,offset,ordering}", { list: undefined }),
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

        const repetitionUnitData = await fetchWgerApi("/setting-repetitionunit/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(repetitionUnitData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching repetition units: ${error}`
          }]
        };
      }
    }
  );

  // Setting Repetition Unit Item Resource
  server.resource(
    "setting-repetitionunit-item",
    new ResourceTemplate("setting-repetitionunit://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const repetitionUnitItemData = await fetchWgerApi(`/setting-repetitionunit/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(repetitionUnitItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching repetition unit: ${error}`
          }]
        };
      }
    }
  );

  // Setting Weight Unit List Resource
  server.resource(
    "setting-weightunit-list",
    new ResourceTemplate("setting-weightunit://list{?limit,name,offset,ordering}", { list: undefined }),
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

        const weightUnitData = await fetchWgerApi("/setting-weightunit/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(weightUnitData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching weight units: ${error}`
          }]
        };
      }
    }
  );

  // Setting Weight Unit Item Resource
  server.resource(
    "setting-weightunit-item",
    new ResourceTemplate("setting-weightunit://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const weightUnitItemData = await fetchWgerApi(`/setting-weightunit/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(weightUnitItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching weight unit: ${error}`
          }]
        };
      }
    }
  );

  // Weight Config List Resource
  server.resource(
    "weight-config-list",
    new ResourceTemplate("weight-config://list{?limit,offset,ordering}", { list: undefined }),
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

        const weightConfigData = await fetchWgerApi("/weight-config/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(weightConfigData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching weight config: ${error}`
          }]
        };
      }
    }
  );

  // Weight Config Item Resource
  server.resource(
    "weight-config-item",
    new ResourceTemplate("weight-config://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const weightConfigItemData = await fetchWgerApi(`/weight-config/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(weightConfigItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching weight config: ${error}`
          }]
        };
      }
    }
  );

  // Max Weight Config List Resource
  server.resource(
    "max-weight-config-list",
    new ResourceTemplate("max-weight-config://list{?limit,offset,ordering}", { list: undefined }),
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

        const maxWeightConfigData = await fetchWgerApi("/max-weight-config/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(maxWeightConfigData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching max weight config: ${error}`
          }]
        };
      }
    }
  );

  // Max Weight Config Item Resource
  server.resource(
    "max-weight-config-item",
    new ResourceTemplate("max-weight-config://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const maxWeightConfigItemData = await fetchWgerApi(`/max-weight-config/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(maxWeightConfigItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching max weight config: ${error}`
          }]
        };
      }
    }
  );

  // ==================== TOOLS ====================

  // Create Sets Config Tool
  server.tool(
    "create-sets-config",
    {
      slot_entry: z.number().int().positive().describe("Slot entry ID"),
      iteration: z.number().int().min(0).describe("Iteration number"),
      value: z.number().int().min(0).max(50).describe("Number of sets"),
      operation: z.enum(['add', 'subtract', 'replace']).optional().describe("Operation to perform"),
      step: z.enum(['na', 'abs', 'percent']).optional().describe("Step type"),
      repeat: z.boolean().optional().describe("Whether to repeat"),
      requirements: z.any().optional().describe("Requirements for the sets config")
    },
    async (params) => {
      try {
        const response = await fetchWgerApi("/sets-config/", {}, {
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
            text: `Error creating sets config: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Update Sets Config Tool
  server.tool(
    "update-sets-config",
    {
      id: z.number().int().positive().describe("Sets config ID"),
      slot_entry: z.number().int().positive().optional().describe("Slot entry ID"),
      iteration: z.number().int().min(0).optional().describe("Iteration number"),
      value: z.number().int().min(0).max(50).optional().describe("Number of sets"),
      operation: z.enum(['add', 'subtract', 'replace']).optional().describe("Operation to perform"),
      step: z.enum(['na', 'abs', 'percent']).optional().describe("Step type"),
      repeat: z.boolean().optional().describe("Whether to repeat"),
      requirements: z.any().optional().describe("Requirements for the sets config")
    },
    async ({ id, ...params }) => {
      try {
        const response = await fetchWgerApi(`/sets-config/${id}/`, {}, {
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
            text: `Error updating sets config: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Sets Config Tool
  server.tool(
    "delete-sets-config",
    {
      id: z.number().int().positive().describe("Sets config ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/sets-config/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted sets config with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting sets config: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Create Weight Config Tool
  server.tool(
    "create-weight-config",
    {
      slot_entry: z.number().int().positive().describe("Slot entry ID"),
      iteration: z.number().int().min(0).describe("Iteration number"),
      value: z.string().describe("Weight value"),
      unit: z.number().int().positive().describe("Weight unit ID"),
      operation: z.enum(['add', 'subtract', 'replace']).optional().describe("Operation to perform"),
      step: z.enum(['na', 'abs', 'percent']).optional().describe("Step type"),
      repeat: z.boolean().optional().describe("Whether to repeat"),
      requirements: z.any().optional().describe("Requirements for the weight config")
    },
    async (params) => {
      try {
        const response = await fetchWgerApi("/weight-config/", {}, {
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
            text: `Error creating weight config: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Update Weight Config Tool
  server.tool(
    "update-weight-config",
    {
      id: z.number().int().positive().describe("Weight config ID"),
      slot_entry: z.number().int().positive().optional().describe("Slot entry ID"),
      iteration: z.number().int().min(0).optional().describe("Iteration number"),
      value: z.string().optional().describe("Weight value"),
      unit: z.number().int().positive().optional().describe("Weight unit ID"),
      operation: z.enum(['add', 'subtract', 'replace']).optional().describe("Operation to perform"),
      step: z.enum(['na', 'abs', 'percent']).optional().describe("Step type"),
      repeat: z.boolean().optional().describe("Whether to repeat"),
      requirements: z.any().optional().describe("Requirements for the weight config")
    },
    async ({ id, ...params }) => {
      try {
        const response = await fetchWgerApi(`/weight-config/${id}/`, {}, {
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
            text: `Error updating weight config: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Weight Config Tool
  server.tool(
    "delete-weight-config",
    {
      id: z.number().int().positive().describe("Weight config ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/weight-config/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted weight config with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting weight config: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Create Max Weight Config Tool
  server.tool(
    "create-max-weight-config",
    {
      exercise: z.number().int().positive().describe("Exercise ID"),
      weight: z.string().describe("Max weight value"),
      weight_unit: z.number().int().positive().describe("Weight unit ID"),
      reps: z.number().int().min(0).optional().describe("Number of repetitions"),
      date: z.string().optional().describe("Date of the max weight (YYYY-MM-DD)")
    },
    async (params) => {
      try {
        const response = await fetchWgerApi("/max-weight-config/", {}, {
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
            text: `Error creating max weight config: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Update Max Weight Config Tool
  server.tool(
    "update-max-weight-config",
    {
      id: z.number().int().positive().describe("Max weight config ID"),
      exercise: z.number().int().positive().optional().describe("Exercise ID"),
      weight: z.string().optional().describe("Max weight value"),
      weight_unit: z.number().int().positive().optional().describe("Weight unit ID"),
      reps: z.number().int().min(0).optional().describe("Number of repetitions"),
      date: z.string().optional().describe("Date of the max weight (YYYY-MM-DD)")
    },
    async ({ id, ...params }) => {
      try {
        const response = await fetchWgerApi(`/max-weight-config/${id}/`, {}, {
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
            text: `Error updating max weight config: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Max Weight Config Tool
  server.tool(
    "delete-max-weight-config",
    {
      id: z.number().int().positive().describe("Max weight config ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/max-weight-config/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted max weight config with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting max weight config: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // // Get Repetition Units Tool
  // server.tool(
  //   "get-repetition-units",
  //   {
  //     name: z.string().optional().describe("Filter by name")
  //   },
  //   async ({ name }) => {
  //     try {
  //       const params: Record<string, string | undefined> = {};
  //       if (name) params.name = name;

  //       const repetitionUnitsData = await fetchWgerApi("/setting-repetitionunit/", params);

  //       return {
  //         content: [{
  //           type: "text",
  //           text: JSON.stringify(repetitionUnitsData, null, 2)
  //         }]
  //       };
  //     } catch (error) {
  //       return {
  //         content: [{
  //           type: "text",
  //           text: `Error fetching repetition units: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // // Get Weight Units Tool
  // server.tool(
  //   "get-weight-units",
  //   {
  //     name: z.string().optional().describe("Filter by name")
  //   },
  //   async ({ name }) => {
  //     try {
  //       const params: Record<string, string | undefined> = {};
  //       if (name) params.name = name;

  //       const weightUnitsData = await fetchWgerApi("/setting-weightunit/", params);

  //       return {
  //         content: [{
  //           type: "text",
  //           text: JSON.stringify(weightUnitsData, null, 2)
  //         }]
  //       };
  //     } catch (error) {
  //       return {
  //         content: [{
  //           type: "text",
  //           text: `Error fetching weight units: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // ==================== PROMPTS ====================

  // Configure Workout Settings Prompt
  server.prompt(
    "configure-workout-settings",
    "Configure workout settings for a routine",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I'm setting up a new workout routine and need to configure the sets, repetitions, and weight units. For bench press, I want to do 4 sets of 8-10 reps with a weight of 185 lbs. For squats, I want to do 5 sets of 5 reps with a weight of 225 lbs. Can you help me configure these settings for my workout?"
          }
        }]
      };
    }
  );
}
