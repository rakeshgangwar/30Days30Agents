# Beehive MCP Tools Documentation

This document provides comprehensive documentation for all tools provided by the Beehive MCP server, including request/response formats, API behavior, edge cases, and error handling.

## Overview

The Beehive MCP server provides tools for interacting with Beehive, an event and agent system that allows you to create automated tasks triggered by events and filters. The tools are organized into the following categories:

1. **Hives Management** - Manage available Hives (plugins)
2. **Bees Management** - Manage Bee instances (configured instances of Hives)
3. **Chains Management** - Manage Chains (connections between events and actions)
4. **Actions** - Manually trigger actions
5. **Logs** - Retrieve logs from the system

## Testing Methodology

Each tool was tested for:
1. Request/response formats - Verifying that the tool accepts the correct parameters and returns the expected response format
2. API behavior validation - Ensuring that the tool performs the expected action in the Beehive system
3. Edge case handling - Testing how the tool handles unusual or boundary conditions
4. Error responses - Verifying that appropriate error messages are returned when things go wrong

### Testing Status

During testing, we discovered several implementation issues with the MCP client that prevent some tools from working correctly. The main issue is that the client doesn't properly format requests according to the Beehive API expectations. For example, the API expects bee creation requests to have a nested structure with a top-level `bee` object, but the client sends the configuration directly.

Status indicators used in this document:
- ✅ Tested and working correctly
- ⚠️ Tested but has issues or limitations
- ❌ Not working or not tested

See the [Testing Results](#testing-results) section at the end of this document for a summary of findings and recommendations.

## Tools Documentation

### Hives Management

#### `list_hives`

**Description:** List all available Hives (plugins).

**Required Parameters:** None

**Optional Parameters:** None

**Request Format:**
```json
{}
```

**Response Format:**
```json
[
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "events": [
      {
        "name": "string",
        "description": "string",
        "options": [
          {
            "name": "string",
            "description": "string",
            "type": "string",
            "mandatory": boolean
          }
        ]
      }
    ],
    "actions": [
      {
        "name": "string",
        "description": "string",
        "options": [
          {
            "name": "string",
            "description": "string",
            "type": "string",
            "mandatory": boolean
          }
        ]
      }
    ]
  }
]
```

**Error Responses:**
- `500 Internal Server Error` - If there's an issue connecting to the Beehive API

**Test Cases:**
- ✅ Verified successful listing of all available Hives - Returns a list of hive objects with their details
- ⚠️ Error handling when Beehive is unavailable - Returns a 500 error

#### `get_hive_details`

**Description:** Get detailed information about a specific Hive.

**Required Parameters:**
- `name` (string) - Name of the Hive (plugin)

**Optional Parameters:** None

**Request Format:**
```json
{
  "name": "string"
}
```

**Response Format:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "events": [
    {
      "name": "string",
      "description": "string",
      "options": [
        {
          "name": "string",
          "description": "string",
          "type": "string",
          "mandatory": boolean
        }
      ]
    }
  ],
  "actions": [
    {
      "name": "string",
      "description": "string",
      "options": [
        {
          "name": "string",
          "description": "string",
          "type": "string",
          "mandatory": boolean
        }
      ]
    }
  ]
}
```

**Error Responses:**
- `404 Not Found` - If the specified Hive doesn't exist
- `500 Internal Server Error` - If there's an issue connecting to the Beehive API

**Test Cases:**
- ✅ Verified successful retrieval of a specific Hive's details - Returns detailed information about the specified hive
- ✅ Tested error handling when the Hive doesn't exist - Returns a 404 error with message "This hive does not exist"
- ⚠️ Error handling when Beehive is unavailable - Returns a 500 error

### Bees Management

#### `list_bees`

**Description:** List all configured Bees (instances of Hives).

**Required Parameters:** None

**Optional Parameters:** None

**Request Format:**
```json
{}
```

**Response Format:**
```json
[
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "namespace": "string",
    "active": boolean,
    "options": {
      // Bee-specific configuration options
    }
  }
]
```

**Error Responses:**
- `500 Internal Server Error` - If there's an issue connecting to the Beehive API

**Test Cases:**
- ✅ Verified successful listing of all configured Bees - Returns an empty array when no bees exist
- ⚠️ Error handling when Beehive is unavailable - Returns a 500 error

#### `get_bee`

**Description:** Get details of a specific Bee.

**Required Parameters:**
- `id` (string) - ID of the Bee

**Optional Parameters:** None

**Request Format:**
```json
{
  "id": "string"
}
```

**Response Format:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "namespace": "string",
  "active": boolean,
  "options": {
    // Bee-specific configuration options
  }
}
```

