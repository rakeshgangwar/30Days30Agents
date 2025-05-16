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

// Register routine resources and tools with the server
export function registerRoutineResources(server: McpServer) {
  // ==================== RESOURCES ====================

  // Routine List Resource
  server.resource(
    "routine-list",
    new ResourceTemplate("routine://list{?created,description,end,is_public,is_template,limit,name,offset,ordering,start}", { list: undefined }),
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

        const routineData = await fetchWgerApi("/routine/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(routineData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching routines: ${error}`
          }]
        };
      }
    }
  );

  // Routine Item Resource
  server.resource(
    "routine-item",
    new ResourceTemplate("routine://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const routineItemData = await fetchWgerApi(`/routine/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(routineItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching routine: ${error}`
          }]
        };
      }
    }
  );

  // Routine Structure Resource
  server.resource(
    "routine-structure",
    new ResourceTemplate("routine://{id}/structure", { list: undefined }),
    async (uri, { id }) => {
      try {
        const routineStructureData = await fetchWgerApi(`/routine/${id}/structure/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(routineStructureData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching routine structure: ${error}`
          }]
        };
      }
    }
  );

  // Routine Logs Resource
  server.resource(
    "routine-logs",
    new ResourceTemplate("routine://{id}/logs", { list: undefined }),
    async (uri, { id }) => {
      try {
        const routineLogsData = await fetchWgerApi(`/routine/${id}/logs/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(routineLogsData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching routine logs: ${error}`
          }]
        };
      }
    }
  );

  // Routine Stats Resource
  server.resource(
    "routine-stats",
    new ResourceTemplate("routine://{id}/stats", { list: undefined }),
    async (uri, { id }) => {
      try {
        const routineStatsData = await fetchWgerApi(`/routine/${id}/stats/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(routineStatsData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching routine stats: ${error}`
          }]
        };
      }
    }
  );

  // Routine Date Sequence Display Resource
  server.resource(
    "routine-date-sequence-display",
    new ResourceTemplate("routine://{id}/date-sequence-display", { list: undefined }),
    async (uri, { id }) => {
      try {
        const routineDateSequenceData = await fetchWgerApi(`/routine/${id}/date-sequence-display/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(routineDateSequenceData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching routine date sequence display: ${error}`
          }]
        };
      }
    }
  );

  // Routine Date Sequence Gym Resource
  server.resource(
    "routine-date-sequence-gym",
    new ResourceTemplate("routine://{id}/date-sequence-gym", { list: undefined }),
    async (uri, { id }) => {
      try {
        const routineDateSequenceGymData = await fetchWgerApi(`/routine/${id}/date-sequence-gym/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(routineDateSequenceGymData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching routine date sequence gym: ${error}`
          }]
        };
      }
    }
  );

  // Day List Resource
  server.resource(
    "day-list",
    new ResourceTemplate("day://list{?description,id,is_rest,limit,name,need_logs_to_advance,offset,order,ordering}", { list: undefined }),
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

        const dayData = await fetchWgerApi("/day/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(dayData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching days: ${error}`
          }]
        };
      }
    }
  );

  // Day Item Resource
  server.resource(
    "day-item",
    new ResourceTemplate("day://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const dayItemData = await fetchWgerApi(`/day/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(dayItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching day: ${error}`
          }]
        };
      }
    }
  );

  // Workout Session List Resource
  server.resource(
    "workoutsession-list",
    new ResourceTemplate("workoutsession://list{?date,impression,limit,notes,offset,ordering,routine,time_end,time_start}", { list: undefined }),
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

        const workoutSessionData = await fetchWgerApi("/workoutsession/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(workoutSessionData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching workout sessions: ${error}`
          }]
        };
      }
    }
  );

  // Workout Session Item Resource
  server.resource(
    "workoutsession-item",
    new ResourceTemplate("workoutsession://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const workoutSessionItemData = await fetchWgerApi(`/workoutsession/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(workoutSessionItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching workout session: ${error}`
          }]
        };
      }
    }
  );

  // Workout Log List Resource
  server.resource(
    "workoutlog-list",
    new ResourceTemplate("workoutlog://list{?date,date__date,date__gt,date__gte,date__lt,date__lte,exercise,exercise__in,iteration,iteration__in,limit,offset,ordering,repetitions,repetitions__gt,repetitions__gte,repetitions__lt,repetitions__lte,repetitions_target,repetitions_target__gt,repetitions_target__gte,repetitions_target__lt,repetitions_target__lte,repetitions_unit,repetitions_unit__in,rir,rir__gt,rir__gte,rir__in,rir__lt,rir__lte,rir_target,rir_target__gt,rir_target__gte,rir_target__in,rir_target__lt,rir_target__lte,routine,session,weight,weight__gt,weight__gte,weight__lt,weight__lte,weight_target,weight_target__gt,weight_target__gte,weight_target__lt,weight_target__lte,weight_unit,weight_unit__in}", { list: undefined }),
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

        const workoutLogData = await fetchWgerApi("/workoutlog/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(workoutLogData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching workout logs: ${error}`
          }]
        };
      }
    }
  );

  // Workout Log Item Resource
  server.resource(
    "workoutlog-item",
    new ResourceTemplate("workoutlog://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const workoutLogItemData = await fetchWgerApi(`/workoutlog/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(workoutLogItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching workout log: ${error}`
          }]
        };
      }
    }
  );

  // Slot List Resource
  server.resource(
    "slot-list",
    new ResourceTemplate("slot://list{?comment,day,limit,offset,order,ordering}", { list: undefined }),
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

        const slotData = await fetchWgerApi("/slot/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(slotData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching slots: ${error}`
          }]
        };
      }
    }
  );

  // Slot Item Resource
  server.resource(
    "slot-item",
    new ResourceTemplate("slot://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const slotItemData = await fetchWgerApi(`/slot/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(slotItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching slot: ${error}`
          }]
        };
      }
    }
  );

  // Slot Entry List Resource
  server.resource(
    "slot-entry-list",
    new ResourceTemplate("slot-entry://list{?comment,exercise,limit,offset,order,ordering,repetition_rounding,repetition_unit,slot,type,weight_rounding,weight_unit}", { list: undefined }),
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

        const slotEntryData = await fetchWgerApi("/slot-entry/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(slotEntryData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching slot entries: ${error}`
          }]
        };
      }
    }
  );

  // Slot Entry Item Resource
  server.resource(
    "slot-entry-item",
    new ResourceTemplate("slot-entry://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const slotEntryItemData = await fetchWgerApi(`/slot-entry/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(slotEntryItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching slot entry: ${error}`
          }]
        };
      }
    }
  );

  // ==================== TOOLS ====================

  // Create Routine Tool
  server.tool(
    "create-routine",
    {
      name: z.string().max(25).describe("Name of the routine (Maximum 25 characters)"),
      description: z.string().max(1000).optional().describe("Description of the routine"),
      start: z.string().describe("Start date of the routine (YYYY-MM-DD)"),
      end: z.string().describe("End date of the routine (YYYY-MM-DD)"),
      fit_in_week: z.boolean().optional().describe("Whether to fit the routine in a week"),
      is_template: z.boolean().optional().describe("Whether the routine is a template"),
      is_public: z.boolean().optional().describe("Whether the routine is public")
    },
    async (params) => {
      try {
        const response = await fetchWgerApi("/routine/", {}, {
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
            text: `Error creating routine: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Update Routine Tool
  server.tool(
    "update-routine",
    {
      id: z.number().int().positive().describe("Routine ID"),
      name: z.string().max(25).optional().describe("Name of the routine"),
      description: z.string().max(1000).optional().describe("Description of the routine"),
      start: z.string().optional().describe("Start date of the routine (YYYY-MM-DD)"),
      end: z.string().optional().describe("End date of the routine (YYYY-MM-DD)"),
      fit_in_week: z.boolean().optional().describe("Whether to fit the routine in a week"),
      is_template: z.boolean().optional().describe("Whether the routine is a template"),
      is_public: z.boolean().optional().describe("Whether the routine is public")
    },
    async ({ id, ...params }) => {
      try {
        const response = await fetchWgerApi(`/routine/${id}/`, {}, {
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
            text: `Error updating routine: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Routine Tool
  server.tool(
    "delete-routine",
    {
      id: z.number().int().positive().describe("Routine ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/routine/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted routine with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting routine: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Get Routine Structure Tool
  // server.tool(
  //   "get-routine-structure",
  //   {
  //     id: z.number().int().positive().describe("Routine ID")
  //   },
  //   async ({ id }) => {
  //     try {
  //       const structureData = await fetchWgerApi(`/routine/${id}/structure/`);

  //       return {
  //         content: [{
  //           type: "text",
  //           text: JSON.stringify(structureData, null, 2)
  //         }]
  //       };
  //     } catch (error) {
  //       return {
  //         content: [{
  //           type: "text",
  //           text: `Error fetching routine structure: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // // Get Routine Logs Tool
  // server.tool(
  //   "get-routine-logs",
  //   {
  //     id: z.number().int().positive().describe("Routine ID")
  //   },
  //   async ({ id }) => {
  //     try {
  //       const logsData = await fetchWgerApi(`/routine/${id}/logs/`);

  //       return {
  //         content: [{
  //           type: "text",
  //           text: JSON.stringify(logsData, null, 2)
  //         }]
  //       };
  //     } catch (error) {
  //       return {
  //         content: [{
  //           type: "text",
  //           text: `Error fetching routine logs: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // // Get Routine Stats Tool
  // server.tool(
  //   "get-routine-stats",
  //   {
  //     id: z.number().int().positive().describe("Routine ID")
  //   },
  //   async ({ id }) => {
  //     try {
  //       const statsData = await fetchWgerApi(`/routine/${id}/stats/`);

  //       return {
  //         content: [{
  //           type: "text",
  //           text: JSON.stringify(statsData, null, 2)
  //         }]
  //       };
  //     } catch (error) {
  //       return {
  //         content: [{
  //           type: "text",
  //           text: `Error fetching routine stats: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // // Get Routine Date Sequence Display Tool
  // server.tool(
  //   "get-routine-date-sequence-display",
  //   {
  //     id: z.number().int().positive().describe("Routine ID")
  //   },
  //   async ({ id }) => {
  //     try {
  //       const dateSequenceData = await fetchWgerApi(`/routine/${id}/date-sequence-display/`);

  //       return {
  //         content: [{
  //           type: "text",
  //           text: JSON.stringify(dateSequenceData, null, 2)
  //         }]
  //       };
  //     } catch (error) {
  //       return {
  //         content: [{
  //           type: "text",
  //           text: `Error fetching routine date sequence display: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // // Get Routine Date Sequence Gym Tool
  // server.tool(
  //   "get-routine-date-sequence-gym",
  //   {
  //     id: z.number().int().positive().describe("Routine ID")
  //   },
  //   async ({ id }) => {
  //     try {
  //       const dateSequenceGymData = await fetchWgerApi(`/routine/${id}/date-sequence-gym/`);

  //       return {
  //         content: [{
  //           type: "text",
  //           text: JSON.stringify(dateSequenceGymData, null, 2)
  //         }]
  //       };
  //     } catch (error) {
  //       return {
  //         content: [{
  //           type: "text",
  //           text: `Error fetching routine date sequence gym: ${error}`
  //         }],
  //         isError: true
  //       };
  //     }
  //   }
  // );

  // Create Day Tool
  server.tool(
    "create-day",
    {
      routine: z.number().int().positive().describe("Routine ID"),
      name: z.string().max(20).optional().describe("Name of the day (e.g., 'Day 1', 'Chest Day')"),
      description: z.string().max(1000).optional().describe("Description of the day"),
      order: z.number().int().min(0).optional().describe("Order of the day in the routine"),
      is_rest: z.boolean().optional().describe("Whether this is a rest day"),
      need_logs_to_advance: z.boolean().optional().describe("Whether logs are needed to advance to the next day"),
      type: z.enum(['custom', 'enom', 'amrap', 'hiit', 'tabata', 'edt', 'rft', 'afap']).optional().describe("Type of the day")
    },
    async (params) => {
      try {
        const response = await fetchWgerApi("/day/", {}, {
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
            text: `Error creating day: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Update Day Tool
  server.tool(
    "update-day",
    {
      id: z.number().int().positive().describe("Day ID"),
      routine: z.number().int().positive().optional().describe("Routine ID"),
      name: z.string().max(20).optional().describe("Name of the day (e.g., 'Day 1', 'Chest Day')"),
      description: z.string().max(1000).optional().describe("Description of the day"),
      order: z.number().int().min(0).optional().describe("Order of the day in the routine"),
      is_rest: z.boolean().optional().describe("Whether this is a rest day"),
      need_logs_to_advance: z.boolean().optional().describe("Whether logs are needed to advance to the next day"),
      type: z.enum(['custom', 'enom', 'amrap', 'hiit', 'tabata', 'edt', 'rft', 'afap']).optional().describe("Type of the day")
    },
    async ({ id, ...params }) => {
      try {
        const response = await fetchWgerApi(`/day/${id}/`, {}, {
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
            text: `Error updating day: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Day Tool
  server.tool(
    "delete-day",
    {
      id: z.number().int().positive().describe("Day ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/day/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted day with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting day: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Create Workout Session Tool
  server.tool(
    "create-workout-session",
    {
      date: z.string().describe("Date of the workout session (YYYY-MM-DD)"),
      routine: z.number().int().positive().optional().describe("Routine ID (optional)"),
      day: z.number().int().positive().optional().describe("Day ID (optional)"),
      notes: z.string().optional().describe("Notes about the workout session"),
      impression: z.enum(['1', '2', '3']).optional().describe("General impression (1=Bad, 2=Neutral, 3=Good)"),
      time_start: z.string().optional().describe("Start time of the workout (HH:MM)"),
      time_end: z.string().optional().describe("End time of the workout (HH:MM)")
    },
    async (params) => {
      try {
        const response = await fetchWgerApi("/workoutsession/", {}, {
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
            text: `Error creating workout session: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Update Workout Session Tool
  server.tool(
    "update-workout-session",
    {
      id: z.number().int().positive().describe("Workout session ID"),
      date: z.string().optional().describe("Date of the workout session (YYYY-MM-DD)"),
      routine: z.number().int().positive().optional().describe("Routine ID (optional)"),
      day: z.number().int().positive().optional().describe("Day ID (optional)"),
      notes: z.string().optional().describe("Notes about the workout session"),
      impression: z.enum(['1', '2', '3']).optional().describe("General impression (1=Bad, 2=Neutral, 3=Good)"),
      time_start: z.string().optional().describe("Start time of the workout (HH:MM)"),
      time_end: z.string().optional().describe("End time of the workout (HH:MM)")
    },
    async ({ id, ...params }) => {
      try {
        const response = await fetchWgerApi(`/workoutsession/${id}/`, {}, {
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
            text: `Error updating workout session: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Workout Session Tool
  server.tool(
    "delete-workout-session",
    {
      id: z.number().int().positive().describe("Workout session ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/workoutsession/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted workout session with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting workout session: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Create Workout Log Tool
  server.tool(
    "create-workout-log",
    {
      exercise: z.number().int().positive().describe("Exercise ID"),
      date: z.string().describe("Date and time of the workout log (ISO format)"),
      session: z.number().int().positive().optional().describe("Workout session ID (optional)"),
      routine: z.number().int().positive().optional().describe("Routine ID (optional)"),
      repetitions: z.string().optional().describe("Number of repetitions performed"),
      repetitions_target: z.string().optional().describe("Target number of repetitions"),
      repetitions_unit: z.number().int().positive().optional().describe("Repetition unit ID (optional)"),
      weight: z.string().optional().describe("Weight used"),
      weight_target: z.string().optional().describe("Target weight"),
      weight_unit: z.number().int().positive().optional().describe("Weight unit ID (optional)"),
      rir: z.string().optional().describe("Reps in reserve"),
      rir_target: z.string().optional().describe("Target reps in reserve"),
      rest: z.number().int().min(0).optional().describe("Rest time in seconds"),
      rest_target: z.number().int().min(0).optional().describe("Target rest time in seconds")
    },
    async (params) => {
      try {
        const response = await fetchWgerApi("/workoutlog/", {}, {
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
            text: `Error creating workout log: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Update Workout Log Tool
  server.tool(
    "update-workout-log",
    {
      id: z.number().int().positive().describe("Workout log ID"),
      exercise: z.number().int().positive().optional().describe("Exercise ID"),
      date: z.string().optional().describe("Date and time of the workout log (ISO format)"),
      session: z.number().int().positive().optional().describe("Workout session ID (optional)"),
      routine: z.number().int().positive().optional().describe("Routine ID (optional)"),
      repetitions: z.string().optional().describe("Number of repetitions performed"),
      repetitions_target: z.string().optional().describe("Target number of repetitions"),
      repetitions_unit: z.number().int().positive().optional().describe("Repetition unit ID (optional)"),
      weight: z.string().optional().describe("Weight used"),
      weight_target: z.string().optional().describe("Target weight"),
      weight_unit: z.number().int().positive().optional().describe("Weight unit ID (optional)"),
      rir: z.string().optional().describe("Reps in reserve"),
      rir_target: z.string().optional().describe("Target reps in reserve"),
      rest: z.number().int().min(0).optional().describe("Rest time in seconds"),
      rest_target: z.number().int().min(0).optional().describe("Target rest time in seconds")
    },
    async ({ id, ...params }) => {
      try {
        const response = await fetchWgerApi(`/workoutlog/${id}/`, {}, {
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
            text: `Error updating workout log: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Workout Log Tool
  server.tool(
    "delete-workout-log",
    {
      id: z.number().int().positive().describe("Workout log ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/workoutlog/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted workout log with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting workout log: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Create Slot Tool
  server.tool(
    "create-slot",
    {
      day: z.number().int().positive().describe("Day ID"),
      order: z.number().int().min(0).optional().describe("Order of the slot in the day"),
      comment: z.string().max(200).optional().describe("Comment for the slot")
    },
    async (params) => {
      try {
        const response = await fetchWgerApi("/slot/", {}, {
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
            text: `Error creating slot: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Update Slot Tool
  server.tool(
    "update-slot",
    {
      id: z.number().int().positive().describe("Slot ID"),
      day: z.number().int().positive().optional().describe("Day ID"),
      order: z.number().int().min(0).optional().describe("Order of the slot in the day"),
      comment: z.string().max(200).optional().describe("Comment for the slot")
    },
    async ({ id, ...params }) => {
      try {
        const response = await fetchWgerApi(`/slot/${id}/`, {}, {
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
            text: `Error updating slot: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Slot Tool
  server.tool(
    "delete-slot",
    {
      id: z.number().int().positive().describe("Slot ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/slot/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted slot with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting slot: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Create Slot Entry Tool
  server.tool(
    "create-slot-entry",
    {
      slot: z.number().int().positive().describe("Slot ID"),
      exercise: z.number().int().positive().describe("Base ID of Exercise"),
      type: z.enum(['normal', 'dropset', 'myo', 'partial', 'forced', 'tut', 'iso', 'jump']).optional().describe("Type of the slot entry"),
      repetition_unit: z.number().int().positive().optional().describe("Repetition unit ID"),
      repetition_rounding: z.string().optional().describe("Repetition rounding"),
      weight_unit: z.number().int().positive().optional().describe("Weight unit ID"),
      weight_rounding: z.string().optional().describe("Weight rounding"),
      order: z.number().int().min(0).optional().describe("Order of the slot entry in the slot"),
      comment: z.string().max(100).optional().describe("Comment for the slot entry")
    },
    async (params) => {
      try {
        const response = await fetchWgerApi("/slot-entry/", {}, {
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
            text: `Error creating slot entry: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Update Slot Entry Tool
  server.tool(
    "update-slot-entry",
    {
      id: z.number().int().positive().describe("Slot entry ID"),
      slot: z.number().int().positive().optional().describe("Slot ID"),
      exercise: z.number().int().positive().optional().describe("Base ID of Exercise"),
      type: z.enum(['normal', 'dropset', 'myo', 'partial', 'forced', 'tut', 'iso', 'jump']).optional().describe("Type of the slot entry"),
      repetition_unit: z.number().int().positive().optional().describe("Repetition unit ID"),
      repetition_rounding: z.string().optional().describe("Repetition rounding"),
      weight_unit: z.number().int().positive().optional().describe("Weight unit ID"),
      weight_rounding: z.string().optional().describe("Weight rounding"),
      order: z.number().int().min(0).optional().describe("Order of the slot entry in the slot"),
      comment: z.string().max(100).optional().describe("Comment for the slot entry")
    },
    async ({ id, ...params }) => {
      try {
        const response = await fetchWgerApi(`/slot-entry/${id}/`, {}, {
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
            text: `Error updating slot entry: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Slot Entry Tool
  server.tool(
    "delete-slot-entry",
    {
      id: z.number().int().positive().describe("Slot entry ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/slot-entry/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted slot entry with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting slot entry: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // ==================== PROMPTS ====================

  // Create Workout Routine Prompt
  server.prompt(
    "create-workout-routine",
    "Create a personalized workout routine",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I want to create a workout routine for building muscle. I can work out 4 days a week, and I have access to a full gym. I'm an intermediate lifter and want to focus on my upper body. Can you help me create a suitable workout routine?"
          }
        }]
      };
    }
  );

  // Analyze Workout Routine Prompt
  server.prompt(
    "analyze-workout-routine",
    "Analyze a workout routine and provide feedback",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I've been following a 3-day split routine: Day 1 is chest and triceps, Day 2 is back and biceps, and Day 3 is legs and shoulders. I work out 6 days a week, repeating the cycle twice. Is this an effective routine? Are there any improvements I should make?"
          }
        }]
      };
    }
  );

  // Plan Workout Day Prompt
  server.prompt(
    "plan-workout-day",
    "Plan a specific workout day for a routine",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I want to create a chest and triceps workout day for my routine. I have access to dumbbells, barbells, and machines at my gym. I'm an intermediate lifter looking to build strength and muscle. Can you help me plan this workout day with appropriate exercises, sets, and reps?"
          }
        }]
      };
    }
  );

  // Track Workout Session Prompt
  server.prompt(
    "track-workout-session",
    "Track a workout session with exercises and performance",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I just completed my chest and triceps workout. I did 4 sets of bench press with 185 lbs (10, 8, 8, 6 reps), 3 sets of incline dumbbell press with 65 lbs dumbbells (10, 8, 8 reps), 3 sets of cable flyes with 50 lbs (12 reps each), and 3 sets of tricep pushdowns with 70 lbs (12, 10, 10 reps). The workout took me about 1 hour and I felt good about my performance. Can you help me log this workout session?"
          }
        }]
      };
    }
  );

  // Analyze Workout Progress Prompt
  server.prompt(
    "analyze-workout-progress",
    "Analyze workout progress over time",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I've been following my current workout routine for 8 weeks now. I want to analyze my progress on the main lifts. For bench press, I started at 165 lbs for 8 reps and now I'm at 185 lbs for 8 reps. For squats, I started at 225 lbs for 8 reps and now I'm at 275 lbs for 8 reps. For deadlifts, I started at 275 lbs for 6 reps and now I'm at 315 lbs for 6 reps. Can you analyze my progress and suggest any adjustments to my training?"
          }
        }]
      };
    }
  );

  // Create Workout Exercises Prompt
  server.prompt(
    "create-workout-exercises",
    "Create exercises for a workout day",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I've created a chest and triceps day in my workout routine. Now I need to add specific exercises to this day. I want to include bench press, incline dumbbell press, cable flyes, and tricep pushdowns. Can you help me set up these exercises with appropriate sets, reps, and rest periods? I'm an intermediate lifter looking to build strength and muscle."
          }
        }]
      };
    }
  );
}
