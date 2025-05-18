# Mealie MCP Server API Reference

This document provides detailed information about the resources and tools available in the Mealie MCP Server.

## Resources

Resources in MCP are data sources that can be accessed by URI. The Mealie MCP Server exposes the following resources:

### Recipe Resources

#### List All Recipes

```
URI: mealie://recipes/list
```

Returns a list of all recipes in the Mealie database.

**Example Response:**
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "slug": "chocolate-chip-cookies",
    "name": "Chocolate Chip Cookies",
    "description": "Classic chocolate chip cookies that are crispy on the outside and chewy on the inside."
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174001",
    "slug": "spaghetti-carbonara",
    "name": "Spaghetti Carbonara",
    "description": "A classic Italian pasta dish with eggs, cheese, pancetta, and black pepper."
  }
]
```

#### Get Recipe by Slug

```
URI: mealie://recipes/{slug}
```

Returns detailed information about a specific recipe.

**Parameters:**
- `slug`: The recipe slug (e.g., "chocolate-chip-cookies")

**Example Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "slug": "chocolate-chip-cookies",
  "name": "Chocolate Chip Cookies",
  "description": "Classic chocolate chip cookies that are crispy on the outside and chewy on the inside.",
  "recipeYield": "24 cookies",
  "recipeIngredient": [
    {
      "note": "",
      "unit": { "id": "unit-id-1", "name": "cup" },
      "food": "all-purpose flour",
      "quantity": 2.25,
      "display": "2 1/4 cups all-purpose flour"
    },
    {
      "note": "",
      "unit": { "id": "unit-id-2", "name": "teaspoon" },
      "food": "baking soda",
      "quantity": 1,
      "display": "1 teaspoon baking soda"
    }
  ],
  "recipeInstructions": [
    {
      "id": "step-1",
      "text": "Preheat oven to 375°F (190°C).",
      "title": "Preheat"
    },
    {
      "id": "step-2",
      "text": "In a small bowl, mix flour, baking soda, and salt.",
      "title": "Mix dry ingredients"
    }
  ]
}
```

### Meal Plan Resources

#### Get Meal Plans for Date Range

```
URI: mealie://mealplans/{startDate}/{endDate}
```

Returns meal plans for the specified date range.

**Parameters:**
- `startDate`: Start date in YYYY-MM-DD format
- `endDate`: End date in YYYY-MM-DD format

**Example Response:**
```json
[
  {
    "id": 1,
    "date": "2023-05-15",
    "entryType": "dinner",
    "title": "Spaghetti Carbonara",
    "recipeId": "223e4567-e89b-12d3-a456-426614174001"
  },
  {
    "id": 2,
    "date": "2023-05-16",
    "entryType": "dinner",
    "title": "Chicken Stir Fry",
    "recipeId": "323e4567-e89b-12d3-a456-426614174002"
  }
]
```

#### Get Today's Meal Plan

```
URI: mealie://mealplans/today
```

Returns the meal plan for the current day.

**Example Response:**
```json
[
  {
    "id": 1,
    "date": "2023-05-15",
    "entryType": "breakfast",
    "title": "Oatmeal with Berries",
    "recipeId": "423e4567-e89b-12d3-a456-426614174003"
  },
  {
    "id": 2,
    "date": "2023-05-15",
    "entryType": "lunch",
    "title": "Caesar Salad",
    "recipeId": "523e4567-e89b-12d3-a456-426614174004"
  },
  {
    "id": 3,
    "date": "2023-05-15",
    "entryType": "dinner",
    "title": "Spaghetti Carbonara",
    "recipeId": "223e4567-e89b-12d3-a456-426614174001"
  }
]
```

### Organizer Resources

#### List Categories

```
URI: mealie://categories
```

Returns a list of all recipe categories.

**Example Response:**
```json
[
  {
    "id": "cat-1",
    "name": "Breakfast",
    "slug": "breakfast"
  },
  {
    "id": "cat-2",
    "name": "Dinner",
    "slug": "dinner"
  },
  {
    "id": "cat-3",
    "name": "Dessert",
    "slug": "dessert"
  }
]
```

#### List Tags

```
URI: mealie://tags
```

Returns a list of all recipe tags.

**Example Response:**
```json
[
  {
    "id": "tag-1",
    "name": "Quick",
    "slug": "quick"
  },
  {
    "id": "tag-2",
    "name": "Vegetarian",
    "slug": "vegetarian"
  },
  {
    "id": "tag-3",
    "name": "Gluten-Free",
    "slug": "gluten-free"
  }
]
```

#### List Units

```
URI: mealie://units
```

Returns a list of all ingredient units.

**Example Response:**
```json
[
  {
    "id": "unit-1",
    "name": "cup",
    "abbreviation": "c",
    "useAbbreviation": true
  },
  {
    "id": "unit-2",
    "name": "teaspoon",
    "abbreviation": "tsp",
    "useAbbreviation": true
  },
  {
    "id": "unit-3",
    "name": "tablespoon",
    "abbreviation": "tbsp",
    "useAbbreviation": true
  }
]
```

## Tools

Tools in MCP are functions that can be called to perform actions. The Mealie MCP Server provides the following tools:

### Recipe Tools

#### Get Recipe

```
Tool: get-recipe
```

Gets a recipe by its slug.

