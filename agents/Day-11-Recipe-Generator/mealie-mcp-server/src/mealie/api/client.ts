import axios, { AxiosInstance, AxiosError } from "axios";
import {
  Recipe,
  MealPlan,
  ShoppingList,
  ShoppingListCreate,
  RandomMealPlanParams,
  ParsedIngredient,
  Category,
  Tag,
  RecipeSuggestion,
  MealieAPIConfig,
  RecipeCreate,
  IngredientUnit
} from "./types.js";

/**
 * MealieAPI client for interacting with the Mealie API
 */
export class MealieAPI {
  public readonly baseUrl: string;
  private client: AxiosInstance;

  /**
   * Creates a new MealieAPI client
   * @param config Configuration for the API client
   */
  constructor(config: MealieAPIConfig) {
    this.baseUrl = config.baseUrl;
    this.client = axios.create({
      baseURL: config.baseUrl,
      headers: {
        Authorization: `Bearer ${config.apiKey}`,
        "Content-Type": "application/json",
      },
    });
  }

  /**
   * Fetches all recipes from Mealie
   * @returns Array of recipes
   */
  async getRecipes(): Promise<Recipe[]> {
    try {
      const response = await this.client.get("/recipes");
      return response.data.items;
    } catch (error) {
      this.handleApiError(error, "Failed to fetch recipes from Mealie API");
    }
  }

  /**
   * Fetches a recipe by its slug
   * @param slug Recipe slug
   * @returns Recipe details
   */
  async getRecipeBySlug(slug: string): Promise<Recipe> {
    try {
      const response = await this.client.get(`/recipes/${slug}`);
      return response.data;
    } catch (error) {
      this.handleApiError(error, `Recipe ${slug} not found`);
    }
  }

  /**
   * Creates a recipe from a URL
   * @param url URL to create recipe from
   * @returns Created recipe
   */
  async createRecipeFromUrl(url: string): Promise<Recipe> {
    try {
      const response = await this.client.post("/recipes/create/url", { url });
      const slug = response.data; // Fetch the newly created recipe details
      return this.getRecipeBySlug(slug);
    } catch (error) {
      this.handleApiError(error, "Failed to create recipe from URL");
    }
  }

  /**
   * Parses ingredients using Mealie's parser
   * @param ingredients Array of ingredient strings to parse
   * @returns Array of parsed ingredients
   */
  async parseIngredients(ingredients: string[]): Promise<ParsedIngredient[]> {
    try {
      const response = await this.client.post("/parser/ingredients", {
        ingredients,
      });
      return response.data;
    } catch (error) {
      this.handleApiError(error, "Failed to parse ingredients");
    }
  }

  /**
   * Gets meal plans for a date range
   * @param startDate Optional start date (YYYY-MM-DD)
   * @param endDate Optional end date (YYYY-MM-DD)
   * @returns Array of meal plans
   */
  async getMealPlans(
    startDate?: string,
    endDate?: string
  ): Promise<MealPlan[]> {
    try {
      let url = "/households/mealplans?";

      if (startDate) {
        url += `start_date=${startDate}&`;
      }

      if (endDate) {
        url += `end_date=${endDate}`;
      }

      const response = await this.client.get(url);
      return response.data.items;
    } catch (error) {
      this.handleApiError(error, "Failed to fetch meal plans");
    }
  }

  /**
   * Creates a random meal plan entry
   * @param params Parameters for the random meal plan
   * @returns Created meal plan
   */
  async createRandomMealPlan(params: RandomMealPlanParams): Promise<MealPlan> {
    try {
      const response = await this.client.post("/households/mealplans/random", {
        date: params.date,
        entryType: params.mealType,
      });
      return response.data;
    } catch (error) {
      this.handleApiError(error, "Failed to create random meal plan");
    }
  }

  /**
   * Creates a new shopping list
   * @param data Shopping list data
   * @returns Created shopping list
   */
  async createShoppingList(data: ShoppingListCreate): Promise<ShoppingList> {
    try {
      const response = await this.client.post(
        "/households/shopping/lists",
        data
      );
      return response.data;
    } catch (error) {
      this.handleApiError(error, "Failed to create shopping list");
    }
  }

  /**
   * Adds a recipe to a shopping list
   * @param listId Shopping list ID
   * @param recipeId Recipe ID
   * @param servings Number of servings (default: 1)
   * @returns Result of the operation
   */
  async addRecipeToShoppingList(
    listId: string,
    recipeId: string,
    servings?: number
  ): Promise<any> {
    try {
      const response = await this.client.post(
        `/households/shopping/lists/${listId}/recipe`,
        [{ recipeId, servings: servings || 1 }]
      );
      return response.data;
    } catch (error) {
      this.handleApiError(error, "Failed to add recipe to shopping list");
    }
  }

