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

// Register templates resources and tools with the server
export function registerTemplatesResources(server: McpServer) {
  // ==================== RESOURCES ====================

  // Templates List Resource
  server.resource(
    "templates-list",
    new ResourceTemplate("templates://list{?created,description,limit,name,offset,ordering}", { list: undefined }),
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

        const templatesData = await fetchWgerApi("/templates/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(templatesData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching templates: ${error}`
          }]
        };
      }
    }
  );

  // Templates Item Resource
  server.resource(
    "templates-item",
    new ResourceTemplate("templates://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const templateItemData = await fetchWgerApi(`/templates/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(templateItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching template: ${error}`
          }]
        };
      }
    }
  );

  // Public Templates List Resource
  server.resource(
    "public-templates-list",
    new ResourceTemplate("public-templates://list{?created,description,limit,name,offset,ordering}", { list: undefined }),
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

        const publicTemplatesData = await fetchWgerApi("/public-templates/", queryParams);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(publicTemplatesData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching public templates: ${error}`
          }]
        };
      }
    }
  );

  // Public Templates Item Resource
  server.resource(
    "public-templates-item",
    new ResourceTemplate("public-templates://{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const publicTemplateItemData = await fetchWgerApi(`/public-templates/${id}/`);
        return {
          contents: [{
            uri: uri.href,
            text: JSON.stringify(publicTemplateItemData, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            text: `Error fetching public template: ${error}`
          }]
        };
      }
    }
  );

  // ==================== TOOLS ====================

  // Create Template from Routine Tool
  server.tool(
    "create-template-from-routine",
    {
      routine_id: z.number().int().positive().describe("Routine ID to create template from"),
      is_public: z.boolean().optional().describe("Whether the template should be public")
    },
    async ({ routine_id, is_public }) => {
      try {
        const requestBody = {
          routine: routine_id,
          ...(is_public !== undefined && { is_public })
        };

        const response = await fetchWgerApi("/templates/", {}, {
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
            text: `Error creating template from routine: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Create Routine from Template Tool
  server.tool(
    "create-routine-from-template",
    {
      template_id: z.number().int().positive().describe("Template ID to create routine from")
    },
    async ({ template_id }) => {
      try {
        const response = await fetchWgerApi(`/templates/${template_id}/use/`, {}, {
          method: 'POST'
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
            text: `Error creating routine from template: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // Delete Template Tool
  server.tool(
    "delete-template",
    {
      id: z.number().int().positive().describe("Template ID")
    },
    async ({ id }) => {
      try {
        await fetchWgerApi(`/templates/${id}/`, {}, {
          method: 'DELETE'
        });

        return {
          content: [{
            type: "text",
            text: `Successfully deleted template with ID ${id}`
          }]
        };
      } catch (error) {
        return {
          content: [{
            type: "text",
            text: `Error deleting template: ${error}`
          }],
          isError: true
        };
      }
    }
  );

  // ==================== PROMPTS ====================

  // Use Workout Template Prompt
  server.prompt(
    "use-workout-template",
    "Create a workout routine from a template",
    () => {
      return {
        messages: [{
          role: "user",
          content: {
            type: "text",
            text: "I want to use a workout template to create a new routine. Can you show me the available templates and help me choose one that's good for building muscle with 3-4 workouts per week?"
          }
        }]
      };
    }
  );
}