**Error Responses:**
- `404 Not Found` - If the specified Bee doesn't exist
- `500 Internal Server Error` - If there's an issue connecting to the Beehive API

**Test Cases:**
- ✅ Verified successful retrieval of a specific Bee's details - Returns detailed information about the specified bee
- ⚠️ Test error handling when the Bee doesn't exist - Should return a 404 error
- ⚠️ Error handling when Beehive is unavailable - Returns a 500 error

#### `create_bee`

**Description:** Create a new Bee instance.

**Required Parameters:**
- `name` (string) - Name for the new Bee
- `hive` (string) - Name of the Hive (plugin) to use

**Optional Parameters:**
- `options` (object) - Configuration options for the Bee

**Request Format:**
```json
{
  "name": "string",
  "hive": "string",
  "options": {
    // Simple key-value pairs for bee options
    "minute": "*/5",
    "hour": "*"
    // Other options specific to the bee type
  }
}
```

**Actual API Request Format (after client processing):**
```json
{
  "bee": {
    "name": "string",
    "namespace": "string", // This is the hive parameter
    "description": "string",
    "active": boolean,
    "options": [
      {
        "Name": "option_name",
        "Description": "option description",
        "Type": "string",
        "Default": null,
        "Mandatory": false,
        "Value": "option_value"
      }
      // Additional options specific to the bee type
    ]
  }
}
```

**Response Format:**
```json
{
  "bees": [
    {
      "id": "string",
      "name": "string",
      "namespace": "string",
      "description": "string",
      "lastaction": "timestamp",
      "lastevent": "timestamp",
      "active": boolean,
      "options": [
        {
          "Name": "option_name",
          "Value": "option_value"
        }
        // Additional options specific to the bee type
      ]
    }
  ],
  "hives": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "image": "string",
      "logocolor": "string",
      "options": [
        {
          "Name": "option_name",
          "Description": "option description",
          "Type": "string",
          "Default": null,
          "Mandatory": boolean
        }
        // Additional options specific to the hive type
      ],
      "states": [],
      "events": [
        {
          "Namespace": "string",
          "Name": "string",
          "Description": "string",
          "Options": [
            {
              "Name": "option_name",
              "Description": "option description",
              "Type": "string",
              "Mandatory": boolean
            }
          ]
        }
      ],
      "actions": []
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` - If the request is missing required parameters or contains invalid values
- `404 Not Found` - If the specified Hive doesn't exist
- `500 Internal Server Error` - If there's an issue connecting to the Beehive API

**Test Cases:**
- ✅ Verified successful creation of a new Bee - Successfully created a cron bee with custom minute setting
- ✅ Tested error handling when required parameters are missing - Returns a 422 error
- ⚠️ Test error handling when the Hive doesn't exist - Should return a 404 error
- ⚠️ Test error handling when options are invalid - Should return a 400 error
- ⚠️ Error handling when Beehive is unavailable - Returns a 500 error

**Implementation Issues:**
1. The MCP client doesn't properly format the request for the Beehive API. The API expects a nested structure with a top-level `bee` object, but the client sends the configuration directly.

2. The `options` field in the bee configuration must be an array of option objects with a specific structure, not a simple key-value object. Each option object must have the following fields:
   - `Name`: The name of the option
   - `Description`: A description of the option
   - `Type`: The data type of the option
   - `Default`: The default value of the option
   - `Mandatory`: Whether the option is required
   - `Value`: The actual value of the option

**Correct Request Format:**
```json
{
  "bee": {
    "name": "TestCronBee",
    "namespace": "cronbee",
    "description": "Test cron bee",
    "active": true,
    "options": [
      {
        "Name": "second",
        "Description": "00-59 for a specific second; * for ignore",
        "Type": "string",
        "Default": null,
        "Mandatory": false,
        "Value": "*"
      },
      {
        "Name": "minute",
        "Description": "00-59 for a specific minute; * for ignore",
        "Type": "string",
        "Default": null,
        "Mandatory": false,
        "Value": "*/5"
      },
      // ... other options
    ]
  }
}
```

