#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";

// Define interfaces for FreshRSS Google Reader API responses
interface GReaderItem {
  id: string;
  origin: {
    streamId: string;
    title: string;
    htmlUrl: string;
  };
  title: string;
  author?: string;
  summary: {
    content: string;
    direction?: string;
  };
  content?: {
    content: string;
    direction?: string;
  };
  alternate?: {
    href: string;
    type: string;
  }[];
  categories: string[];
  published: number;
  updated: number;
  crawlTimeMsec: string;
  timestampUsec: string;
}

interface GReaderStreamContents {
  direction?: string;
  id: string;
  title: string;
  description?: string;
  updated: number;
  items: GReaderItem[];
  continuation?: string;
}

interface GReaderSubscription {
  id: string;
  title: string;
  categories: {
    id: string;
    label: string;
  }[];
  url: string;
  htmlUrl: string;
  iconUrl?: string;
}

interface GReaderSubscriptionList {
  subscriptions: GReaderSubscription[];
}

interface GReaderTagList {
  tags: {
    id: string;
    type: string;
  }[];
}

// Interface for unread counts response
// Currently not used directly but kept for reference
// and potential future implementation
/*
interface GReaderUnreadCount {
  max: number;
  unreadcounts: {
    id: string;
    count: number;
    newestItemTimestampUsec: string;
  }[];
}
*/

// FreshRSS Google Reader API client class
class FreshRSSGReaderClient {
  private apiUrl: string;
  private username: string;
  private password: string;
  private authToken: string | null = null;

  constructor(apiUrl: string, username: string, password: string) {
    this.apiUrl = apiUrl.replace(/\/$/, ''); // Remove trailing slash
    this.username = username;
    this.password = password;
  }

  // Initialize authentication
  private async authenticate(): Promise<string> {
    if (this.authToken) {
      return this.authToken;
    }

    try {
      // Google Reader API authentication
      const requestData = new URLSearchParams({
        Email: this.username,
        Passwd: this.password
      });

      const response = await axios({
        method: 'POST',
        url: `${this.apiUrl}/api/greader.php/accounts/ClientLogin`,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        data: requestData,
      });

      // Parse the response which is in format "Auth=token"
      const responseText = response.data;
      const authMatch = responseText.match(/Auth=(.+)/);

      if (!authMatch) {
        throw new Error('Invalid authentication response');
      }

      this.authToken = authMatch[1];
      // Non-null assertion since we just checked it's not null
      return this.authToken!;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new McpError(
          ErrorCode.InternalError,
          `FreshRSS authentication error: ${error.response?.data || error.message}`
        );
      }
      throw error;
    }
  }

  private async request<T>(endpoint: string, method: string = 'GET', params: Record<string, any> = {}): Promise<T> {
    try {
      const authToken = await this.authenticate();

      const url = `${this.apiUrl}/api/greader.php${endpoint}`;

      // Add output format to params
      params.output = 'json';

      const config: any = {
        method,
        url,
        headers: {
          'Authorization': `GoogleLogin auth=${authToken}`
        }
      };

      // Handle GET vs POST requests
      if (method === 'GET') {
        config.params = params;
      } else {
        config.headers['Content-Type'] = 'application/x-www-form-urlencoded';
        config.data = new URLSearchParams(params);
      }

      const response = await axios(config);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new McpError(
          ErrorCode.InternalError,
          `FreshRSS API error: ${error.response?.data?.error || error.message}`
        );
      }
      throw error;
    }
  }

  // Get a token for write operations
  private async getToken(): Promise<string> {
    const response = await this.request<string>('/reader/api/0/token', 'GET');
    return response;
  }

  // Get feed subscriptions
  async getSubscriptions() {
    return this.request<GReaderSubscriptionList>('/reader/api/0/subscription/list');
  }

  // Get feed groups/tags
  async getFeedGroups() {
    return this.request<GReaderTagList>('/reader/api/0/tag/list');
  }

  // Get unread items
  async getUnreadItems() {
    // Get unread items using the reading-list with unread filter
    return this.request<GReaderStreamContents>(
      '/reader/api/0/stream/contents/user/-/state/com.google/reading-list',
      'GET',
      {
        xt: 'user/-/state/com.google/read', // Exclude read items
        n: 50 // Limit to 50 items
      }
    );
  }

  // Get feed items
  async getFeedItems(feedId: string) {
    // In Google Reader API, feed IDs are prefixed with "feed/"
    const formattedFeedId = feedId.startsWith('feed/') ? feedId : `feed/${feedId}`;

    return this.request<GReaderStreamContents>(
      `/reader/api/0/stream/contents/${encodeURIComponent(formattedFeedId)}`,
      'GET',
      {
        n: 50 // Limit to 50 items
      }
    );
  }

  // Mark item as read
  async markAsRead(itemId: string) {
    const token = await this.getToken();

    return this.request(
      '/reader/api/0/edit-tag',
      'POST',
      {
        i: itemId,
        a: 'user/-/state/com.google/read',
        T: token
      }
    );
  }

  // Mark item as unread
  async markAsUnread(itemId: string) {
    const token = await this.getToken();

    return this.request(
      '/reader/api/0/edit-tag',
      'POST',
      {
        i: itemId,
        r: 'user/-/state/com.google/read',
        T: token
      }
    );
  }

  // Mark all items in a feed as read
  async markFeedAsRead(feedId: string) {
    const token = await this.getToken();
    const formattedFeedId = feedId.startsWith('feed/') ? feedId : `feed/${feedId}`;

    return this.request(
      '/reader/api/0/mark-all-as-read',
      'POST',
      {
        s: formattedFeedId,
        ts: Math.floor(Date.now() / 1000),
        T: token
      }
    );
  }

  // Get specific items by IDs
  async getItems(itemIds: string[]) {
    // Google Reader API doesn't have a direct endpoint for getting items by IDs
    // We'll use the stream/items/contents endpoint with a filter
    const token = await this.getToken();

    return this.request<GReaderStreamContents>(
      '/reader/api/0/stream/items/contents',
      'POST',
      {
        i: itemIds,
        T: token
      }
    );
  }
}

