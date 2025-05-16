# Tools

Tools in the MCP server provide write access to the wger API, allowing clients to create, update, and delete data.

## Nutrition Tools

### Create Nutrition Plan Tool

- **Name**: `create-nutrition-plan`
- **Description**: Create a new nutrition plan
- **Parameters**:
  - `description`: Description of the nutrition plan (optional)
  - `has_goal_calories`: Whether the plan has goal calories (optional)
  - `goal_calories`: Goal calories for the plan (optional)
- **Example**:
  ```javascript
  const result = await callTool("create-nutrition-plan", {
    description: "My weight loss plan",
    has_goal_calories: true,
    goal_calories: 2000
  });
  ```

### Create Nutrition Diary Entry Tool

- **Name**: `create-nutrition-diary-entry`
- **Description**: Create a new nutrition diary entry
- **Parameters**:
  - `plan`: Nutrition plan ID (required)
  - `ingredient`: Ingredient ID (required)
  - `amount`: Amount of the ingredient (required)
  - `datetime`: Date and time of the entry (required)
  - `meal`: Meal ID (optional)
  - `weight_unit`: Weight unit ID (optional)
- **Example**:
  ```javascript
  const result = await callTool("create-nutrition-diary-entry", {
    plan: 123,
    ingredient: 456,
    amount: 100,
    datetime: "2023-10-15T08:00:00Z",
    meal: 789
  });
  ```

## Ingredient Tools

### Search Ingredients Tool

- **Name**: `search-ingredients`
- **Description**: Search for ingredients by name
- **Parameters**:
  - `term`: Search term for ingredient name (required)
  - `language`: Comma separated list of language codes to search (required)
- **Example**:
  ```javascript
  const result = await callTool("search-ingredients", {
    term: "chicken",
    language: "en,de"
  });
  ```

## Meal Tools

### Create Meal Tool

- **Name**: `create-meal`
- **Description**: Create a new meal
- **Parameters**:
  - `plan`: Nutrition plan ID (required)
  - `name`: Name of the meal (optional)
  - `time`: Time of the meal in HH:MM format (optional)
- **Example**:
  ```javascript
  const result = await callTool("create-meal", {
    plan: 123,
    name: "Breakfast",
    time: "08:00"
  });
  ```

## Workout Tools

### Create Routine Tool

- **Name**: `create-routine`
- **Description**: Create a new workout routine
- **Parameters**:
  - `name`: Name of the routine (required)
  - `description`: Description of the routine (optional)
  - `start`: Start date of the routine (required)
  - `end`: End date of the routine (required)
  - `fit_in_week`: Whether to fit the routine in a week (optional)
  - `is_template`: Whether the routine is a template (optional)
  - `is_public`: Whether the routine is public (optional)
- **Example**:
  ```javascript
  const result = await callTool("create-routine", {
    name: "My Workout Routine",
    description: "A 4-day split focusing on strength",
    start: "2023-10-15",
    end: "2023-12-15",
    is_public: false
  });
  ```

### Create Day Tool

- **Name**: `create-day`
- **Description**: Create a new workout day
- **Parameters**:
  - `routine`: Routine ID (required)
  - `name`: Name of the day (optional)
  - `description`: Description of the day (optional)
  - `order`: Order of the day in the routine (optional)
  - `is_rest`: Whether this is a rest day (optional)
  - `need_logs_to_advance`: Whether logs are needed to advance to the next day (optional)
  - `type`: Type of the day (optional)
- **Example**:
  ```javascript
  const result = await callTool("create-day", {
    routine: 123,
    name: "Chest Day",
    description: "Focus on chest and triceps",
    order: 1,
    is_rest: false
  });
  ```

### Create Workout Session Tool

- **Name**: `create-workout-session`
- **Description**: Create a new workout session
- **Parameters**:
  - `date`: Date of the workout session (required)
  - `routine`: Routine ID (optional)
  - `day`: Day ID (optional)
  - `notes`: Notes about the workout session (optional)
  - `impression`: General impression (optional)
  - `time_start`: Start time of the workout (optional)
  - `time_end`: End time of the workout (optional)
- **Example**:
  ```javascript
  const result = await callTool("create-workout-session", {
    date: "2023-10-15",
    routine: 123,
    day: 456,
    notes: "Felt strong today",
    impression: "3",
    time_start: "18:00",
    time_end: "19:00"
  });
  ```

### Update Workout Session Tool