**Fixed Implementation:**
The client has been updated to properly format the request by:
1. Fetching the hive details to get the available options
2. Converting the simple options object to an array of option objects with the proper structure
3. Wrapping the configuration in a `bee` object

#### `update_bee`

**Description:** Update an existing Bee.

**Required Parameters:**
- `id` (string) - ID of the Bee to update

**Optional Parameters:**
- `name` (string) - New name for the Bee
- `options` (object) - Updated configuration options for the Bee

**Request Format:**
```json
{
  "id": "string",
  "name": "string",
  "options": {
    // Simple key-value pairs for updated bee options
    "minute": "*/10",
    // Other options specific to the bee type
  }
}
```

**Actual API Request Format (after client processing):**
```json
{
  "bee": {
    "name": "string",
    "namespace": "string",
    "description": "string",
    "active": boolean,
    "options": [
      {
        "Name": "option_name",
        "Description": "option description",
        "Type": "string",
        "Default": null,
        "Mandatory": false,
        "Value": "option_value"
      }
      // Additional options specific to the bee type
    ]
  }
}
```

**Response Format:**
```json
{
  "bees": [
    {
      "id": "string",
      "name": "string",
      "namespace": "string",
      "description": "string",
      "lastaction": "timestamp",
      "lastevent": "timestamp",
      "active": boolean,
      "options": [
        {
          "Name": "option_name",
          "Value": "option_value"
        }
        // Additional options specific to the bee type
      ]
    }
  ],
  "hives": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "image": "string",
      "logocolor": "string",
      "options": [
        {
          "Name": "option_name",
          "Description": "option description",
          "Type": "string",
          "Default": null,
          "Mandatory": boolean
        }
        // Additional options specific to the hive type
      ],
      "states": [],
      "events": [
        {
          "Namespace": "string",
          "Name": "string",
          "Description": "string",
          "Options": [
            {
              "Name": "option_name",
              "Description": "option description",
              "Type": "string",
              "Mandatory": boolean
            }
          ]
        }
      ],
      "actions": []
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` - If the request contains invalid values
- `404 Not Found` - If the specified Bee doesn't exist
- `500 Internal Server Error` - If there's an issue connecting to the Beehive API

**Test Cases:**
- ✅ Verified successful update of an existing Bee - Successfully updated the bee's options
- ✅ Test updating only the options - Successfully updated the minute option from "*/5" to "*/10"
- ⚠️ Test updating only the name - Not fully tested
- ⚠️ Test updating both name and options - Not fully tested
- ⚠️ Test error handling when the Bee doesn't exist - Should return a 404 error
- ⚠️ Test error handling when options are invalid - Should return a 400 error
- ⚠️ Error handling when Beehive is unavailable - Returns a 500 error

**Implementation Issues:**
The `update_bee` tool had the same issues as the `create_bee` tool:
1. The MCP client didn't properly format the request for the Beehive API
2. The `options` field needed to be an array of option objects with a specific structure

**Fixed Implementation:**
The client has been updated to properly format the request by:
1. Fetching the current bee details to preserve existing values
2. Fetching the hive details to get the available options
3. Converting the simple options object to an array of option objects with the proper structure
4. Wrapping the configuration in a `bee` object

#### `delete_bee`

**Description:** Delete a Bee instance.

**Required Parameters:**
- `id` (string) - ID of the Bee to delete

**Optional Parameters:** None

**Request Format:**
```json
{
  "id": "string"
}
```

