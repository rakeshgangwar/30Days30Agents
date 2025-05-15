require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const BeehiveClient = require('./beehive-client');

// Initialize the Beehive client with the API key (if provided)
// Note: Beehive doesn't use API keys by default - this is for custom auth implementations
const beehiveClient = new BeehiveClient(
  process.env.BEEHIVE_URL,
  process.env.BEEHIVE_API_KEY
);

// Create Express server
const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Server metadata for MCP
const serverMetadata = {
  name: process.env.MCP_SERVER_NAME || 'beehive',
  description: 'Beehive automation and event system MCP server',
  version: '0.1.0',
  vendor: {
    name: 'Beehive MCP',
    url: 'https://github.com/muesli/beehive'
  }
};

// MCP Tool Schemas

// List Hives tool schema
const listHivesSchema = {
  type: 'object',
  properties: {},
  description: 'List all available Hives (plugins)'
};

// Get Hive Details tool schema
const getHiveDetailsSchema = {
  type: 'object',
  properties: {
    name: {
      type: 'string',
      description: 'Name of the Hive (plugin)'
    }
  },
  required: ['name'],
  description: 'Get detailed information about a specific Hive'
};

// List Bees tool schema
const listBeesSchema = {
  type: 'object',
  properties: {},
  description: 'List all configured Bees (instances of Hives)'
};

// Get Bee tool schema
const getBeeSchema = {
  type: 'object',
  properties: {
    id: {
      type: 'string',
      description: 'ID of the Bee'
    }
  },
  required: ['id'],
  description: 'Get details of a specific Bee'
};

// Create Bee tool schema
const createBeeSchema = {
  type: 'object',
  properties: {
    name: {
      type: 'string',
      description: 'Name for the new Bee'
    },
    hive: {
      type: 'string',
      description: 'Name of the Hive (plugin) to use'
    },
    options: {
      type: 'object',
      description: 'Configuration options for the Bee'
    }
  },
  required: ['name', 'hive'],
  description: 'Create a new Bee instance'
};

// Update Bee tool schema
const updateBeeSchema = {
  type: 'object',
  properties: {
    id: {
      type: 'string',
      description: 'ID of the Bee to update'
    },
    name: {
      type: 'string',
      description: 'New name for the Bee'
    },
    options: {
      type: 'object',
      description: 'Updated configuration options for the Bee'
    }
  },
  required: ['id'],
  description: 'Update an existing Bee'
};

// Delete Bee tool schema
const deleteBeeSchema = {
  type: 'object',
  properties: {
    id: {
      type: 'string',
      description: 'ID of the Bee to delete'
    }
  },
  required: ['id'],
  description: 'Delete a Bee instance'
};

// List Chains tool schema
const listChainsSchema = {
  type: 'object',
  properties: {},
  description: 'List all configured Chains'
};

// Get Chain tool schema
const getChainSchema = {
  type: 'object',
  properties: {
    id: {
      type: 'string',
      description: 'ID of the Chain'
    }
  },
  required: ['id'],
  description: 'Get details of a specific Chain'
};

// Create Chain tool schema
const createChainSchema = {
  type: 'object',
  properties: {
    name: {
      type: 'string',
      description: 'Name for the new Chain'
    },
    event: {
      type: 'object',
      properties: {
        bee: {
          type: 'string',
          description: 'ID of the Bee that generates the event'
        },
        name: {
          type: 'string',
          description: 'Name of the event'
        }
      },
      required: ['bee', 'name'],
      description: 'Event that triggers the chain'
    },
    actions: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          bee: {
            type: 'string',
            description: 'ID of the Bee that performs the action'
          },
          name: {
            type: 'string',
            description: 'Name of the action'
          },
          options: {
            type: 'object',
            description: 'Options/parameters for the action'
          }
        },
        required: ['bee', 'name']
      },
      description: 'Actions to perform when the event is triggered'
    },
    filters: {
      type: 'array',
      items: {
        type: 'object',
        description: 'Filters to apply to the event'
      },
      description: 'Filters to determine if the action should be executed'
    }
  },
  required: ['name', 'event', 'actions'],
  description: 'Create a new Chain connecting events to actions'
};

// Update Chain tool schema
const updateChainSchema = {
  type: 'object',
  properties: {
    id: {
      type: 'string',
      description: 'ID of the Chain to update'
    },
    name: {
      type: 'string',
      description: 'Updated name for the Chain'
    },
    event: {
      type: 'object',
      properties: {
        bee: {
          type: 'string',
          description: 'ID of the Bee that generates the event'
        },
        name: {
          type: 'string',
          description: 'Name of the event'
        }
      },
      description: 'Updated event that triggers the chain'
    },
    actions: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          bee: {
            type: 'string',
            description: 'ID of the Bee that performs the action'
          },
          name: {
            type: 'string',
            description: 'Name of the action'
          },
          options: {
            type: 'object',
            description: 'Options/parameters for the action'
          }
        },
        required: ['bee', 'name']
      },
      description: 'Updated actions to perform when the event is triggered'
    },
    filters: {
      type: 'array',
      items: {
        type: 'object',
        description: 'Filters to apply to the event'
      },
      description: 'Updated filters to determine if the action should be executed'
    }
  },
  required: ['id'],
  description: 'Update an existing Chain'
};

// Delete Chain tool schema
const deleteChainSchema = {
  type: 'object',
  properties: {
    id: {
      type: 'string',
      description: 'ID of the Chain to delete'
    }
  },
  required: ['id'],
  description: 'Delete a Chain'
};

