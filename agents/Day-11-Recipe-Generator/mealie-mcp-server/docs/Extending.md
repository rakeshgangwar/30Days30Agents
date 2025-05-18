# Extending the Mealie MCP Server

This document explains how to extend the Mealie MCP Server with new resources and tools. It provides guidance on adding new functionality, integrating with additional Mealie API endpoints, and customizing the server for your needs.

## Overview

The Mealie MCP Server is designed to be modular and extensible. You can add new resources and tools to expose additional Mealie functionality to LLMs. This guide will walk you through the process of extending the server.

## Project Structure

Before extending the server, it's important to understand its structure:

```
src/
├── mealie/
│   ├── api/                  # Mealie API client and types
│   │   ├── client.ts         # API client implementation
│   │   ├── index.ts          # API module exports
│   │   └── types.ts          # TypeScript interfaces for API data
│   ├── resources/            # MCP resources and tools
│   │   ├── index.ts          # Resource module exports
│   │   ├── mealplans.ts      # Meal plan resources and tools
│   │   ├── organizers.ts     # Category/tag resources and tools
│   │   ├── recipes.ts        # Recipe resources and tools
│   │   └── shopping.ts       # Shopping list resources and tools
│   ├── transports/           # MCP transport implementations
│   ├── utils/                # Utility functions
│   ├── index.ts              # Main entry point
│   └── server.ts             # MCP server configuration
```

## Adding New API Client Methods

To add new functionality, you'll often need to extend the API client to interact with additional Mealie API endpoints.

### Step 1: Update API Types

First, define any new types in `src/mealie/api/types.ts`:

```typescript
/**
 * New data structure for your feature
 */
export interface NewFeature {
  id: string;
  name: string;
  // Other properties
}

/**
 * Parameters for creating a new feature
 */
export interface NewFeatureCreate {
  name: string;
  // Other properties
}
```

### Step 2: Add API Client Methods

Next, add methods to the `MealieAPI` class in `src/mealie/api/client.ts`:

```typescript
/**
 * Gets all new features
 * @returns Array of new features
 */
async getNewFeatures(): Promise<NewFeature[]> {
  try {
    const response = await this.client.get("/new-features");
    return response.data.items;
  } catch (error) {
    this.handleApiError(error, "Failed to fetch new features");
  }
}

/**
 * Creates a new feature
 * @param data New feature data
 * @returns Created feature
 */
async createNewFeature(data: NewFeatureCreate): Promise<NewFeature> {
  try {
    const response = await this.client.post("/new-features", data);
    return response.data;
  } catch (error) {
    this.handleApiError(error, "Failed to create new feature");
  }
}
```

## Adding New Resources

Resources in MCP are data sources that can be accessed by URI. To add a new resource:

### Step 1: Create a Resource Module

If your resource doesn't fit into an existing category, create a new file in the `resources` directory:

```typescript
// src/mealie/resources/new-features.ts
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { mealieApi, logger } from "../server.js";

/**
 * Registers all new feature related resources and tools with the MCP server
 * @param server MCP server instance
 */
export function registerNewFeatureResources(server: McpServer) {
  logger.debug("Registering new feature resources and tools");

  // ==================== RESOURCES ====================

  // Resource: List new features
  server.resource("new-features-list", "mealie://new-features/list", async () => {
    try {
      const features = await mealieApi.getNewFeatures();
      return {
        contents: [
          {
            uri: "mealie://new-features/list",
            text: JSON.stringify(features, null, 2),
          },
        ],
      };
    } catch (error) {
      logger.error(`Error fetching new features: ${error}`);
      return {
        contents: [
          {
            uri: "mealie://new-features/list",
            text: `Error fetching new features: ${error}`,
          },
        ],
      };
    }
  });

  // Resource: Get new feature by ID
  server.resource(
    "new-feature-by-id",
    new ResourceTemplate("mealie://new-features/{id}", { list: undefined }),
    async (uri, { id }) => {
      try {
        const feature = await mealieApi.getNewFeatureById(
          Array.isArray(id) ? id[0] : id
        );
        return {
          contents: [
            {
              uri: uri.href,
              text: JSON.stringify(feature, null, 2),
            },
          ],
        };
      } catch (error) {
        logger.error(`Error fetching new feature ${id}: ${error}`);
        return {
          contents: [
            {
              uri: uri.href,
              text: `Error fetching new feature: ${error}`,
            },
          ],
        };
      }
    }
  );

  // ==================== TOOLS ====================

  // Tool: Create new feature
  server.tool(
    "create-new-feature",
    {
      name: z.string(),
      description: z.string().optional(),
    },
    async ({ name, description }) => {
      try {
        const feature = await mealieApi.createNewFeature({
          name,
          description,
        });
        return {
          content: [
            {
              type: "text",
              text: `New feature created: ${feature.name} (${feature.id})`,
            },
          ],
        };
      } catch (error: any) {
        logger.error(`Error creating new feature: ${error}`);
        return {
          content: [
            {
              type: "text",
              text: `Failed to create new feature: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );
}
```

### Step 2: Update the Resources Index

Add your new resource module to `src/mealie/resources/index.ts`:

```typescript
/**
 * Resource modules for MCP server
 */

