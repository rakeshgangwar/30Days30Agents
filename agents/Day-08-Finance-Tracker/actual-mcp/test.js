// Simple test script for the Actual Finance MCP server
const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio.js');
const { spawn } = require('child_process');
const path = require('path');

async function runTest() {
  console.log('Starting Actual Finance MCP server test...');
  
  // Start the server as a child process
  const serverProcess = spawn('node', ['server.js'], {
    cwd: __dirname,
    stdio: ['pipe', 'pipe', 'pipe']
  });
  
  // Log server output
  serverProcess.stdout.on('data', (data) => {
    console.log(`Server stdout: ${data}`);
  });
  
  serverProcess.stderr.on('data', (data) => {
    console.error(`Server stderr: ${data}`);
  });
  
  // Give the server a moment to start
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  try {
    // Create an MCP client
    const transport = new StdioClientTransport({
      command: 'node',
      args: [path.join(__dirname, 'server.js')]
    });
    
    const client = new Client({
      name: 'test-client',
      version: '1.0.0'
    });
    
    console.log('Connecting to MCP server...');
    await client.connect(transport);
    console.log('Connected to MCP server');
    
    // Test listing resources
    console.log('\nTesting resource listing...');
    const resources = await client.listResources();
    console.log(`Available resources: ${resources.resources.map(r => r.name).join(', ')}`);
    
    // Test listing tools
    console.log('\nTesting tool listing...');
    const tools = await client.listTools();
    console.log(`Available tools: ${tools.tools.map(t => t.name).join(', ')}`);
    
    // Test listing prompts
    console.log('\nTesting prompt listing...');
    const prompts = await client.listPrompts();
    console.log(`Available prompts: ${prompts.prompts.map(p => p.name).join(', ')}`);
    
    // Test reading a resource (if accounts are available)
    try {
      console.log('\nTesting resource reading (accounts)...');
      const accountsResource = await client.readResource({ uri: 'accounts://list' });
      console.log('Successfully read accounts resource');
      
      // Parse the accounts data
      const accountsData = JSON.parse(accountsResource.contents[0].text);
      console.log(`Found ${accountsData.length} accounts`);
    } catch (error) {
      console.error('Error reading accounts resource:', error.message);
    }
    
    console.log('\nTests completed');
  } catch (error) {
    console.error('Test failed:', error);
  } finally {
    // Clean up
    serverProcess.kill();
  }
}

runTest().catch(console.error);