// Trigger Action tool schema
const triggerActionSchema = {
  type: 'object',
  properties: {
    beeId: {
      type: 'string',
      description: 'ID of the Bee to trigger the action on'
    },
    actionName: {
      type: 'string',
      description: 'Name of the action to trigger'
    },
    options: {
      type: 'object',
      description: 'Parameters for the action'
    }
  },
  required: ['beeId', 'actionName'],
  description: 'Manually trigger an action on a Bee'
};

// List all available tools
const tools = [
  {
    name: 'list_hives',
    description: 'List all available Hives (plugins)',
    inputSchema: listHivesSchema,
    handler: async () => {
      return await beehiveClient.getHives();
    }
  },
  {
    name: 'get_hive_details',
    description: 'Get detailed information about a specific Hive',
    inputSchema: getHiveDetailsSchema,
    handler: async ({ name }) => {
      return await beehiveClient.getHive(name);
    }
  },
  {
    name: 'list_bees',
    description: 'List all configured Bees (instances of Hives)',
    inputSchema: listBeesSchema,
    handler: async () => {
      return await beehiveClient.getBees();
    }
  },
  {
    name: 'get_bee',
    description: 'Get details of a specific Bee',
    inputSchema: getBeeSchema,
    handler: async ({ id }) => {
      return await beehiveClient.getBee(id);
    }
  },
  {
    name: 'create_bee',
    description: 'Create a new Bee instance',
    inputSchema: createBeeSchema,
    handler: async ({ name, hive, description = '', options = {} }) => {
      const beeConfig = {
        name,
        namespace: hive, // The API expects 'namespace' instead of 'hive'
        description,
        active: true,
        options
      };
      return await beehiveClient.createBee(beeConfig);
    }
  },
  {
    name: 'update_bee',
    description: 'Update an existing Bee',
    inputSchema: updateBeeSchema,
    handler: async ({ id, name, options }) => {
      const beeConfig = {};
      if (name) beeConfig.name = name;
      if (options) beeConfig.options = options;
      return await beehiveClient.updateBee(id, beeConfig);
    }
  },
  {
    name: 'delete_bee',
    description: 'Delete a Bee instance',
    inputSchema: deleteBeeSchema,
    handler: async ({ id }) => {
      return await beehiveClient.deleteBee(id);
    }
  },
  {
    name: 'list_chains',
    description: 'List all configured Chains',
    inputSchema: listChainsSchema,
    handler: async () => {
      return await beehiveClient.getChains();
    }
  },
  {
    name: 'get_chain',
    description: 'Get details of a specific Chain',
    inputSchema: getChainSchema,
    handler: async ({ id }) => {
      return await beehiveClient.getChain(id);
    }
  },
  {
    name: 'create_chain',
    description: 'Create a new Chain connecting events to actions',
    inputSchema: createChainSchema,
    handler: async ({ name, event, actions, filters = [] }) => {
      const chainConfig = {
        name,
        event,
        actions,
        filters
      };
      return await beehiveClient.createChain(chainConfig);
    }
  },
  {
    name: 'update_chain',
    description: 'Update an existing Chain',
    inputSchema: updateChainSchema,
    handler: async ({ id, name, event, actions, filters }) => {
      const chainConfig = {};
      if (name) chainConfig.name = name;
      if (event) chainConfig.event = event;
      if (actions) chainConfig.actions = actions;
      if (filters) chainConfig.filters = filters;
      return await beehiveClient.updateChain(id, chainConfig);
    }
  },
  {
    name: 'delete_chain',
    description: 'Delete a Chain',
    inputSchema: deleteChainSchema,
    handler: async ({ id }) => {
      return await beehiveClient.deleteChain(id);
    }
  },
  {
    name: 'trigger_action',
    description: 'Manually trigger an action on a Bee',
    inputSchema: triggerActionSchema,
    handler: async ({ beeId, actionName, options = {} }) => {
      return await beehiveClient.triggerAction(beeId, actionName, options);
    }
  }
];

// Map of tools by name for easy lookup
const toolsByName = tools.reduce((acc, tool) => {
  acc[tool.name] = tool;
  return acc;
}, {});

// MCP endpoint to handle tool use
app.post('/tools/:tool_name', async (req, res) => {
  const toolName = req.params.tool_name;
  const tool = toolsByName[toolName];

  if (!tool) {
    return res.status(404).json({
      error: `Tool "${toolName}" not found`
    });
  }

  try {
    const result = await tool.handler(req.body);
    res.json(result);
  } catch (error) {
    console.error(`Error executing tool ${toolName}:`, error);
    res.status(500).json({
      error: `Error executing tool: ${error.message}`
    });
  }
});

// MCP endpoint to list available tools
app.get('/tools', (req, res) => {
  const toolList = tools.map(tool => ({
    name: tool.name,
    description: tool.description,
    inputSchema: tool.inputSchema
  }));

  res.json(toolList);
});

// MCP endpoint for server metadata
app.get('/metadata', (req, res) => {
  res.json(serverMetadata);
});

// Start the server
app.listen(port, () => {
  console.log(`Beehive MCP server running on port ${port}`);
  console.log(`Server name: ${serverMetadata.name}`);
  console.log(`Connected to Beehive at: ${process.env.BEEHIVE_URL || 'http://localhost:8181'}`);
});