import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import dotenv from "dotenv";
import { registerNutritionResources } from "./nutrition.js";
import { registerIngredientResources } from "./ingredients.js";
import { registerMealResources } from "./meals.js";
import { registerRoutineResources } from "./routines.js";
import { registerSettingsResources } from "./settings.js";
import { registerExerciseResources } from "./exercises.js";
import { registerTemplatesResources } from "./templates.js";

// Load environment variables from .env file
dotenv.config();

// Environment variables are loaded by dotenv.config() above

// Create the MCP server instance
const server = new McpServer({
  name: "wger MCP Server",
  version: "0.1.0"
});

// ==================== RESOURCES ====================

// ==================== TOOLS ====================

// // Get muscle details tool
// server.tool(
//   "get-muscle-details",
//   {
//     id: z.number().int().positive().describe("Muscle ID")
//   },
//   async ({ id }) => {
//     try {
//       const muscleData = await fetchWgerApi(`/muscle/${id}/`);

//       return {
//         content: [{
//           type: "text",
//           text: JSON.stringify(muscleData, null, 2)
//         }]
//       };
//     } catch (error) {
//       return {
//         content: [{
//           type: "text",
//           text: `Error fetching muscle details: ${error}`
//         }],
//         isError: true
//       };
//     }
//   }
// );

// ==================== PROMPTS ====================

// Workout plan prompt
server.prompt(
  "create-workout-plan",
  "Create a personalized workout plan based on your goals and availability",
  () => {
    return {
      messages: [{
        role: "user",
        content: {
          type: "text",
          text: "I want to create a workout plan with the goal of building muscle. I can work out 3 days per week, and I have about 60 minutes available for each session. My fitness level is beginner. I have access to a full gym. Can you create a detailed workout plan for me?"
        }
      }]
    };
  }
);

// Register exercise resources and tools
registerExerciseResources(server);

// Register nutrition resources and tools
registerNutritionResources(server);

// Register ingredient resources and tools
registerIngredientResources(server);

// Register meal resources and tools
registerMealResources(server);

// Register routine resources and tools
registerRoutineResources(server);

// Register settings resources and tools
registerSettingsResources(server);

// Register templates resources and tools
registerTemplatesResources(server);

// Start the server using stdio transport
const transport = new StdioServerTransport();
server.connect(transport).catch((err) => {
  console.error("Failed to start MCP server:", err);
});