- **Name**: `update-workout-session`
- **Description**: Update an existing workout session
- **Parameters**:
  - `id`: Workout session ID (required)
  - `date`: Date of the workout session (optional)
  - `routine`: Routine ID (optional)
  - `day`: Day ID (optional)
  - `notes`: Notes about the workout session (optional)
  - `impression`: General impression (optional)
  - `time_start`: Start time of the workout (optional)
  - `time_end`: End time of the workout (optional)
- **Example**:
  ```javascript
  const result = await callTool("update-workout-session", {
    id: 123,
    notes: "Updated notes about the workout",
    impression: "2"
  });
  ```

### Delete Workout Session Tool

- **Name**: `delete-workout-session`
- **Description**: Delete a workout session
- **Parameters**:
  - `id`: Workout session ID (required)
- **Example**:
  ```javascript
  const result = await callTool("delete-workout-session", {
    id: 123
  });
  ```

### Create Workout Log Tool

- **Name**: `create-workout-log`
- **Description**: Create a new workout log entry
- **Parameters**:
  - `exercise`: Exercise ID (required)
  - `date`: Date and time of the workout log (required)
  - `session`: Workout session ID (optional)
  - `routine`: Routine ID (optional)
  - `repetitions`: Number of repetitions performed (optional)
  - `repetitions_target`: Target number of repetitions (optional)
  - `repetitions_unit`: Repetition unit ID (optional)
  - `weight`: Weight used (optional)
  - `weight_target`: Target weight (optional)
  - `weight_unit`: Weight unit ID (optional)
  - `rir`: Reps in reserve (optional)
  - `rir_target`: Target reps in reserve (optional)
  - `rest`: Rest time in seconds (optional)
  - `rest_target`: Target rest time in seconds (optional)
- **Example**:
  ```javascript
  const result = await callTool("create-workout-log", {
    exercise: 123,
    date: "2023-10-15T18:15:00Z",
    session: 456,
    repetitions: "10",
    weight: "185",
    weight_unit: 1
  });
  ```

### Update Workout Log Tool

- **Name**: `update-workout-log`
- **Description**: Update an existing workout log entry
- **Parameters**:
  - `id`: Workout log ID (required)
  - `exercise`: Exercise ID (optional)
  - `date`: Date and time of the workout log (optional)
  - `session`: Workout session ID (optional)
  - `routine`: Routine ID (optional)
  - `repetitions`: Number of repetitions performed (optional)
  - `repetitions_target`: Target number of repetitions (optional)
  - `repetitions_unit`: Repetition unit ID (optional)
  - `weight`: Weight used (optional)
  - `weight_target`: Target weight (optional)
  - `weight_unit`: Weight unit ID (optional)
  - `rir`: Reps in reserve (optional)
  - `rir_target`: Target reps in reserve (optional)
  - `rest`: Rest time in seconds (optional)
  - `rest_target`: Target rest time in seconds (optional)
- **Example**:
  ```javascript
  const result = await callTool("update-workout-log", {
    id: 123,
    repetitions: "12",
    weight: "195"
  });
  ```

### Delete Workout Log Tool

- **Name**: `delete-workout-log`
- **Description**: Delete a workout log entry
- **Parameters**:
  - `id`: Workout log ID (required)
- **Example**:
  ```javascript
  const result = await callTool("delete-workout-log", {
    id: 123
  });
  ```

### Create Slot Tool

- **Name**: `create-slot`
- **Description**: Create a new slot for exercises in a workout day
- **Parameters**:
  - `day`: Day ID (required)
  - `order`: Order of the slot in the day (optional)
  - `comment`: Comment for the slot (optional)
- **Example**:
  ```javascript
  const result = await callTool("create-slot", {
    day: 123,
    order: 1,
    comment: "Chest exercises"
  });
  ```

### Create Slot Entry Tool

- **Name**: `create-slot-entry`
- **Description**: Create a new slot entry for an exercise
- **Parameters**:
  - `slot`: Slot ID (required)
  - `exercise`: Exercise ID (required)
  - `order`: Order of the entry in the slot (optional)
  - `weight`: Weight to use (optional)
  - `weight_unit`: Weight unit ID (optional)
  - `repetitions`: Number of repetitions (optional)
  - `repetitions_unit`: Repetition unit ID (optional)
  - `comment`: Comment for the slot entry (optional)
- **Example**:
  ```javascript
  const result = await callTool("create-slot-entry", {
    slot: 123,
    exercise: 456,
    order: 1,
    weight: "185",
    weight_unit: 1,
    repetitions: "10",
    repetitions_unit: 1
  });
  ```
