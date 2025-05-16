# Data Models

The wger MCP Server uses several data models defined in the wger API. This document provides an overview of the main data models used in the server.

## Exercise Models

### Exercise

Represents a specific exercise with details like name, description, muscles worked, etc.

```json
{
  "id": 123,
  "uuid": "00000000-0000-0000-0000-000000000000",
  "name": "Bench Press",
  "exercise_base": 456,
  "description": "Lie on a bench and press the weight upward...",
  "category": 10,
  "muscles": [4, 5],
  "muscles_secondary": [2, 3],
  "equipment": [1],
  "language": 2,
  "license": 1,
  "license_author": "wger.de",
  "variations": [124, 125]
}
```

### Muscle

Represents a muscle in the body.

```json
{
  "id": 4,
  "name": "Pectoralis major",
  "is_front": true,
  "image_url_main": "https://wger.de/static/images/muscles/main/muscle-4.svg",
  "image_url_secondary": "https://wger.de/static/images/muscles/secondary/muscle-4.svg"
}
```

### Equipment

Represents equipment used for exercises.

```json
{
  "id": 1,
  "name": "Barbell"
}
```

## Nutrition Models

### NutritionPlan

Represents a nutrition plan with details like description, goal calories, etc.

```json
{
  "id": 123,
  "description": "My weight loss plan",
  "creation_date": "2023-10-15",
  "has_goal_calories": true,
  "goal_calories": 2000
}
```

### NutritionDiary

Represents a diary entry for tracking food consumption.

```json
{
  "id": 123,
  "plan": 456,
  "ingredient": 789,
  "weight_unit": 1,
  "amount": 100,
  "datetime": "2023-10-15T08:00:00Z",
  "meal": 101
}
```

### Ingredient

Represents a food ingredient with nutritional information.

```json
{
  "id": 123,
  "name": "Chicken Breast",
  "energy": 165,
  "protein": 31,
  "carbohydrates": 0,
  "carbohydrates_sugar": 0,
  "fat": 3.6,
  "fat_saturated": 1,
  "fiber": 0,
  "sodium": 74,
  "license": 1,
  "license_author": "wger.de",
  "language": 2
}
```

### Meal

Represents a meal in a nutrition plan.

```json
{
  "id": 123,
  "plan": 456,
  "order": 1,
  "time": "08:00",
  "name": "Breakfast"
}
```

## Workout Models

### Routine

Represents a workout routine with details like name, description, start/end dates, etc.

```json
{
  "id": 123,
  "name": "My Workout Routine",
  "description": "A 4-day split focusing on strength",
  "created": "2023-10-15",
  "start": "2023-10-15",
  "end": "2023-12-15",
  "is_public": false,
  "is_template": false
}
```

### Day

Represents a day in a workout routine.

```json
{
  "id": 123,
  "routine": 456,
  "order": 1,
  "name": "Chest Day",
  "description": "Focus on chest and triceps",
  "is_rest": false,
  "need_logs_to_advance": false,
  "type": "custom"
}
```

### WorkoutSession

Represents a workout session with details like date, notes, impression, etc.

```json
{
  "id": 123,
  "date": "2023-10-15",
  "routine": 456,
  "day": 789,
  "notes": "Felt strong today",
  "impression": "3",
  "time_start": "18:00",
  "time_end": "19:00"
}
```

### WorkoutLog

Represents a log entry for tracking exercise performance.

```json
{
  "id": 123,
  "date": "2023-10-15T18:15:00Z",
  "exercise": 456,
  "session": 789,
  "routine": 101,
  "repetitions": "10",
  "repetitions_target": "10",
  "repetitions_unit": 1,
  "weight": "185",
  "weight_target": "185",
  "weight_unit": 1,
  "rir": "2",
  "rir_target": "2",
  "rest": 90,
  "rest_target": 90
}
```

### Slot

Represents a slot for exercises in a workout day.

```json
{
  "id": 123,
  "day": 456,
  "order": 1,
  "comment": "Chest exercises"
}
```

### SlotEntry

Represents an exercise entry in a slot.

```json
{
  "id": 123,
  "slot": 456,
  "exercise": 789,
  "order": 1,
  "weight": "185",
  "weight_unit": 1,
  "repetitions": "10",
  "repetitions_unit": 1,
  "comment": "Focus on form"
}
```

## Settings Models

### SetsConfig

Represents configuration for sets in a workout.

```json
{
  "id": 123,
  "name": "Standard",
  "description": "Standard sets configuration",
  "sets": 4,
  "repetitions": "10",
  "repetitions_unit": 1,
  "weight": "0",
  "weight_unit": 1,
  "rir": "2",
  "rest": 90
}
```

## Enum Values

### Impression

Represents the general impression of a workout session.

- `1`: Bad
- `2`: Neutral
- `3`: Good

### WeightUnit

Represents the unit of measurement for weight.

- `kg`: Metric (kilogram)
- `lb`: Imperial (pound)

### RepetitionUnit

Represents the unit of measurement for repetitions.

- `1`: Repetitions
- `2`: Until Failure
- `3`: Seconds
- `4`: Minutes
- `5`: Kilometers
- `6`: Miles

### DayType

Represents the type of workout day.

- `custom`: Custom
- `enom`: Every Minute on the Minute
- `amrap`: As Many Rounds as Possible
- `hiit`: High Intensity Interval Training
- `tabata`: Tabata
- `edt`: Escalating Density Training
- `rft`: Rounds for Time
- `afap`: As Fast as Possible

## Relationships Between Models

The following diagram illustrates the relationships between the main data models:

```
NutritionPlan
    |
    +-- Meal
    |     |
    |     +-- MealItem
    |           |
    |           +-- Ingredient
    |
    +-- NutritionDiary
          |
          +-- Ingredient

Routine
    |
    +-- Day
    |     |
    |     +-- Slot
    |           |
    |           +-- SlotEntry
    |                 |
    |                 +-- Exercise
    |
    +-- WorkoutSession
          |
          +-- WorkoutLog
                |
                +-- Exercise
```

## Working with Models

When using the wger MCP Server, you'll interact with these models through the resources and tools provided by the server. For example, you can:

- Fetch exercise information using the exercise resources
- Create nutrition plans and diary entries using the nutrition tools
- Track workout sessions and logs using the workout tools

The server handles the communication with the wger API and provides a consistent interface for working with these models.
