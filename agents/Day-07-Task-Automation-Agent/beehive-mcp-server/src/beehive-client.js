const axios = require('axios');

/**
 * Client for interacting with the Beehive API
 */
class BeehiveClient {
  /**
   * Create a BeehiveClient
   * @param {string} baseUrl - Base URL for the Beehive API (e.g., http://localhost:8181)
   * @param {string} [apiKey] - Optional API key for authentication (not used by default in Beehive)
   */
  constructor(baseUrl = 'http://localhost:8181', apiKey = null) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;

    // Create an axios instance with default config
    this.axios = axios.create({
      baseURL: this.baseUrl,
      headers: this.apiKey ? {
        'Authorization': `Bearer ${this.apiKey}`
      } : {}
    });
  }

  /**
   * Get all available Hives (plugins)
   * @returns {Promise<Array>} - List of available Hives
   */
  async getHives() {
    try {
      const response = await this.axios.get('/v1/hives');
      return response.data;
    } catch (error) {
      this._handleError(error, 'Error fetching hives');
    }
  }

  /**
   * Get details of a specific Hive
   * @param {string} name - Name of the Hive
   * @returns {Promise<Object>} - Hive details
   */
  async getHive(name) {
    try {
      const response = await this.axios.get(`/v1/hives/${name}`);
      return response.data;
    } catch (error) {
      this._handleError(error, `Error fetching hive ${name}`);
    }
  }

  /**
   * Get all configured Bees
   * @returns {Promise<Array>} - List of configured Bees
   */
  async getBees() {
    try {
      const response = await this.axios.get('/v1/bees');
      return response.data;
    } catch (error) {
      this._handleError(error, 'Error fetching bees');
    }
  }

  /**
   * Get details of a specific Bee
   * @param {string} id - ID of the Bee
   * @returns {Promise<Object>} - Bee details
   */
  async getBee(id) {
    try {
      const response = await this.axios.get(`/v1/bees/${id}`);
      return response.data;
    } catch (error) {
      this._handleError(error, `Error fetching bee ${id}`);
    }
  }

  /**
   * Create a new Bee
   * @param {Object} config - Bee configuration
   * @param {string} config.name - Name for the Bee
   * @param {string} config.namespace - Hive namespace (the type of Hive to use)
   * @param {Object} config.options - Configuration options for the Bee
   * @returns {Promise<Object>} - Created Bee
   */
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

  /**
   * Update an existing Bee
   * @param {string} id - ID of the Bee to update
   * @param {Object} config - Updated configuration
   * @returns {Promise<Object>} - Updated Bee
   */
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

  /**
   * Delete a Bee
   * @param {string} id - ID of the Bee to delete
   * @returns {Promise<Object>} - Deleted Bee
   */
  async deleteBee(id) {
    try {
      const response = await this.axios.delete(`/v1/bees/${id}`);
      return response.data;
    } catch (error) {
      this._handleError(error, `Error deleting bee ${id}`);
    }
  }

  /**
   * Get all configured Chains
   * @returns {Promise<Array>} - List of configured Chains
   */
  async getChains() {
    try {
      const response = await this.axios.get('/v1/chains');
      return response.data;
    } catch (error) {
      this._handleError(error, 'Error fetching chains');
    }
  }

  /**
   * Get details of a specific Chain
   * @param {string} id - ID of the Chain
   * @returns {Promise<Object>} - Chain details
   */
  async getChain(id) {
    try {
      const response = await this.axios.get(`/v1/chains/${id}`);
      return response.data;
    } catch (error) {
      this._handleError(error, `Error fetching chain ${id}`);
    }
  }

  /**
   * Create a new Chain
   * @param {Object} config - Chain configuration
   * @param {string} config.name - Name for the Chain
   * @param {Object} config.event - Event that triggers the chain
   * @param {Array} config.actions - Actions to perform
   * @param {Array} [config.filters=[]] - Filters to apply
   * @returns {Promise<Object>} - Created Chain
   */
  async createChain(config) {
    try {
      // Format the event object properly
      const formattedEvent = {
        Bee: config.event.bee,
        Name: config.event.name,
        Options: config.event.options || null // The API expects null if no options are provided
      };

      // Get the action IDs
      const actionIds = [];
      if (config.actions && config.actions.length > 0) {
        // For each action in the config, create an action in the API and get its ID
        for (const action of config.actions) {
          // Convert options to Placeholder array if needed
          let formattedOptions = [];
          if (action.options) {
            if (Array.isArray(action.options)) {
              // If options is already an array of Placeholder objects, use it as is
              formattedOptions = action.options;
            } else if (typeof action.options === 'object') {
              // If options is an object, convert it to an array of Placeholder objects
              formattedOptions = Object.entries(action.options).map(([name, value]) => ({
                Name: name,
                Type: typeof value === 'string' ? 'string' : typeof value,
                Value: value
              }));
            }
          }

          // Create the action
          const actionResponse = await this.axios.post('/v1/actions', {
            action: {
              bee: action.bee,
              name: action.name,
              options: formattedOptions
            }
          });

          if (actionResponse.data && actionResponse.data.actions && actionResponse.data.actions.length > 0) {
            actionIds.push(actionResponse.data.actions[0].id);
          }
        }
      }

      // Format the chain config
      const formattedConfig = {
        name: config.name,
        description: config.description || '',
        event: formattedEvent,
        filters: config.filters || [],
        actions: actionIds
      };

      // Wrap the config in a 'chain' object as expected by the API
      const wrappedConfig = { chain: formattedConfig };
      const response = await this.axios.post('/v1/chains', wrappedConfig);
      return response.data;
    } catch (error) {
      this._handleError(error, 'Error creating chain');
    }
  }

  /**
   * Update an existing Chain
   * @param {string} id - ID of the Chain to update
   * @param {Object} config - Updated configuration
   * @returns {Promise<Object>} - Updated Chain
   */
  async updateChain(id, config) {
    try {
      // Get the current chain details
      const chainResponse = await this.axios.get(`/v1/chains/${id}`);
      const currentChain = chainResponse.data.chains[0];

      // Format the event object properly if provided
      let formattedEvent = currentChain.event;
      if (config.event) {
        formattedEvent = {
          Bee: config.event.bee || currentChain.event.Bee,
          Name: config.event.name || currentChain.event.Name,
          Options: config.event.options || currentChain.event.Options || null // Use new options if provided
        };
      }

      // Handle actions if provided
      let actionIds = currentChain.actions;
      if (config.actions && config.actions.length > 0) {
        actionIds = [];
        // For each action in the config, create an action in the API and get its ID
        for (const action of config.actions) {
          // Convert options to Placeholder array if needed
          let formattedOptions = [];
          if (action.options) {
            if (Array.isArray(action.options)) {
              // If options is already an array of Placeholder objects, use it as is
              formattedOptions = action.options;
            } else if (typeof action.options === 'object') {
              // If options is an object, convert it to an array of Placeholder objects
              formattedOptions = Object.entries(action.options).map(([name, value]) => ({
                Name: name,
                Type: typeof value === 'string' ? 'string' : typeof value,
                Value: value
              }));
            }
          }

          // Create the action
          const actionResponse = await this.axios.post('/v1/actions', {
            action: {
              bee: action.bee,
              name: action.name,
              options: formattedOptions
            }
          });

          if (actionResponse.data && actionResponse.data.actions && actionResponse.data.actions.length > 0) {
            actionIds.push(actionResponse.data.actions[0].id);
          }
        }
      }

      // Format the chain config
      const formattedConfig = {
        name: config.name || currentChain.name,
        description: config.description || currentChain.description,
        event: formattedEvent,
        filters: config.filters || currentChain.filters,
        actions: actionIds
      };

      // Wrap the config in a 'chain' object as expected by the API
      const wrappedConfig = { chain: formattedConfig };
      const response = await this.axios.put(`/v1/chains/${id}`, wrappedConfig);
      return response.data;
    } catch (error) {
      this._handleError(error, `Error updating chain ${id}`);
    }
  }

  /**
   * Delete a Chain
   * @param {string} id - ID of the Chain to delete
   * @returns {Promise<Object>} - Deleted Chain
   */
  async deleteChain(id) {
    try {
      const response = await this.axios.delete(`/v1/chains/${id}`);
      return response.data;
    } catch (error) {
      this._handleError(error, `Error deleting chain ${id}`);
    }
  }

  /**
   * Trigger an action on a Bee
   * @param {string} beeId - ID of the Bee
   * @param {string} actionName - Name of the action
   * @param {Object} options - Action parameters
   * @returns {Promise<Object>} - Action result
   */
  /**
   * Get logs from the system
   * @param {string} [beeId] - Optional ID of the Bee to filter logs for
   * @returns {Promise<Object>} - Logs
   */
  async getLogs(beeId = '') {
    try {
      const url = '/v1/logs' + (beeId ? `?bee=${beeId}` : '');
      const response = await this.axios.get(url);
      return response.data;
    } catch (error) {
      this._handleError(error, 'Error fetching logs');
    }
  }

  /**
   * Trigger an action on a Bee
   * @param {string} beeId - ID of the Bee
   * @param {string} actionName - Name of the action
   * @param {Object} options - Action parameters
   * @returns {Promise<Object>} - Action result
   */
  async triggerAction(beeId, actionName, options = {}) {
    try {
      const response = await this.axios.post(`/v1/bees/${beeId}/actions/${actionName}`, options);
      return response.data;
    } catch (error) {
      this._handleError(error, `Error triggering action ${actionName} on bee ${beeId}`);
    }
  }

  /**
   * Handle errors from API calls
   * @private
   * @param {Error} error - Error object
   * @param {string} message - Custom error message
   * @throws {Error} - Throws an error with details
   */
  _handleError(error, message) {
    // If it's an Axios error with a response, extract the data
    if (error.response) {
      const { status, data } = error.response;
      throw new Error(`${message}: ${status} - ${JSON.stringify(data)}`);
    } else if (error.request) {
      // The request was made but no response was received
      throw new Error(`${message}: No response received - ${error.message}`);
    } else {
      // Something happened in setting up the request
      throw new Error(`${message}: ${error.message}`);
    }
  }
}

module.exports = BeehiveClient;
