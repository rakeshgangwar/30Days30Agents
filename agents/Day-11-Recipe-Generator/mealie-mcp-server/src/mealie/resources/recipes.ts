import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { mealieApi, logger } from "../server.js";
import crypto from "crypto";

/**
 * Registers all recipe-related resources and tools with the MCP server
 * @param server MCP server instance
 */
export function registerRecipeResources(server: McpServer) {
  logger.debug("Registering recipe resources and tools");

  // ==================== RESOURCES ====================

  // Resource: List recipes
  server.resource("recipes-list", "mealie://recipes/list", async () => {
    try {
      const recipes = await mealieApi.getRecipes();
      return {
        contents: [
          {
            uri: "mealie://recipes/list",
            text: JSON.stringify(recipes, null, 2),
          },
        ],
      };
    } catch (error) {
      logger.error(`Error fetching recipes: ${error}`);
      return {
        contents: [
          {
            uri: "mealie://recipes/list",
            text: `Error fetching recipes: ${error}`,
          },
        ],
      };
    }
  });

  // Resource: Get recipe by slug
  server.resource(
    "recipe-by-slug",
    new ResourceTemplate("mealie://recipes/{slug}", { list: undefined }),
    async (uri, { slug }) => {
      try {
        const recipe = await mealieApi.getRecipeBySlug(
          Array.isArray(slug) ? slug[0] : slug
        );
        return {
          contents: [
            {
              uri: uri.href,
              text: JSON.stringify(recipe, null, 2),
            },
          ],
        };
      } catch (error) {
        logger.error(`Error fetching recipe ${slug}: ${error}`);
        return {
          contents: [
            {
              uri: uri.href,
              text: `Error fetching recipe: ${error}`,
            },
          ],
        };
      }
    }
  );

  // ==================== TOOLS ====================

  // Tool: Create recipe from URL
  server.tool(
    "create-recipe-from-url",
    { url: z.string().url() },
    async ({ url }) => {
      try {
        const recipe = await mealieApi.createRecipeFromUrl(url);
        return {
          content: [
            {
              type: "text",
              text: `Recipe created: ${recipe.name} (${recipe.slug})`,
            },
          ],
        };
      } catch (error: any) {
        logger.error(`Error creating recipe from URL: ${error}`);
        return {
          content: [
            {
              type: "text",
              text: `Failed to create recipe from URL: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );

  // Tool: Get recipe by slug
  server.tool(
    "get-recipe",
    { slug: z.string() },
    async ({ slug }) => {
      try {
        const recipe = await mealieApi.getRecipeBySlug(slug);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(recipe, null, 2),
            },
          ],
        };
      } catch (error: any) {
        logger.error(`Error fetching recipe: ${error}`);
        return {
          content: [
            {
              type: "text",
              text: `Failed to fetch recipe: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );

  // Tool: Parse ingredients
  server.tool(
    "parse-ingredients",
    { ingredients: z.array(z.string()) },
    async ({ ingredients }) => {
      try {
        const parsedIngredients = await mealieApi.parseIngredients(ingredients);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(parsedIngredients, null, 2),
            },
          ],
        };
      } catch (error: any) {
        logger.error(`Error parsing ingredients: ${error}`);
        return {
          content: [
            {
              type: "text",
              text: `Failed to parse ingredients: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );

  // Tool: Suggest recipes
  server.tool(
    "suggest-recipes",
    {
      foods: z.array(z.string()).optional(),
      limit: z.number().min(1).max(20).optional(),
    },
    async ({ foods, limit }) => {
      try {
        const suggestions = await mealieApi.getSuggestedRecipes(foods, limit);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(suggestions, null, 2),
            },
          ],
        };
      } catch (error: any) {
        logger.error(`Error suggesting recipes: ${error}`);
        return {
          content: [
            {
              type: "text",
              text: `Failed to suggest recipes: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );

  // Tool: Create recipe (simple version)
  server.tool(
    "create-recipe",
    {
      name: z.string(),
      description: z.string().optional(),
    },
    async ({ name, description }) => {
      try {
        // Create a basic recipe with just the name and optional description
        const recipeData: any = { name };
        if (description) {
          recipeData.description = description;
        }

        const recipe = await mealieApi.createRecipe(recipeData);
        return {
          content: [
            {
              type: "text",
              text: `Recipe created: ${recipe.name} (${recipe.slug})`,
            },
          ],
        };
      } catch (error: any) {
        logger.error(`Error creating recipe: ${error}`);
        return {
          content: [
            {
              type: "text",
              text: `Failed to create recipe: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );

  // Tool: Update recipe
  server.tool(
    "update-recipe",
    {
      slug: z.string(),
      name: z.string().optional(),
      description: z.string().optional(),
      recipeYield: z.string().optional(),
      recipeYieldQuantity: z.number().optional(),
      recipeServings: z.number().optional(),
      prepTime: z.string().optional(),
      cookTime: z.string().optional(),
      performTime: z.string().optional(),
      totalTime: z.string().optional(),
      recipeCategory: z.array(
        z.object({
          id: z.string().optional(),
          name: z.string(),
          slug: z.string().optional(),
        })
      ).optional(),
      tags: z.array(
        z.object({
          id: z.string().optional(),
          name: z.string(),
          slug: z.string().optional(),
        })
      ).optional(),
      tools: z.array(
        z.object({
          id: z.string().optional(),
          name: z.string(),
          slug: z.string().optional(),
        })
      ).optional(),
      recipeIngredient: z.array(
        z.object({
          note: z.string().optional(),
          unit: z.union([
            z.string(),
            z.object({ id: z.string() }),
            z.null()
          ]).optional(),
          food: z.union([z.string(), z.null()]).optional(),
          quantity: z.number().optional(),
          display: z.string().optional(),
          title: z.union([z.string(), z.null()]).optional(),
          disableAmount: z.boolean().optional(),
          isFood: z.boolean().optional(),
          originalText: z.union([z.string(), z.null()]).optional(),
          referenceId: z.string().optional(),
        })
      ).optional(),
      recipeInstructions: z.array(
        z.object({
          id: z.string().optional(),
          text: z.string(),
          title: z.string().optional(),
          summary: z.string().optional(),
          ingredientReferences: z.array(z.any()).optional(),
        })
      ).optional(),
      settings: z.object({
        public: z.boolean().optional(),
        showNutrition: z.boolean().optional(),
        showAssets: z.boolean().optional(),
        landscapeView: z.boolean().optional(),
        disableComments: z.boolean().optional(),
        disableAmount: z.boolean().optional(),
        locked: z.boolean().optional(),
      }).optional(),
    },
    async ({ slug, ...recipeData }) => {
      try {
        // Process recipe data to handle units properly
        // Use type assertion to allow for the unit object structure
        const processedData: any = { ...recipeData };

        // Process recipe categories if provided
        if (processedData.recipeCategory && processedData.recipeCategory.length > 0) {
          // For categories without IDs, we need to fetch or create them
          const categories = await Promise.all(
            processedData.recipeCategory.map(async (category: { id?: string, name: string, slug?: string }) => {
              // If category already has an ID, use it as is
              if (category.id) {
                return category;
              }

              try {
                // Try to fetch existing categories to find a match
                const allCategories = await mealieApi.getCategories();
                const existingCategory = allCategories.find(
                  c => c.name.toLowerCase() === category.name.toLowerCase()
                );

                if (existingCategory) {
                  return existingCategory;
                } else {
                  // Category doesn't exist, just use the name
                  // The API will handle this appropriately
                  logger.debug(`Using category without ID: ${category.name}`);
                  return { name: category.name };
                }
              } catch (error) {
                logger.error(`Error processing category ${category.name}: ${error}`);
                // Return just the name if we can't process it properly
                return { name: category.name };
              }
            })
          );

          processedData.recipeCategory = categories;
        }

        // Process recipe tags if provided
        if (processedData.tags && processedData.tags.length > 0) {
          // For tags without IDs, we need to fetch existing ones
          const tags = await Promise.all(
            processedData.tags.map(async (tag: { id?: string, name: string, slug?: string }) => {
              // If tag already has an ID, use it as is
              if (tag.id) {
                return tag;
              }

              try {
                // Try to fetch existing tags to find a match
                const allTags = await mealieApi.getTags();
                const existingTag = allTags.find(
                  t => t.name.toLowerCase() === tag.name.toLowerCase()
                );

                if (existingTag) {
                  return existingTag;
                } else {
                  // Tag doesn't exist, just use the name
                  logger.debug(`Using tag without ID: ${tag.name}`);
                  return { name: tag.name };
                }
              } catch (error) {
                logger.error(`Error processing tag ${tag.name}: ${error}`);
                // Return just the name if we can't process it properly
                return { name: tag.name };
              }
            })
          );

          processedData.tags = tags;
        }

        // Process recipe tools if provided
        if (processedData.tools && processedData.tools.length > 0) {
          // Just use the tool names as provided
          // The API will handle this appropriately
          processedData.tools = processedData.tools.map((tool: { id?: string, name: string, slug?: string }) => {
            if (tool.id) {
              return tool;
            }
            return { name: tool.name };
          });
        }

        // If there are ingredients with units, convert unit names to unit objects with IDs
        if (processedData.recipeIngredient && processedData.recipeIngredient.length > 0) {
          // Get all available units
          const units = await mealieApi.getUnits();

          // Process each ingredient to convert unit names to unit objects with IDs
          processedData.recipeIngredient = processedData.recipeIngredient.map((ingredient: any) => {
            // Create a processed ingredient with all the fields
            const processedIngredient = {
              ...ingredient,
              // Generate a reference ID if not provided
              referenceId: ingredient.referenceId || crypto.randomUUID(),
              // Set default values for required fields
              disableAmount: ingredient.disableAmount !== undefined ? ingredient.disableAmount : false,
              isFood: ingredient.isFood !== undefined ? ingredient.isFood : false,
              title: ingredient.title || "",
              originalText: ingredient.originalText || null,
            };

            // If display is not provided but note is, use note as display
            if (!processedIngredient.display && processedIngredient.note) {
              processedIngredient.display = processedIngredient.note;
            }

            // Process unit if it's a string
            if (typeof ingredient.unit === 'string' && ingredient.unit) {
              // Find the unit by name
              const matchedUnit = units.find(u =>
                u.name.toLowerCase() === ingredient.unit?.toString().toLowerCase() ||
                (u.abbreviation && u.abbreviation.toLowerCase() === ingredient.unit?.toString().toLowerCase())
              );

              if (matchedUnit) {
                // Replace the unit name with a unit object containing the ID
                processedIngredient.unit = { id: matchedUnit.id };
              } else {
                // If no matching unit found, set to null to avoid errors
                processedIngredient.unit = null;
              }
            }

            return processedIngredient;
          });
        }

        // Process recipe instructions if provided
        if (processedData.recipeInstructions && processedData.recipeInstructions.length > 0) {
          // Add IDs to instructions if not provided
          processedData.recipeInstructions = processedData.recipeInstructions.map((instruction: any) => ({
            ...instruction,
            id: instruction.id || crypto.randomUUID(),
            title: instruction.title || "",
            summary: instruction.summary || "",
            ingredientReferences: instruction.ingredientReferences || []
          }));
        }

        // Add default settings if not provided
        if (!processedData.settings) {
          processedData.settings = {
            public: false,
            showNutrition: false,
            showAssets: false,
            landscapeView: false,
            disableComments: false,
            disableAmount: true,
            locked: false
          };
        }

        const updatedRecipe = await mealieApi.updateRecipe(slug, processedData);
        return {
          content: [
            {
              type: "text",
              text: `Recipe updated: ${updatedRecipe.name} (${updatedRecipe.slug})`,
            },
          ],
        };
      } catch (error: any) {
        logger.error(`Error updating recipe: ${error}`);
        return {
          content: [
            {
              type: "text",
              text: `Failed to update recipe: ${error.message}`,
            },
          ],
          isError: true,
        };
      }
    }
  );
}