  /**
   * Gets all recipe categories
   * @returns Array of categories
   */
  async getCategories(): Promise<Category[]> {
    try {
      const response = await this.client.get("/organizers/categories");
      return response.data.items;
    } catch (error) {
      this.handleApiError(error, "Failed to fetch categories");
    }
  }

  /**
   * Gets all recipe tags
   * @returns Array of tags
   */
  async getTags(): Promise<Tag[]> {
    try {
      const response = await this.client.get("/organizers/tags");
      return response.data.items;
    } catch (error) {
      this.handleApiError(error, "Failed to fetch tags");
    }
  }

  /**
   * Creates a new recipe tag
   * @param name Tag name
   * @returns Created tag
   */
  async createTag(name: string): Promise<Tag> {
    try {
      const response = await this.client.post("/organizers/tags", { name });
      return response.data;
    } catch (error) {
      this.handleApiError(error, `Failed to create tag: ${name}`);
    }
  }

  /**
   * Gets all recipe tools
   * @returns Array of tools
   */
  async getTools(): Promise<Tag[]> {
    try {
      const response = await this.client.get("/organizers/tools");
      return response.data.items;
    } catch (error) {
      this.handleApiError(error, "Failed to fetch tools");
    }
  }

  /**
   * Creates a new recipe tool
   * @param name Tool name
   * @returns Created tool
   */
  async createTool(name: string): Promise<Tag> {
    try {
      const response = await this.client.post("/organizers/tools", { name });
      return response.data;
    } catch (error) {
      this.handleApiError(error, `Failed to create tool: ${name}`);
    }
  }

  /**
   * Gets recipe suggestions based on available foods
   * @param foods Optional array of food IDs or names
   * @param limit Maximum number of suggestions to return
   * @returns Array of recipe suggestions
   */
  async getSuggestedRecipes(
    foods?: string[],
    limit: number = 5
  ): Promise<RecipeSuggestion[]> {
    try {
      let url = `/recipes/suggestions?limit=${limit}`;

      if (foods && foods.length > 0) {
        url += `&foods=${foods.join(",")}`;
      }

      const response = await this.client.get(url);
      return response.data.suggestions;
    } catch (error) {
      this.handleApiError(error, "Failed to fetch recipe suggestions");
    }
  }

  /**
   * Creates a new recipe manually
   * @param recipeData Recipe data with at least a name
   * @returns Created recipe
   */
  async createRecipe(recipeData: RecipeCreate): Promise<Recipe> {
    try {
      const response = await this.client.post("/recipes", recipeData);
      const slug = response.data; // Mealie returns the slug of the created recipe
      return this.getRecipeBySlug(slug);
    } catch (error) {
      this.handleApiError(error, "Failed to create recipe");
    }
  }

  /**
   * Updates an existing recipe
   * @param slug Recipe slug
   * @param recipeData Updated recipe data
   * @returns Updated recipe
   */
  async updateRecipe(slug: string, recipeData: any): Promise<Recipe> {
    try {
      await this.client.put(`/recipes/${slug}`, recipeData);
      return this.getRecipeBySlug(slug);
    } catch (error) {
      this.handleApiError(error, `Failed to update recipe ${slug}`);
    }
  }

  /**
   * Gets all available ingredient units
   * @returns Array of ingredient units
   */
  async getUnits(): Promise<IngredientUnit[]> {
    try {
      const response = await this.client.get("/units");
      return response.data.items;
    } catch (error) {
      this.handleApiError(error, "Failed to fetch ingredient units");
    }
  }

  /**
   * Gets a specific ingredient unit by ID
   * @param id Unit ID
   * @returns Ingredient unit details
   */
  async getUnitById(id: string): Promise<IngredientUnit> {
    try {
      const response = await this.client.get(`/units/${id}`);
      return response.data;
    } catch (error) {
      this.handleApiError(error, `Unit with ID ${id} not found`);
    }
  }

  /**
   * Handles API errors in a consistent way
   * @param error Error from axios
   * @param defaultMessage Default error message
   */
  private handleApiError(error: unknown, defaultMessage: string): never {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      const statusCode = axiosError.response?.status;
      const responseData = axiosError.response?.data;

      let errorMessage = defaultMessage;
      if (responseData && typeof responseData === 'object' && 'message' in responseData) {
        errorMessage = `${defaultMessage}: ${responseData.message}`;
      }

      throw new Error(`API Error (${statusCode}): ${errorMessage}`);
    }

    throw new Error(defaultMessage);
  }
}
