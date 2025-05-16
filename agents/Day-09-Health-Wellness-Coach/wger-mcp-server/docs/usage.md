# Usage Examples

This document provides examples of how to use the wger MCP Server with an MCP client. These examples demonstrate common workflows and how to combine resources and tools to accomplish specific tasks.

## Setting Up the Client

Before you can use the wger MCP Server, you need to set up an MCP client. Here's an example of how to set up a client using the MCP SDK:

```javascript
import { McpClient } from "@modelcontextprotocol/sdk/client/mcp.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

// Create a transport to connect to the server
const transport = new StdioClientTransport({
  command: "node dist/server.js",
  env: {
    WGER_API_TOKEN: "your_token_here"
  }
});

// Create the client
const client = new McpClient();

// Connect to the server
await client.connect(transport);

// Now you can use the client to interact with the server
```

## Fetching Exercise Information

### Get Information About a Specific Exercise

```javascript
// Get information about a specific exercise by ID
const exerciseInfo = await client.getResource("exercise://123");
console.log(exerciseInfo);
```

### Get a List of Exercises That Target the Chest

```javascript
// Get a list of exercises that target the chest (muscle ID 4)
const chestExercises = await client.getResource("exercise://list?muscles=4&limit=10");
console.log(chestExercises);
```

### Search for Exercises by Name

```javascript
// Get a list of exercises that contain "press" in the name
const pressExercises = await client.getResource("exercise://list?name=press&limit=10");
console.log(pressExercises);
```

## Working with Nutrition Plans

### Create a Nutrition Plan

```javascript
// Create a new nutrition plan
const nutritionPlan = await client.callTool("create-nutrition-plan", {
  description: "My weight loss plan",
  has_goal_calories: true,
  goal_calories: 2000
});
console.log(nutritionPlan);

// Get the nutrition plan ID
const planId = nutritionPlan.id;
```

### Add Meals to a Nutrition Plan

```javascript
// Add breakfast to the plan
const breakfast = await client.callTool("create-meal", {
  plan: planId,
  name: "Breakfast",
  time: "08:00"
});
console.log(breakfast);

// Add lunch to the plan
const lunch = await client.callTool("create-meal", {
  plan: planId,
  name: "Lunch",
  time: "12:00"
});
console.log(lunch);

// Add dinner to the plan
const dinner = await client.callTool("create-meal", {
  plan: planId,
  name: "Dinner",
  time: "18:00"
});
console.log(dinner);
```

### Search for Ingredients

```javascript
// Search for chicken ingredients
const chickenIngredients = await client.callTool("search-ingredients", {
  term: "chicken",
  language: "en"
});
console.log(chickenIngredients);

// Get the first chicken ingredient ID
const chickenId = chickenIngredients.results[0].id;
```

### Add Food to a Meal

```javascript
// Add chicken to breakfast
const breakfastChicken = await client.callTool("create-nutrition-diary-entry", {
  plan: planId,
  meal: breakfast.id,
  ingredient: chickenId,
  amount: 100,
  datetime: "2023-10-15T08:00:00Z"
});
console.log(breakfastChicken);
```

### Get Nutritional Values for a Meal

```javascript
// Get nutritional values for breakfast
const breakfastNutrition = await client.getResource(`meal://${breakfast.id}/nutritional_values`);
console.log(breakfastNutrition);
```

## Working with Workout Routines

### Create a Workout Routine

```javascript
// Create a new workout routine
const routine = await client.callTool("create-routine", {
  name: "My Workout Routine",
  description: "A 4-day split focusing on strength",
  start: "2023-10-15",
  end: "2023-12-15",
  is_public: false
});
console.log(routine);

// Get the routine ID
const routineId = routine.id;
```

### Add Days to a Routine

```javascript
// Add chest day to the routine
const chestDay = await client.callTool("create-day", {
  routine: routineId,
  name: "Chest Day",
  description: "Focus on chest and triceps",
  order: 1,
  is_rest: false
});
console.log(chestDay);

// Add back day to the routine
const backDay = await client.callTool("create-day", {
  routine: routineId,
  name: "Back Day",
  description: "Focus on back and biceps",
  order: 2,
  is_rest: false
});
console.log(backDay);

// Add leg day to the routine
const legDay = await client.callTool("create-day", {
  routine: routineId,
  name: "Leg Day",
  description: "Focus on legs and core",
  order: 3,
  is_rest: false
});
console.log(legDay);

// Add rest day to the routine
const restDay = await client.callTool("create-day", {
  routine: routineId,
  name: "Rest Day",
  description: "Active recovery",
  order: 4,
  is_rest: true
});
console.log(restDay);
```

### Add Exercises to a Day

```javascript
// Create a slot for chest exercises
const chestSlot = await client.callTool("create-slot", {
  day: chestDay.id,
  order: 1,
  comment: "Chest exercises"
});
console.log(chestSlot);