export * from "./recipes.js";
export * from "./mealplans.js";
export * from "./shopping.js";
export * from "./organizers.js";
export * from "./new-features.js"; // Add your new module
```

### Step 3: Register the Resources

Update the server creation in `src/mealie/server.ts` to register your new resources:

```typescript
/**
 * Creates and configures an MCP server with Mealie resources and tools
 */
export function createMcpServer() {
  const server = new McpServer({
    name: "MealieMCP",
    version: "1.0.0",
    description: "MCP server for Mealie recipe generation and meal planning",
  });

  // Log server creation
  logger.info("Creating MCP Server");
  logger.info(`Mealie API URL: ${mealieApi.baseUrl}`);

  // Register resources and tools
  registerRecipeResources(server);
  registerMealPlanResources(server);
  registerShoppingResources(server);
  registerOrganizerResources(server);
  registerNewFeatureResources(server); // Add your new resources

  return server;
}
```

## Adding New Tools

Tools in MCP are functions that can be called to perform actions. You can add tools to existing resource modules or create new ones.

### Example: Adding a Tool to an Existing Module

Here's an example of adding a new tool to the recipes module:

```typescript
// In src/mealie/resources/recipes.ts

// Tool: Rate recipe
server.tool(
  "rate-recipe",
  {
    slug: z.string(),
    rating: z.number().min(1).max(5),
    comment: z.string().optional(),
  },
  async ({ slug, rating, comment }) => {
    try {
      await mealieApi.rateRecipe(slug, rating, comment);
      return {
        content: [
          {
            type: "text",
            text: `Recipe ${slug} rated ${rating}/5`,
          },
        ],
      };
    } catch (error: any) {
      logger.error(`Error rating recipe: ${error}`);
      return {
        content: [
          {
            type: "text",
            text: `Failed to rate recipe: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
);
```

## Best Practices

When extending the Mealie MCP Server, follow these best practices:

### 1. Organize by Domain

Group related resources and tools in the same module based on their domain (e.g., recipes, meal plans).

### 2. Consistent Error Handling

Use consistent error handling patterns:

```typescript
try {
  // API call
} catch (error: any) {
  logger.error(`Error message: ${error}`);
  return {
    content: [
      {
        type: "text",
        text: `User-friendly error message: ${error.message}`,
      },
    ],
    isError: true,
  };
}
```

### 3. Input Validation with Zod

Use Zod schemas for tool parameters to ensure proper validation:

```typescript
server.tool(
  "tool-name",
  {
    requiredParam: z.string(),
    optionalParam: z.number().optional(),
    enumParam: z.enum(["option1", "option2"]),
    arrayParam: z.array(z.string()),
  },
  async (params) => {
    // Tool implementation
  }
);
```

### 4. Resource Naming Conventions

Follow consistent naming conventions for resources:

- Resource IDs: kebab-case (e.g., `"new-features-list"`)
- URIs: `mealie://{domain}/{action}` or `mealie://{domain}/{parameter}`

### 5. Documentation

Document your additions in the API reference:

- Add new resources to the resources section
- Add new tools to the tools section
- Include examples of usage

## Testing Your Extensions

Test your extensions using the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector --command "node dist/mealie/index.js --stdio"
```

## Example: Complete Extension

Here's a complete example of adding support for Mealie's cookbook feature:

1. Add types in `src/mealie/api/types.ts`:

```typescript
/**
 * Cookbook data structure
 */
export interface Cookbook {
  id: string;
  name: string;
  description?: string;
  recipeCount: number;
}

/**
 * Data for creating a cookbook
 */
export interface CookbookCreate {
  name: string;
  description?: string;
}
```

2. Add API methods in `src/mealie/api/client.ts`:

```typescript
/**
 * Gets all cookbooks
 * @returns Array of cookbooks
 */
async getCookbooks(): Promise<Cookbook[]> {
  try {
    const response = await this.client.get("/cookbooks");
    return response.data.items;
  } catch (error) {
    this.handleApiError(error, "Failed to fetch cookbooks");
  }
}

/**
 * Creates a new cookbook
 * @param data Cookbook data
 * @returns Created cookbook
 */
async createCookbook(data: CookbookCreate): Promise<Cookbook> {
  try {
    const response = await this.client.post("/cookbooks", data);
    return response.data;
  } catch (error) {
    this.handleApiError(error, "Failed to create cookbook");
  }
}
```

3. Create a new resource module `src/mealie/resources/cookbooks.ts`:

```typescript
import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { mealieApi, logger } from "../server.js";

export function registerCookbookResources(server: McpServer) {
  // Resources and tools implementation
}
```

4. Update `src/mealie/resources/index.ts` and `src/mealie/server.ts`.

5. Document your extension in the API reference.

## Conclusion

By following this guide, you can extend the Mealie MCP Server with new resources and tools to expose additional Mealie functionality to LLMs. This allows you to customize the server for your specific needs and integrate with all aspects of the Mealie API.
