# Resources

Resources in the MCP server provide read access to data from the wger API. Each resource follows a consistent pattern with URI templates for accessing either lists of items or individual items.

## Exercise Resources

### Exercise Item Resource

- **URI Template**: `exercise://{id}`
- **Description**: Get detailed information about a specific exercise by ID
- **Parameters**:
  - `id`: Exercise ID (required)
- **Example**:
  ```
  exercise://123
  ```

### Exercise List Resource

- **URI Template**: `exercise://list{?equipment,exercise_base,language,license,limit,muscles,muscles_secondary,name,offset,ordering,uuid}`
- **Description**: Get a list of exercises with optional filtering
- **Parameters**:
  - `equipment`: Filter by equipment ID
  - `exercise_base`: Filter by exercise base ID
  - `language`: Filter by language code
  - `license`: Filter by license ID
  - `limit`: Maximum number of results to return
  - `muscles`: Filter by primary muscles
  - `muscles_secondary`: Filter by secondary muscles
  - `name`: Filter by exercise name
  - `offset`: Pagination offset
  - `ordering`: Field to order results by
  - `uuid`: Filter by UUID
- **Example**:
  ```
  exercise://list?muscles=4&limit=10
  ```

## Nutrition Resources

### Nutrition Diary List Resource

- **URI Template**: `nutritiondiary://list{?amount,datetime,datetime__date,datetime__gt,datetime__gte,datetime__lt,datetime__lte,ingredient,limit,offset,ordering,plan,weight_unit}`
- **Description**: Get a list of nutrition diary entries with optional filtering
- **Parameters**:
  - `amount`: Filter by amount
  - `datetime`: Filter by exact datetime
  - `datetime__date`: Filter by date
  - `datetime__gt`: Filter by datetime greater than
  - `datetime__gte`: Filter by datetime greater than or equal
  - `datetime__lt`: Filter by datetime less than
  - `datetime__lte`: Filter by datetime less than or equal
  - `ingredient`: Filter by ingredient ID
  - `limit`: Maximum number of results to return
  - `offset`: Pagination offset
  - `ordering`: Field to order results by
  - `plan`: Filter by nutrition plan ID
  - `weight_unit`: Filter by weight unit
- **Example**:
  ```
  nutritiondiary://list?plan=5&datetime__date=2023-10-15
  ```

### Nutrition Diary Item Resource

- **URI Template**: `nutritiondiary://{id}`
- **Description**: Get a specific nutrition diary entry by ID
- **Parameters**:
  - `id`: Nutrition diary entry ID (required)
- **Example**:
  ```
  nutritiondiary://123
  ```

### Nutrition Diary Nutritional Values Resource

- **URI Template**: `nutritiondiary://{id}/nutritional_values`
- **Description**: Get nutritional values for a specific diary entry
- **Parameters**:
  - `id`: Nutrition diary entry ID (required)
- **Example**:
  ```
  nutritiondiary://123/nutritional_values
  ```

### Nutrition Plan List Resource

- **URI Template**: `nutritionplan://list{?creation_date,description,has_goal_calories,limit,offset,ordering}`
- **Description**: Get a list of nutrition plans with optional filtering
- **Parameters**:
  - `creation_date`: Filter by creation date
  - `description`: Filter by description
  - `has_goal_calories`: Filter by whether the plan has goal calories
  - `limit`: Maximum number of results to return
  - `offset`: Pagination offset
  - `ordering`: Field to order results by
- **Example**:
  ```
  nutritionplan://list?has_goal_calories=true&limit=5
  ```

### Nutrition Plan Item Resource

- **URI Template**: `nutritionplan://{id}`
- **Description**: Get a specific nutrition plan by ID
- **Parameters**:
  - `id`: Nutrition plan ID (required)
- **Example**:
  ```
  nutritionplan://123
  ```

### Nutrition Plan Info List Resource

- **URI Template**: `nutritionplaninfo://list{?creation_date,description,has_goal_calories,limit,offset,ordering}`
- **Description**: Get a list of nutrition plan info with optional filtering
- **Parameters**: Same as Nutrition Plan List Resource
- **Example**:
  ```
  nutritionplaninfo://list?limit=10
  ```

## Ingredient Resources

### Ingredient List Resource

- **URI Template**: `ingredient://list{?carbohydrates,carbohydrates_sugar,code,created,created__gt,created__lt,energy,fat,fat_saturated,fiber,id,id__in,language,language__in,last_imported,last_imported__gt,last_imported__lt,last_update,last_update__gt,last_update__lt,license,license_author,limit,name,offset,ordering,protein,sodium,source_name,uuid}`
- **Description**: Get a list of ingredients with optional filtering
- **Parameters**:
  - `carbohydrates`: Filter by carbohydrates content
  - `carbohydrates_sugar`: Filter by sugar content
  - `code`: Filter by ingredient code
  - `created`: Filter by creation date
  - `energy`: Filter by energy content
  - `fat`: Filter by fat content
  - `fat_saturated`: Filter by saturated fat content
  - `fiber`: Filter by fiber content
  - `id`: Filter by ID
  - `id__in`: Filter by multiple IDs
  - `language`: Filter by language code
  - `language__in`: Filter by multiple language codes
  - `limit`: Maximum number of results to return
  - `name`: Filter by ingredient name
  - `offset`: Pagination offset
  - `ordering`: Field to order results by
  - `protein`: Filter by protein content
  - `sodium`: Filter by sodium content
  - `uuid`: Filter by UUID
- **Example**:
  ```
  ingredient://list?name=chicken&language=en&limit=10
  ```

### Ingredient Item Resource

- **URI Template**: `ingredient://{id}`
- **Description**: Get a specific ingredient by ID
- **Parameters**:
  - `id`: Ingredient ID (required)