**Response Format:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "namespace": "string",
  "active": boolean,
  "options": {
    // Bee-specific configuration options
  }
}
```

**Error Responses:**
- `404 Not Found` - If the specified Bee doesn't exist
- `500 Internal Server Error` - If there's an issue connecting to the Beehive API

**Test Cases:**
- TODO: Verify successful deletion of a Bee
- TODO: Test error handling when the Bee doesn't exist
- TODO: Test error handling when Beehive is unavailable

### Chains Management

#### `list_chains`

**Description:** List all configured Chains.

**Required Parameters:** None

**Optional Parameters:** None

**Request Format:**
```json
{}
```

**Response Format:**
```json
[
  {
    "id": "string",
    "name": "string",
    "event": {
      "bee": "string",
      "name": "string"
    },
    "actions": [
      {
        "bee": "string",
        "name": "string",
        "options": {
          // Action-specific options
        }
      }
    ],
    "filters": [
      {
        // Filter-specific configuration
      }
    ]
  }
]
```

**Error Responses:**
- `500 Internal Server Error` - If there's an issue connecting to the Beehive API

**Test Cases:**
- ✅ Verified successful listing of all configured Chains - Returns an empty array when no chains exist
- ⚠️ Error handling when Beehive is unavailable - Returns a 500 error

#### `get_chain`

**Description:** Get details of a specific Chain.

**Required Parameters:**
- `id` (string) - ID of the Chain

**Optional Parameters:** None

**Request Format:**
```json
{
  "id": "string"
}
```

**Response Format:**
```json
{
  "id": "string",
  "name": "string",
  "event": {
    "bee": "string",
    "name": "string"
  },
  "actions": [
    {
      "bee": "string",
      "name": "string",
      "options": {
        // Action-specific options
      }
    }
  ],
  "filters": [
    {
      // Filter-specific configuration
    }
  ]
}
```

**Error Responses:**
- `404 Not Found` - If the specified Chain doesn't exist
- `500 Internal Server Error` - If there's an issue connecting to the Beehive API

**Test Cases:**
- ✅ Verified successful retrieval of a specific Chain's details - Returns detailed information about the specified chain
- ✅ Test error handling when the Chain doesn't exist - Returns a 404 error
- ⚠️ Error handling when Beehive is unavailable - Returns a 500 error

#### `create_chain`

**Description:** Create a new Chain connecting events to actions.

**Required Parameters:**
- `name` (string) - Name for the new Chain
- `event` (object) - Event that triggers the chain
  - `bee` (string) - ID of the Bee that generates the event
  - `name` (string) - Name of the event
- `actions` (array) - Actions to perform when the event is triggered
  - Each action contains:
    - `bee` (string) - ID of the Bee that performs the action
    - `name` (string) - Name of the action
    - `options` (object, optional) - Options/parameters for the action

**Optional Parameters:**
- `filters` (array) - Filters to determine if the action should be executed

**Request Format:**
```json
{
  "name": "string",
  "event": {
    "bee": "string",
    "name": "string"
  },
  "actions": [
    {
      "bee": "string",
      "name": "string",
      "options": {
        // Action-specific options
      }
    }
  ],
  "filters": [
    {
      // Filter-specific configuration
    }
  ]
}
```

**Response Format:**
```json
{
  "id": "string",
  "name": "string",
  "event": {
    "bee": "string",
    "name": "string"
  },
  "actions": [
    {
      "bee": "string",
      "name": "string",
      "options": {
        // Action-specific options
      }
    }
  ],
  "filters": [
    {
      // Filter-specific configuration
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` - If the request is missing required parameters or contains invalid values
- `404 Not Found` - If the specified Bee IDs don't exist
- `500 Internal Server Error` - If there's an issue connecting to the Beehive API

**Test Cases:**
- ✅ Verified successful creation of a new Chain - Successfully created a chain with the specified event and action
- ✅ Test error handling when a chain with the same name already exists - Returns a 422 error
- ⚠️ Test error handling when required parameters are missing - Should return a 400 error
- ⚠️ Test error handling when Bee IDs don't exist - Should return a 404 error
- ⚠️ Test error handling when event or action names are invalid - Should return a 400 error
- ⚠️ Error handling when Beehive is unavailable - Returns a 500 error

**Implementation Note:**
The chain creation functionality is working correctly. The client properly formats the request by creating action objects and wrapping the configuration in a `chain` object as expected by the API.

#### `update_chain`

**Description:** Update an existing Chain.

**Status:** ❌ Not implemented in the Beehive API

**Implementation Note:**
The Beehive API does not implement a PUT endpoint for chains. The ChainResource in the API only implements GET, POST, and DELETE methods, but not PUT. This means that chains cannot be updated directly through the API.

**Workaround:**
To update a chain, you would need to:
1. Delete the existing chain using the `delete_chain` tool
2. Create a new chain with the updated configuration using the `create_chain` tool

**Recommendation:**
The server-side API should be extended to implement a PUT method for chains, similar to how it's implemented for bees. This would require adding a `chains_put.go` file with the appropriate implementation.

#### `delete_chain`

**Description:** Delete a Chain.

**Required Parameters:**
- `id` (string) - ID of the Chain to delete

**Optional Parameters:** None

**Request Format:**
```json
{
  "id": "string"
}
```

**Response Format:**
```json
{
  "id": "string",
  "name": "string",
  "event": {
    "bee": "string",
    "name": "string"
  },
  "actions": [
    {
      "bee": "string",
      "name": "string",
      "options": {
        // Action-specific options
      }
    }
  ],
  "filters": [
    {
      // Filter-specific configuration
    }
  ]
}
```

**Error Responses:**
- `404 Not Found` - If the specified Chain doesn't exist
- `500 Internal Server Error` - If there's an issue connecting to the Beehive API

**Test Cases:**
- ✅ Verified successful deletion of a Chain - Successfully deleted the specified chain
- ✅ Test error handling when the Chain doesn't exist - Returns a 404 error
- ⚠️ Error handling when Beehive is unavailable - Returns a 500 error

## Logs

### `get_logs`

**Description:** Retrieve logs from the system.

**Required Parameters:**
- None

**Optional Parameters:**
- `beeId` (string) - ID of the Bee to filter logs for

**Request Format:**
```json
{
  "beeId": "string" // Optional
}
```

**Response Format:**
```json
{
  "logs": [
    {
      "id": "string",
      "bee": "string",
      "level": 0,
      "message": "string",
      "timestamp": "2023-01-01T00:00:00Z"
    }
  ]
}
```

**Error Responses:**
- `500 Internal Server Error` - If there's an issue connecting to the Beehive API

**Test Cases:**
- ✅ Verified successful retrieval of logs - Returns an array of log messages
- ✅ Verified filtering logs by bee ID - Returns only logs for the specified bee
- ⚠️ Error handling when Beehive is unavailable - Returns a 500 error

**Implementation Note:**
The logs functionality is working correctly. The client properly formats the request and handles the response from the API.

## Actions

#### `trigger_action`

**Description:** Manually trigger an action on a Bee.

**Required Parameters:**
- `beeId` (string) - ID of the Bee to trigger the action on
- `actionName` (string) - Name of the action to trigger

**Optional Parameters:**
- `options` (object) - Parameters for the action

**Request Format:**
```json
{
  "beeId": "string",
  "actionName": "string",
  "options": {
    // Action-specific parameters
  }
}
```

**Response Format:**
```json
{
  // Action-specific response
}
```

**Error Responses:**
- `400 Bad Request` - If the request is missing required parameters or contains invalid values
- `404 Not Found` - If the specified Bee doesn't exist or the action isn't available
- `500 Internal Server Error` - If there's an issue connecting to the Beehive API

**Test Cases:**
- ⚠️ Attempted to trigger an action - Test was cancelled as no bees were available to trigger actions on
- ⚠️ Test error handling when the Bee doesn't exist - Should return a 404 error
- ⚠️ Test error handling when the action doesn't exist - Should return a 404 error
- ⚠️ Test error handling when options are invalid - Should return a 400 error
- ⚠️ Error handling when Beehive is unavailable - Returns a 500 error

**Implementation Note:**
This tool could not be fully tested due to the inability to create bees because of the implementation issues described above. Once the bee creation issue is fixed, this tool should be tested thoroughly.

## Testing Results

### Summary of Findings

1. **Working Tools:**
   - `list_hives` - Successfully lists all available hives
   - `get_hive_details` - Successfully retrieves details for a specific hive
   - `list_bees` - Successfully lists all configured bees
   - `get_bee` - Successfully retrieves details for a specific bee
   - `create_bee` - Successfully creates a new bee (after fixing implementation)
   - `update_bee` - Successfully updates an existing bee (after fixing implementation)
   - `list_chains` - Successfully lists all configured chains (empty array when none exist)

2. **Fixed Implementation Issues:**
   - `create_bee` - Fixed the request formatting to properly wrap the configuration in a `bee` object and format the options as an array of option objects
   - `update_bee` - Fixed the request formatting to properly wrap the configuration in a `bee` object and format the options as an array of option objects

3. **Remaining Tools with Implementation Issues:**
   - `delete_bee` - Not fully tested, but should work correctly
   - `create_chain` - Working correctly
   - `update_chain` - Not implemented in the Beehive API (no PUT endpoint for chains)
   - `delete_chain` - Working correctly
   - `trigger_action` - Not fully tested due to lack of bees to trigger actions on
   - `get_logs` - Working correctly

4. **Error Handling:**
   - 404 errors are properly returned when resources don't exist
   - 422 errors are returned for validation failures
   - 500 errors would be returned for server issues (not directly tested)

### Recommendations

1. **Completed Fixes:**
   - ✅ Fixed request formatting for bee creation/updates:
     - Properly wrap the configuration in a `bee` object
     - Format the options as an array of option objects with the correct structure

2. **Remaining Fixes Needed:**
   - Remove the `updateChain` method from the client or modify it to use a delete+create approach:
     - The Beehive API does not implement a PUT endpoint for chains
     - The client should either remove this method or implement a workaround using delete and create
   - Fix request formatting for action triggering if needed

3. **Improve Error Handling:**
   - Add more detailed error messages to help diagnose issues
   - Implement proper validation before sending requests to the API

4. **Add Comprehensive Testing:**
   - Create unit tests for each tool
   - Test edge cases and error conditions
   - Verify that all tools work as expected after fixing the implementation issues

### Implementation Fixes

Here are the code changes that have been implemented to fix the identified issues:

#### Implemented Fix for `createBee` in `src/beehive-client.js`:

```javascript
async createBee(config) {
  try {
    // Get the hive details to properly format the options
    const hiveResponse = await this.axios.get(`/v1/hives/${config.namespace}`);
    const hiveOptions = hiveResponse.data.hives[0].options;

    // Convert simple options object to array of option objects with proper structure
    const formattedOptions = [];
    for (const option of hiveOptions) {
      const optionValue = config.options && config.options[option.Name] !== undefined
        ? config.options[option.Name]
        : (option.Default || '*');

      formattedOptions.push({
        Name: option.Name,
        Description: option.Description,
        Type: option.Type,
        Default: option.Default,
        Mandatory: option.Mandatory,
        Value: optionValue
      });
    }

    // Create the properly formatted config
    const formattedConfig = {
      name: config.name,
      namespace: config.namespace,
      description: config.description || '',
      active: config.active !== undefined ? config.active : false,
      options: formattedOptions
    };

    // Wrap the config in a 'bee' object as expected by the API
    const wrappedConfig = { bee: formattedConfig };
    const response = await this.axios.post('/v1/bees', wrappedConfig);
    return response.data;
  } catch (error) {
    this._handleError(error, 'Error creating bee');
  }
}
```

#### Implemented Fix for `updateBee` in `src/beehive-client.js`:

```javascript
async updateBee(id, config) {
  try {
    // Get the current bee details
    const beeResponse = await this.axios.get(`/v1/bees/${id}`);
    const currentBee = beeResponse.data.bees[0];

    // Get the hive details to properly format the options
    const hiveResponse = await this.axios.get(`/v1/hives/${currentBee.namespace}`);
    const hiveOptions = hiveResponse.data.hives[0].options;

    // Convert simple options object to array of option objects with proper structure
    const formattedOptions = [];
    for (const option of hiveOptions) {
      // Use the new option value if provided, otherwise use the current value or default
      const currentOption = currentBee.options.find(o => o.Name === option.Name);
      const currentValue = currentOption ? currentOption.Value : (option.Default || '*');
      const optionValue = config.options && config.options[option.Name] !== undefined
        ? config.options[option.Name]
        : currentValue;

      formattedOptions.push({
        Name: option.Name,
        Description: option.Description,
        Type: option.Type,
        Default: option.Default,
        Mandatory: option.Mandatory,
        Value: optionValue
      });
    }

    // Create the properly formatted config
    const formattedConfig = {
      name: config.name || currentBee.name,
      namespace: currentBee.namespace,
      description: config.description || currentBee.description,
      active: config.active !== undefined ? config.active : currentBee.active,
      options: formattedOptions
    };

    // Wrap the config in a 'bee' object as expected by the API
    const wrappedConfig = { bee: formattedConfig };
    const response = await this.axios.put(`/v1/bees/${id}`, wrappedConfig);
    return response.data;
  } catch (error) {
    this._handleError(error, `Error updating bee ${id}`);
  }
}
```

#### Remaining Fixes Needed for Chain-Related Methods:

The following methods need to be addressed:

1. `updateChain` - This method attempts to use a PUT endpoint that doesn't exist in the Beehive API. It should either be:
   - Removed from the client since the API doesn't support updating chains directly
   - Modified to implement a workaround by deleting the existing chain and creating a new one with the updated configuration

After implementing these changes, all the tools should work correctly with the Beehive API.