# Mealie API: Recipe Generation and Meal Planning

Based on my analysis of the Mealie API, here's a comprehensive overview focused on the recipe generation and meal planning capabilities.

## 1. Recipe Generation & Management

### Recipe Creation
- **Manual Creation**: `/api/recipes` POST endpoint allows creating recipes with detailed information
- **Creation from URL**: `/api/recipes/create/url` scrapes recipe websites to automatically extract and import recipes
- **Bulk URL Import**: `/api/recipes/create/url/bulk` processes multiple URLs at once
- **Creation from HTML/JSON**: `/api/recipes/create/html-or-json` parses raw HTML or schema.org/Recipe JSON objects
- **Creation from Images**: `/api/recipes/create/image` uses OpenAI to extract recipe details from images
- **Creation from ZIP**: `/api/recipes/create/zip` imports from archive files

### Recipe Parsing
- **Ingredient Parsing**: 
  - `/api/parser/ingredient` parses individual ingredients
  - `/api/parser/ingredients` processes multiple ingredients at once
  - This is useful for converting free-text ingredients into structured data

### Recipe Management
- **CRUD Operations**: Complete endpoints for creating, reading, updating, and deleting recipes
- **Recipe Duplication**: `/api/recipes/{slug}/duplicate` creates copies with optional name changes
- **Recipe Exports**: Multiple formats supported including ZIP and various templates
- **Recipe Timeline**: Track recipe events and modifications
- **Recipe Bulk Actions**: Tag, categorize, and manage recipes in batches

## 2. Meal Planning

### Meal Plan Management
- **Create/View Plans**: `/api/households/mealplans` endpoints for meal planning
- **Today's Meals**: `/api/households/mealplans/today` quickly retrieve what's planned for today
- **Date Range**: Filter meal plans by date ranges with `start_date` and `end_date` parameters

### Random Meal Generation
- **Smart Random Meals**: `/api/households/mealplans/random` generates meal plans following household rules
- **Rule-Based Planning**: Random selection honors preferences and restrictions

### Meal Plan Rules
- **Rule Management**: `/api/households/mealplans/rules` endpoints define constraints for meal planning
- **Rule CRUD**: Create, read, update, and delete meal planning rules

## 3. Shopping Lists

### Shopping List Management
- **Create/View Lists**: `/api/households/shopping/lists` endpoints for shopping lists
- **Item Management**: Add, update, and delete items from shopping lists

### Recipe Integration
- **Add Recipe Ingredients**: `/api/households/shopping/lists/{item_id}/recipe` adds ingredients from recipes to shopping lists
- **Remove Recipe Ingredients**: Can selectively remove recipe ingredients from lists

## 4. Organization & Classification

### Categories & Tags
- **Organize Recipes**: Use categories and tags to organize recipes
- **Search & Filter**: Leverage these classifications for meal planning

### Food & Tool Management
- **Track Ingredients**: Manage foods and tools to assist with recipe planning
- **Recipe Suggestions**: `/api/recipes/suggestions` recommends recipes based on available foods and tools

## Integration Points for Recipe Generation Projects

1. **Recipe Creation API**: Use the various creation endpoints to import or create recipes
2. **Ingredient Parsing**: Leverage the parsing endpoints to structure ingredients
3. **Meal Planning**: Use the meal planning APIs for suggesting daily/weekly meal plans
4. **Rule-Based Generation**: Implement intelligent meal planning with user preferences
5. **Shopping List Integration**: Automatically generate shopping lists from planned meals

The Mealie API provides a robust foundation for recipe management and meal planning applications, with particular strengths in recipe import, ingredient parsing, and rule-based meal planning that would be valuable for a recipe generator project.