// Initialize server
const apiUrl = process.env.FRESHRSS_API_URL;
const username = process.env.FRESHRSS_USERNAME;
const password = process.env.FRESHRSS_PASSWORD;

if (!apiUrl || !username || !password) {
  throw new Error('FRESHRSS_API_URL, FRESHRSS_USERNAME, and FRESHRSS_PASSWORD environment variables are required');
}

const client = new FreshRSSGReaderClient(apiUrl, username, password);

const server = new Server(
  {
    name: "freshrss-server",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "list_feeds",
      description: "List all feed subscriptions",
      inputSchema: {
        type: "object",
        properties: {},
      },
    },
    {
      name: "get_feed_groups",
      description: "Get feed groups",
      inputSchema: {
        type: "object",
        properties: {},
      },
    },
    {
      name: "get_unread",
      description: "Get unread items",
      inputSchema: {
        type: "object",
        properties: {},
      },
    },
    {
      name: "get_feed_items",
      description: "Get items from a specific feed",
      inputSchema: {
        type: "object",
        properties: {
          feed_id: {
            type: "string",
            description: "Feed ID",
          },
        },
        required: ["feed_id"],
      },
    },
    {
      name: "mark_item_read",
      description: "Mark an item as read",
      inputSchema: {
        type: "object",
        properties: {
          item_id: {
            type: "string",
            description: "Item ID to mark as read",
          },
        },
        required: ["item_id"],
      },
    },
    {
      name: "mark_item_unread",
      description: "Mark an item as unread",
      inputSchema: {
        type: "object",
        properties: {
          item_id: {
            type: "string",
            description: "Item ID to mark as unread",
          },
        },
        required: ["item_id"],
      },
    },
    {
      name: "mark_feed_read",
      description: "Mark all items in a feed as read",
      inputSchema: {
        type: "object",
        properties: {
          feed_id: {
            type: "string",
            description: "Feed ID to mark as read",
          },
        },
        required: ["feed_id"],
      },
    },
    {
      name: "get_items",
      description: "Get specific items by their IDs",
      inputSchema: {
        type: "object",
        properties: {
          item_ids: {
            type: "array",
            items: {
              type: "string",
            },
            description: "Array of item IDs to get",
          },
        },
        required: ["item_ids"],
      },
    },
  ],
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    switch (request.params.name) {
      case "list_feeds": {
        const response = await client.getSubscriptions();
        return {
          content: [{
            type: "text",
            text: JSON.stringify(response, null, 2),
          }],
        };
      }

      case "get_feed_groups": {
        const response = await client.getFeedGroups();
        return {
          content: [{
            type: "text",
            text: JSON.stringify(response, null, 2),
          }],
        };
      }

      case "get_unread": {
        const response = await client.getUnreadItems();
        return {
          content: [{
            type: "text",
            text: JSON.stringify(response, null, 2),
          }],
        };
      }

      case "get_feed_items": {
        const { feed_id } = request.params.arguments as { feed_id: string };
        const response = await client.getFeedItems(feed_id);

        // No need to filter items as the Google Reader API already returns items for the specific feed
        return {
          content: [{
            type: "text",
            text: JSON.stringify(response, null, 2),
          }],
        };
      }

      case "mark_item_read": {
        const { item_id } = request.params.arguments as { item_id: string };
        await client.markAsRead(item_id);
        return {
          content: [{
            type: "text",
            text: `Successfully marked item ${item_id} as read`,
          }],
        };
      }

      case "mark_item_unread": {
        const { item_id } = request.params.arguments as { item_id: string };
        await client.markAsUnread(item_id);
        return {
          content: [{
            type: "text",
            text: `Successfully marked item ${item_id} as unread`,
          }],
        };
      }

      case "mark_feed_read": {
        const { feed_id } = request.params.arguments as { feed_id: string };
        await client.markFeedAsRead(feed_id);
        return {
          content: [{
            type: "text",
            text: `Successfully marked all items in feed ${feed_id} as read`,
          }],
        };
      }

      case "get_items": {
        const { item_ids } = request.params.arguments as { item_ids: string[] };
        const items = await client.getItems(item_ids);
        return {
          content: [{
            type: "text",
            text: JSON.stringify(items, null, 2),
          }],
        };
      }

      default:
        throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${request.params.name}`);
    }
  } catch (error) {
    if (error instanceof McpError) {
      throw error;
    }
    throw new McpError(ErrorCode.InternalError, String(error));
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('FreshRSS MCP server running on stdio');
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
