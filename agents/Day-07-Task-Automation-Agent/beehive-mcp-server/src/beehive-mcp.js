require('dotenv').config();
const { McpServer } = require('@modelcontextprotocol/sdk/server/mcp.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const { z } = require('zod');
const BeehiveClient = require('./beehive-client');

// Initialize the Beehive client
const beehiveClient = new BeehiveClient(
  process.env.BEEHIVE_URL,
  process.env.BEEHIVE_API_KEY
);

// Create an MCP server with metadata
const server = new McpServer({
  name: process.env.MCP_SERVER_NAME || 'beehive',
  description: 'Beehive automation and event system MCP server',
  version: '0.1.0',
  vendor: {
    name: 'Beehive MCP',
    url: 'https://github.com/muesli/beehive'
  }
});

// Add tools for Hives management
server.tool(
  'list_hives',
  {},
  async () => {
    try {
      const hives = await beehiveClient.getHives();
      return {
        content: [{ type: 'text', text: JSON.stringify(hives, null, 2) }]
      };
    } catch (error) {
      console.error('Error listing hives:', error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.tool(
  'get_hive_details',
  { name: z.string().describe('Name of the Hive (plugin)') },
  async ({ name }) => {
    try {
      const hive = await beehiveClient.getHive(name);
      return {
        content: [{ type: 'text', text: JSON.stringify(hive, null, 2) }]
      };
    } catch (error) {
      console.error(`Error fetching hive ${name}:`, error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

// Add tools for Bees management
server.tool(
  'list_bees',
  {},
  async () => {
    try {
      const bees = await beehiveClient.getBees();
      return {
        content: [{ type: 'text', text: JSON.stringify(bees, null, 2) }]
      };
    } catch (error) {
      console.error('Error listing bees:', error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.tool(
  'get_bee',
  { id: z.string().describe('ID of the Bee') },
  async ({ id }) => {
    try {
      const bee = await beehiveClient.getBee(id);
      return {
        content: [{ type: 'text', text: JSON.stringify(bee, null, 2) }]
      };
    } catch (error) {
      console.error(`Error fetching bee ${id}:`, error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.tool(
  'create_bee',
  {
    name: z.string().describe('Name for the new Bee'),
    hive: z.string().describe('Name of the Hive (plugin) to use'),
    options: z.object({}).passthrough().optional().describe('Configuration options for the Bee')
  },
  async ({ name, hive, options = {} }) => {
    try {
      const beeConfig = {
        name,
        namespace: hive, // The API expects 'namespace' instead of 'hive'
        description: '',
        active: true,
        options
      };
      const result = await beehiveClient.createBee(beeConfig);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    } catch (error) {
      console.error('Error creating bee:', error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.tool(
  'update_bee',
  {
    id: z.string().describe('ID of the Bee to update'),
    name: z.string().optional().describe('New name for the Bee'),
    options: z.object({}).passthrough().optional().describe('Updated configuration options for the Bee')
  },
  async ({ id, name, options }) => {
    try {
      const beeConfig = {};
      if (name) beeConfig.name = name;
      if (options) beeConfig.options = options;

      const result = await beehiveClient.updateBee(id, beeConfig);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    } catch (error) {
      console.error(`Error updating bee ${id}:`, error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.tool(
  'delete_bee',
  { id: z.string().describe('ID of the Bee to delete') },
  async ({ id }) => {
    try {
      const result = await beehiveClient.deleteBee(id);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    } catch (error) {
      console.error(`Error deleting bee ${id}:`, error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

// Add tools for Chains management
server.tool(
  'list_chains',
  {},
  async () => {
    try {
      const chains = await beehiveClient.getChains();
      return {
        content: [{ type: 'text', text: JSON.stringify(chains, null, 2) }]
      };
    } catch (error) {
      console.error('Error listing chains:', error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.tool(
  'get_chain',
  { id: z.string().describe('ID of the Chain') },
  async ({ id }) => {
    try {
      const chain = await beehiveClient.getChain(id);
      return {
        content: [{ type: 'text', text: JSON.stringify(chain, null, 2) }]
      };
    } catch (error) {
      console.error(`Error fetching chain ${id}:`, error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.tool(
  'create_chain',
  {
    name: z.string().describe('Name for the new Chain'),
    event: z.object({
      bee: z.string().describe('ID of the Bee that generates the event'),
      name: z.string().describe('Name of the event')
    }).describe('Event that triggers the chain'),
    actions: z.array(
      z.object({
        bee: z.string().describe('ID of the Bee that performs the action'),
        name: z.string().describe('Name of the action'),
        options: z.object({}).passthrough().optional().describe('Options/parameters for the action')
      })
    ).describe('Actions to perform when the event is triggered'),
    filters: z.array(
      z.object({}).passthrough()
    ).optional().describe('Filters to determine if the action should be executed')
  },
  async ({ name, event, actions, filters = [] }) => {
    try {
      const chainConfig = {
        name,
        event,
        actions,
        filters
      };
      const result = await beehiveClient.createChain(chainConfig);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    } catch (error) {
      console.error('Error creating chain:', error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.tool(
  'update_chain',
  {
    id: z.string().describe('ID of the Chain to update'),
    name: z.string().optional().describe('Updated name for the Chain'),
    event: z.object({
      bee: z.string().describe('ID of the Bee that generates the event'),
      name: z.string().describe('Name of the event')
    }).optional().describe('Updated event that triggers the chain'),
    actions: z.array(
      z.object({
        bee: z.string().describe('ID of the Bee that performs the action'),
        name: z.string().describe('Name of the action'),
        options: z.object({}).passthrough().optional().describe('Options/parameters for the action')
      })
    ).optional().describe('Updated actions to perform when the event is triggered'),
    filters: z.array(
      z.object({}).passthrough()
    ).optional().describe('Updated filters to determine if the action should be executed')
  },
  async ({ id, name, event, actions, filters }) => {
    try {
      const chainConfig = {};
      if (name) chainConfig.name = name;
      if (event) chainConfig.event = event;
      if (actions) chainConfig.actions = actions;
      if (filters) chainConfig.filters = filters;

      const result = await beehiveClient.updateChain(id, chainConfig);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    } catch (error) {
      console.error(`Error updating chain ${id}:`, error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

server.tool(
  'delete_chain',
  { id: z.string().describe('ID of the Chain to delete') },
  async ({ id }) => {
    try {
      const result = await beehiveClient.deleteChain(id);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    } catch (error) {
      console.error(`Error deleting chain ${id}:`, error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

// Add tool for triggering actions
server.tool(
  'trigger_action',
  {
    beeId: z.string().describe('ID of the Bee to trigger the action on'),
    actionName: z.string().describe('Name of the action to trigger'),
    options: z.object({}).passthrough().optional().describe('Parameters for the action')
  },
  async ({ beeId, actionName, options = {} }) => {
    try {
      const result = await beehiveClient.triggerAction(beeId, actionName, options);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    } catch (error) {
      console.error(`Error triggering action ${actionName} on bee ${beeId}:`, error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

// Add tool for retrieving logs
server.tool(
  'get_logs',
  {
    beeId: z.string().optional().describe('Optional ID of the Bee to filter logs for')
  },
  async ({ beeId }) => {
    try {
      const logs = await beehiveClient.getLogs(beeId);
      return {
        content: [{ type: 'text', text: JSON.stringify(logs, null, 2) }]
      };
    } catch (error) {
      console.error('Error fetching logs:', error.message);
      return {
        content: [{ type: 'text', text: `Error: ${error.message}` }],
        isError: true
      };
    }
  }
);

// Start the server with stdio transport
async function startServer() {
  try {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.log('Beehive MCP server started with stdio transport');
  } catch (error) {
    console.error('Error starting server:', error);
    process.exit(1);
  }
}

// Start the server
startServer();

module.exports = server;
