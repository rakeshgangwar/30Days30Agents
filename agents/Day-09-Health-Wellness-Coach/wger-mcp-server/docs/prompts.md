# Prompts

The wger MCP Server provides several predefined prompts for common user interactions. These prompts can be used to guide users through common workflows and provide examples of how to interact with the server.

## Create Workout Plan Prompt

- **Name**: `create-workout-plan`
- **Description**: Create a personalized workout plan based on your goals and availability
- **Example User Message**:
  ```
  I want to create a workout plan with the goal of building muscle. I can work out 3 days per week, and I have about 60 minutes available for each session. My fitness level is beginner. I have access to a full gym. Can you create a detailed workout plan for me?
  ```

### Implementation

```javascript
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
```

### Usage

This prompt can be used to help users create a personalized workout plan based on their goals, availability, and fitness level. The LLM can use the exercise resources to find appropriate exercises and create a structured workout plan.

## Create Workout Routine Prompt

- **Name**: `create-workout-routine`
- **Description**: Create a personalized workout routine
- **Example User Message**:
  ```
  I want to create a workout routine for building muscle. I can work out 4 days a week, and I have access to a full gym. I'm an intermediate lifter and want to focus on my upper body. Can you help me create a suitable workout routine?
  ```

### Implementation

```javascript
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
```

### Usage

This prompt can be used to help users create a structured workout routine with specific days and exercises. The LLM can use the routine, day, and slot resources to create a complete workout routine that can be tracked over time.

## Track Workout Session Prompt

- **Name**: `track-workout-session`
- **Description**: Track a workout session with exercises and performance
- **Example User Message**:
  ```
  I just completed my chest and triceps workout. I did 4 sets of bench press with 185 lbs (10, 8, 8, 6 reps), 3 sets of incline dumbbell press with 65 lbs dumbbells (10, 8, 8 reps), 3 sets of cable flyes with 50 lbs (12 reps each), and 3 sets of tricep pushdowns with 70 lbs (12, 10, 10 reps). The workout took me about 1 hour and I felt good about my performance. Can you help me log this workout session?
  ```

### Implementation

```javascript
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
```

### Usage

This prompt can be used to help users track their workout sessions and log their exercise performance. The LLM can use the workout session and workout log resources to record the user's workout data, including exercises, sets, repetitions, and weights.

## Creating Custom Prompts

You can create custom prompts for your specific use cases by following the pattern shown above. Here's a template for creating a custom prompt:

```javascript
server.prompt(
  "prompt-name",
  "Prompt description",
  () => {
    return {
      messages: [{
        role: "user",
        content: {
          type: "text",
          text: "Example user message"
        }
      }]
    };
  }
);
```

Replace `"prompt-name"`, `"Prompt description"`, and `"Example user message"` with your own values.

## Best Practices for Prompts

When creating prompts, consider the following best practices:

1. **Be specific**: Clearly define the purpose of the prompt and what the user is trying to accomplish.
2. **Provide context**: Include relevant information in the example user message to help the LLM understand the user's needs.
3. **Use realistic examples**: Use examples that reflect how real users would interact with the system.
4. **Keep it concise**: Keep the example user message concise while still providing enough information for the LLM to understand the task.
5. **Consider edge cases**: Think about potential edge cases or variations in how users might express their needs.

## Using Prompts with MCP Clients

To use a prompt with an MCP client, you can call the `getPrompt` method with the prompt name:

```javascript
const prompt = await client.getPrompt("create-workout-plan");
```

This will return the prompt object, which you can then use to generate a response from the LLM.
