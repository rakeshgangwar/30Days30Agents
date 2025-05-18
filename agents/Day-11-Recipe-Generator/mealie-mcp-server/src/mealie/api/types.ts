/**
 * Configuration for the MealieAPI client
 */
export interface MealieAPIConfig {
  baseUrl: string;
  apiKey: string;
}

/**
 * Recipe data structure
 */
export interface Recipe {
  id: string;
  slug: string;
  name: string;
  description?: string;
  recipeCategory?: string[];
  recipeIngredient?: any[];
  recipeInstructions?: any[];
  // Other recipe properties
}

/**
 * Meal plan data structure
 */
export interface MealPlan {
  id: number;
  date: string;
  entryType: string;
  title?: string;
  recipeId?: string;
  recipe?: Recipe;
  text?: string;
}

/**
 * Shopping list data structure
 */
export interface ShoppingList {
  id: string;
  name: string;
  description?: string;
  items?: any[];
}

/**
 * Data for creating a shopping list
 */
export interface ShoppingListCreate {
  name: string;
  description?: string;
}

/**
 * Parameters for creating a random meal plan
 */
export interface RandomMealPlanParams {
  date: string;
  mealType: string;
}

/**
 * Parsed ingredient data structure
 */
export interface ParsedIngredient {
  input: string;
  quantity?: number;
  unit?: string;
  food?: string;
  note?: string;
}

/**
 * Recipe category data structure
 */
export interface Category {
  id: string;
  name: string;
  slug: string;
}

/**
 * Recipe tag data structure
 */
export interface Tag {
  id: string;
  name: string;
  slug: string;
}

/**
 * Recipe suggestion data structure
 */
export interface RecipeSuggestion {
  recipe: { id: string; slug: string; name: string };
  missingFoods: string[];
  missingTools: string[];
}

/**
 * API error response
 */
export interface ApiErrorResponse {
  message: string;
  detail?: string;
  status?: number;
}

/**
 * Recipe creation data - minimal version for initial creation
 */
export interface RecipeCreate {
  name: string;
  description?: string;
  recipeCategory?: string[];
  recipeIngredient?: any[];
  recipeInstructions?: any[];
  // Other optional properties
}

/**
 * Recipe ingredient data
 */
export interface RecipeIngredient {
  note?: string;
  unit?: string | { id: string } | null;
  food?: string | null;
  quantity?: number;
  display?: string;
  title?: string | null;
  disableAmount?: boolean;
  isFood?: boolean;
  originalText?: string | null;
  referenceId?: string;
}

/**
 * Recipe instruction step
 */
export interface RecipeStep {
  id?: string;
  text: string;
  title?: string;
  summary?: string;
  ingredientReferences?: any[];
}

/**
 * Ingredient unit data structure
 */
export interface IngredientUnit {
  id: string;
  name: string;
  abbreviation?: string;
  useAbbreviation?: boolean;
  description?: string;
  fraction?: boolean;
}

/**
 * Export all types
 */