- **Example**:
  ```
  ingredient://123
  ```

### Ingredient Get Values Resource

- **URI Template**: `ingredient://{id}/get_values{?amount,unit}`
- **Description**: Get nutritional values for a specific ingredient with optional amount and unit
- **Parameters**:
  - `id`: Ingredient ID (required)
  - `amount`: Amount of the ingredient
  - `unit`: Unit of measurement
- **Example**:
  ```
  ingredient://123/get_values?amount=100&unit=g
  ```

## Meal Resources

### Meal List Resource

- **URI Template**: `meal://list{?limit,offset,order,ordering,plan,time}`
- **Description**: Get a list of meals with optional filtering
- **Parameters**:
  - `limit`: Maximum number of results to return
  - `offset`: Pagination offset
  - `order`: Filter by order
  - `ordering`: Field to order results by
  - `plan`: Filter by nutrition plan ID
  - `time`: Filter by meal time
- **Example**:
  ```
  meal://list?plan=5&limit=10
  ```

### Meal Item Resource

- **URI Template**: `meal://{id}`
- **Description**: Get a specific meal by ID
- **Parameters**:
  - `id`: Meal ID (required)
- **Example**:
  ```
  meal://123
  ```

### Meal Nutritional Values Resource

- **URI Template**: `meal://{id}/nutritional_values`
- **Description**: Get nutritional values for a specific meal
- **Parameters**:
  - `id`: Meal ID (required)
- **Example**:
  ```
  meal://123/nutritional_values
  ```

## Workout Resources

### Routine List Resource

- **URI Template**: `routine://list{?created,description,end,is_public,is_template,limit,name,offset,ordering,start}`
- **Description**: Get a list of workout routines with optional filtering
- **Parameters**:
  - `created`: Filter by creation date
  - `description`: Filter by description
  - `end`: Filter by end date
  - `is_public`: Filter by public status
  - `is_template`: Filter by template status
  - `limit`: Maximum number of results to return
  - `name`: Filter by routine name
  - `offset`: Pagination offset
  - `ordering`: Field to order results by
  - `start`: Filter by start date
- **Example**:
  ```
  routine://list?is_public=true&limit=10
  ```

### Routine Item Resource

- **URI Template**: `routine://{id}`
- **Description**: Get a specific workout routine by ID
- **Parameters**:
  - `id`: Routine ID (required)
- **Example**:
  ```
  routine://123
  ```

### Day List Resource

- **URI Template**: `day://list{?description,id,is_rest,limit,name,need_logs_to_advance,offset,order,ordering}`
- **Description**: Get a list of workout days with optional filtering
- **Parameters**:
  - `description`: Filter by description
  - `id`: Filter by ID
  - `is_rest`: Filter by rest day status
  - `limit`: Maximum number of results to return
  - `name`: Filter by day name
  - `need_logs_to_advance`: Filter by whether logs are needed to advance
  - `offset`: Pagination offset
  - `order`: Filter by order
  - `ordering`: Field to order results by
- **Example**:
  ```
  day://list?is_rest=false&limit=10
  ```

### Workout Session List Resource

- **URI Template**: `workoutsession://list{?date,impression,limit,notes,offset,ordering,routine,time_end,time_start}`
- **Description**: Get a list of workout sessions with optional filtering
- **Parameters**:
  - `date`: Filter by date
  - `impression`: Filter by impression rating
  - `limit`: Maximum number of results to return
  - `notes`: Filter by notes
  - `offset`: Pagination offset
  - `ordering`: Field to order results by
  - `routine`: Filter by routine ID
  - `time_end`: Filter by end time
  - `time_start`: Filter by start time
- **Example**:
  ```
  workoutsession://list?date=2023-10-15&limit=10
  ```

### Workout Session Item Resource

- **URI Template**: `workoutsession://{id}`
- **Description**: Get a specific workout session by ID
- **Parameters**:
  - `id`: Workout session ID (required)
- **Example**:
  ```
  workoutsession://123
  ```

### Workout Log List Resource

- **URI Template**: `workoutlog://list{?date,exercise,limit,offset,ordering,repetitions,repetitions_unit,rir,routine,session,weight,weight_unit}`
- **Description**: Get a list of workout logs with optional filtering
- **Parameters**:
  - `date`: Filter by date
  - `exercise`: Filter by exercise ID
  - `limit`: Maximum number of results to return
  - `offset`: Pagination offset
  - `ordering`: Field to order results by
  - `repetitions`: Filter by repetitions
  - `repetitions_unit`: Filter by repetitions unit
  - `rir`: Filter by reps in reserve
  - `routine`: Filter by routine ID
  - `session`: Filter by session ID
  - `weight`: Filter by weight
  - `weight_unit`: Filter by weight unit
- **Example**:
  ```
  workoutlog://list?session=123&limit=20
  ```

### Workout Log Item Resource

- **URI Template**: `workoutlog://{id}`
- **Description**: Get a specific workout log by ID
- **Parameters**:
  - `id`: Workout log ID (required)
- **Example**:
  ```
  workoutlog://123
  ```

## Settings Resources

### Sets Config List Resource

- **URI Template**: `sets-config://list{?limit,offset,ordering}`
- **Description**: Get a list of sets configurations with optional filtering
- **Parameters**:
  - `limit`: Maximum number of results to return
  - `offset`: Pagination offset
  - `ordering`: Field to order results by
- **Example**:
  ```
  sets-config://list?limit=10
  ```

### Sets Config Item Resource

- **URI Template**: `sets-config://{id}`
- **Description**: Get a specific sets configuration by ID
- **Parameters**:
  - `id`: Sets config ID (required)
- **Example**:
  ```
  sets-config://123
  ```