**Parameters:**
- `slug`: Recipe slug (string)

**Example Request:**
```json
{
  "name": "get-recipe",
  "arguments": {
    "slug": "chocolate-chip-cookies"
  }
}
```

#### Create Recipe from URL

```
Tool: create-recipe-from-url
```

Creates a recipe by scraping a URL.

**Parameters:**
- `url`: Recipe URL (string)

**Example Request:**
```json
{
  "name": "create-recipe-from-url",
  "arguments": {
    "url": "https://example.com/recipe/chocolate-chip-cookies"
  }
}
```

#### Parse Ingredients

```
Tool: parse-ingredients
```

Parses ingredient text into structured data.

**Parameters:**
- `ingredients`: Array of ingredient strings

**Example Request:**
```json
{
  "name": "parse-ingredients",
  "arguments": {
    "ingredients": [
      "2 cups flour",
      "1 tsp salt",
      "3 tbsp butter, softened"
    ]
  }
}
```

**Example Response:**
```json
[
  {
    "input": "2 cups flour",
    "quantity": 2,
    "unit": "cup",
    "food": "flour",
    "note": ""
  },
  {
    "input": "1 tsp salt",
    "quantity": 1,
    "unit": "teaspoon",
    "food": "salt",
    "note": ""
  },
  {
    "input": "3 tbsp butter, softened",
    "quantity": 3,
    "unit": "tablespoon",
    "food": "butter",
    "note": "softened"
  }
]
```

#### Create Recipe

```
Tool: create-recipe
```

Creates a basic recipe with minimal information.

**Parameters:**
- `name`: Recipe name (string)
- `description`: Recipe description (string, optional)

**Example Request:**
```json
{
  "name": "create-recipe",
  "arguments": {
    "name": "Simple Pasta",
    "description": "A quick and easy pasta dish."
  }
}
```

#### Update Recipe

```
Tool: update-recipe
```

Updates an existing recipe with new information.

**Parameters:**
- `slug`: Recipe slug (string)
- Various recipe fields (optional)

**Example Request:**
```json
{
  "name": "update-recipe",
  "arguments": {
    "slug": "simple-pasta",
    "name": "Simple Pasta with Garlic",
    "description": "A quick and easy pasta dish with garlic.",
    "recipeIngredient": [
      {
        "quantity": 8,
        "unit": { "id": "unit-id-4" },
        "food": "pasta",
        "note": "dry"
      },
      {
        "quantity": 2,
        "unit": { "id": "unit-id-3" },
        "food": "garlic",
        "note": "minced"
      }
    ],
    "recipeInstructions": [
      {
        "text": "Boil pasta according to package instructions."
      },
      {
        "text": "Sauté garlic in olive oil."
      },
      {
        "text": "Mix pasta and garlic. Serve hot."
      }
    ]
  }
}
```

### Meal Plan Tools

#### Generate Random Meal

```
Tool: generate-random-meal
```

Generates a random meal plan for a specific date.

**Parameters:**
- `date`: Date in YYYY-MM-DD format (string)
- `mealType`: Meal type (string, optional, default: "dinner")

**Example Request:**
```json
{
  "name": "generate-random-meal",
  "arguments": {
    "date": "2023-05-20",
    "mealType": "dinner"
  }
}
```

### Shopping List Tools

#### Create Shopping List

```
Tool: create-shopping-list
```

Creates a new shopping list.

**Parameters:**
- `name`: Shopping list name (string)
- `description`: Shopping list description (string, optional)

**Example Request:**
```json
{
  "name": "create-shopping-list",
  "arguments": {
    "name": "Weekly Groceries",
    "description": "Groceries for the week of May 15-21"
  }
}
```

#### Add Recipe to Shopping List

```
Tool: add-recipe-to-shopping-list
```

Adds a recipe's ingredients to a shopping list.

**Parameters:**
- `listId`: Shopping list ID (string)
- `recipeId`: Recipe ID (string)

**Example Request:**
```json
{
  "name": "add-recipe-to-shopping-list",
  "arguments": {
    "listId": "list-123",
    "recipeId": "recipe-456"
  }
}
```

### Suggestion Tools

#### Suggest Recipes

```
Tool: suggest-recipes
```

Gets recipe suggestions based on available foods.

**Parameters:**
- `foods`: Array of food names (string[], optional)
- `limit`: Maximum number of suggestions (number, optional, default: 5)

**Example Request:**
```json
{
  "name": "suggest-recipes",
  "arguments": {
    "foods": ["chicken", "rice", "broccoli"],
    "limit": 3
  }
}
```

**Example Response:**
```json
[
  {
    "recipe": {
      "id": "recipe-1",
      "slug": "chicken-stir-fry",
      "name": "Chicken Stir Fry"
    },
    "missingFoods": [],
    "missingTools": []
  },
  {
    "recipe": {
      "id": "recipe-2",
      "slug": "chicken-and-rice-casserole",
      "name": "Chicken and Rice Casserole"
    },
    "missingFoods": ["cream of mushroom soup"],
    "missingTools": []
  }
]
```

### Organizer Tools

#### Get Units

```
Tool: get-units
```

Gets all available ingredient units.

**Parameters:** None

**Example Request:**
```json
{
  "name": "get-units",
  "arguments": {}
}
```