// Add bench press to the chest slot
const benchPress = await client.callTool("create-slot-entry", {
  slot: chestSlot.id,
  exercise: 123, // Bench press ID
  order: 1,
  weight: "185",
  weight_unit: 1,
  repetitions: "10",
  repetitions_unit: 1
});
console.log(benchPress);

// Add incline press to the chest slot
const inclinePress = await client.callTool("create-slot-entry", {
  slot: chestSlot.id,
  exercise: 124, // Incline press ID
  order: 2,
  weight: "135",
  weight_unit: 1,
  repetitions: "10",
  repetitions_unit: 1
});
console.log(inclinePress);
```

## Tracking Workouts

### Create a Workout Session

```javascript
// Create a new workout session
const session = await client.callTool("create-workout-session", {
  date: "2023-10-15",
  routine: routineId,
  day: chestDay.id,
  notes: "Felt strong today",
  impression: "3",
  time_start: "18:00",
  time_end: "19:00"
});
console.log(session);

// Get the session ID
const sessionId = session.id;
```

### Log Exercises

```javascript
// Log bench press
const benchPressLog = await client.callTool("create-workout-log", {
  exercise: 123, // Bench press ID
  date: "2023-10-15T18:15:00Z",
  session: sessionId,
  routine: routineId,
  repetitions: "10",
  weight: "185",
  weight_unit: 1
});
console.log(benchPressLog);

// Log incline press
const inclinePressLog = await client.callTool("create-workout-log", {
  exercise: 124, // Incline press ID
  date: "2023-10-15T18:30:00Z",
  session: sessionId,
  routine: routineId,
  repetitions: "10",
  weight: "135",
  weight_unit: 1
});
console.log(inclinePressLog);
```

### Update a Workout Log

```javascript
// Update the bench press log
const updatedBenchPressLog = await client.callTool("update-workout-log", {
  id: benchPressLog.id,
  repetitions: "12",
  weight: "195"
});
console.log(updatedBenchPressLog);
```

### Get Workout Session Information

```javascript
// Get information about the workout session
const sessionInfo = await client.getResource(`workoutsession://${sessionId}`);
console.log(sessionInfo);
```

### Get Workout Logs for a Session

```javascript
// Get all workout logs for the session
const sessionLogs = await client.getResource(`workoutlog://list?session=${sessionId}`);
console.log(sessionLogs);
```

## Using Prompts

### Get a Predefined Prompt

```javascript
// Get the create-workout-plan prompt
const workoutPlanPrompt = await client.getPrompt("create-workout-plan");
console.log(workoutPlanPrompt);
```

### Use a Prompt with an LLM

```javascript
// Use the prompt with an LLM (example using a hypothetical LLM client)
const llmResponse = await llmClient.generateResponse({
  messages: workoutPlanPrompt.messages,
  tools: client.getTools(),
  resources: client.getResources()
});
console.log(llmResponse);
```

## Combining Resources and Tools

The real power of the wger MCP Server comes from combining resources and tools to create complete workflows. Here's an example of a complete workflow for creating a workout plan, tracking a workout, and analyzing performance:

```javascript
// 1. Create a workout routine
const routine = await client.callTool("create-routine", {
  name: "My Workout Routine",
  description: "A 4-day split focusing on strength",
  start: "2023-10-15",
  end: "2023-12-15"
});

// 2. Add days to the routine
const chestDay = await client.callTool("create-day", {
  routine: routine.id,
  name: "Chest Day",
  order: 1
});

// 3. Find exercises for chest day
const chestExercises = await client.getResource("exercise://list?muscles=4&limit=5");

// 4. Add exercises to chest day
const chestSlot = await client.callTool("create-slot", {
  day: chestDay.id,
  order: 1
});

for (let i = 0; i < chestExercises.results.length; i++) {
  await client.callTool("create-slot-entry", {
    slot: chestSlot.id,
    exercise: chestExercises.results[i].id,
    order: i + 1
  });
}

// 5. Create a workout session
const session = await client.callTool("create-workout-session", {
  date: "2023-10-15",
  routine: routine.id,
  day: chestDay.id
});

// 6. Log exercises
for (let i = 0; i < chestExercises.results.length; i++) {
  await client.callTool("create-workout-log", {
    exercise: chestExercises.results[i].id,
    date: `2023-10-15T${18 + i}:00:00Z`,
    session: session.id,
    routine: routine.id,
    repetitions: "10",
    weight: "100"
  });
}

// 7. Get workout logs for analysis
const logs = await client.getResource(`workoutlog://list?session=${session.id}`);
console.log(logs);
```

This workflow demonstrates how to create a complete workout tracking system using the wger MCP Server.
