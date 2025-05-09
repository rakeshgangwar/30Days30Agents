/**
 * Web server for the Code Assistant UI
 */

const express = require('express');
const path = require('path');
const bodyParser = require('body-parser');
const cors = require('cors');
const http = require('http');
const { Server } = require('socket.io');
const RepositoryAnalysisAgent = require('./app');

// Initialize Express app
const app = express();
const server = http.createServer(app);
const io = new Server(server);
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '../public')));

// Initialize the agent
const agent = new RepositoryAnalysisAgent();
let initialized = false;

// Active sessions
const activeSessions = new Map();

// Initialize agent on startup
(async () => {
  try {
    await agent.initialize();
    initialized = true;
    console.log('Repository Analysis Agent initialized successfully');
  } catch (error) {
    console.error('Failed to initialize agent:', error.message);
  }
})();

// Socket.IO connection handling
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  // Handle repository connection
  socket.on('connect-repo', async (data) => {
    try {
      if (!initialized) {
        await agent.initialize();
        initialized = true;
      }

      const { type, path, owner, repo } = data;
      let result;

      if (type === 'local') {
        // Connect to local repository
        result = await agent.startConversation(path, {
          generateSummary: true
        });
      } else {
        // Connect to GitHub repository
        result = await agent.cloneAndStartConversation(owner, repo, {
          generateSummary: true
        });
      }

      if (result.success) {
        // Store session info
        activeSessions.set(result.sessionId, {
          socketId: socket.id,
          type,
          path: type === 'local' ? path : null,
          owner: type === 'github' ? owner : null,
          repo: type === 'github' ? repo : null
        });

        socket.emit('repo-connected', {
          success: true,
          sessionId: result.sessionId,
          summary: result.summary || 'Connected to repository successfully.'
        });
      } else {
        socket.emit('repo-connected', {
          success: false,
          error: result.error || 'Failed to connect to repository'
        });
      }
    } catch (error) {
      console.error('Error connecting to repository:', error);
      socket.emit('repo-connected', {
        success: false,
        error: error.message || 'Internal server error'
      });
    }
  });

  // Handle chat messages
  socket.on('chat-message', async (data) => {
    try {
      const { sessionId, message } = data;

      if (!sessionId || !message) {
        socket.emit('chat-response', {
          success: false,
          error: 'Session ID and message are required'
        });
        return;
      }

      // Send message to conversation manager
      socket.emit('chat-thinking', { sessionId });

      const result = await agent.conversationManager.askQuestion(sessionId, message);

      if (result.success) {
        socket.emit('chat-response', {
          success: true,
          message: result.response
        });
      } else {
        socket.emit('chat-response', {
          success: false,
          error: result.error || 'Failed to process message'
        });
      }
    } catch (error) {
      console.error('Error processing chat message:', error);
      socket.emit('chat-response', {
        success: false,
        error: error.message || 'Internal server error'
      });
    }
  });

  // Handle disconnect
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);

    // Clean up any sessions associated with this socket
    for (const [sessionId, session] of activeSessions.entries()) {
      if (session.socketId === socket.id) {
        activeSessions.delete(sessionId);
        console.log(`Cleaned up session ${sessionId}`);
      }
    }
  });
});

// API Routes
app.post('/api/repository/connect', async (req, res) => {
  try {
    if (!initialized) {
      await agent.initialize();
      initialized = true;
    }

    const { type, path, owner, repo } = req.body;
    let result;

    if (type === 'local') {
      // Connect to local repository
      result = await agent.startConversation(path, {
        generateSummary: true
      });
    } else {
      // Connect to GitHub repository
      result = await agent.cloneAndStartConversation(owner, repo, {
        generateSummary: true
      });
    }

    if (result.success) {
      res.json({
        success: true,
        sessionId: result.sessionId,
        summary: result.summary || 'Connected to repository successfully.'
      });
    } else {
      res.status(400).json({
        success: false,
        error: result.error || 'Failed to connect to repository'
      });
    }
  } catch (error) {
    console.error('Error connecting to repository:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
});

app.post('/api/chat/message', async (req, res) => {
  try {
    const { sessionId, message } = req.body;

    if (!sessionId || !message) {
      return res.status(400).json({
        success: false,
        error: 'Session ID and message are required'
      });
    }

    // Send message to conversation manager
    const result = await agent.conversationManager.askQuestion(sessionId, message);

    if (result.success) {
      res.json({
        success: true,
        message: result.response
      });
    } else {
      res.status(400).json({
        success: false,
        error: result.error || 'Failed to process message'
      });
    }
  } catch (error) {
    console.error('Error processing chat message:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
});

app.post('/api/repository/analyze', async (req, res) => {
  try {
    if (!initialized) {
      await agent.initialize();
      initialized = true;
    }

    const { type, owner, repo } = req.body;

    if (type !== 'github') {
      return res.status(400).json({
        success: false,
        error: 'Only GitHub repositories can be analyzed at this time'
      });
    }

    if (!owner || !repo) {
      return res.status(400).json({
        success: false,
        error: 'Owner and repo are required'
      });
    }

    // Analyze repository
    console.log(`Analyzing repository ${owner}/${repo}...`);
    const result = await agent.analyzeRepository(owner, repo, {
      dryRun: true // Don't create issues automatically
    });

    if (result.success) {
      res.json({
        success: true,
        repositoryInfo: result.repositoryInfo,
        findings: result.findings,
        report: result.report
      });
    } else {
      res.status(400).json({
        success: false,
        error: result.error || 'Failed to analyze repository'
      });
    }
  } catch (error) {
    console.error('Error analyzing repository:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
});

app.post('/api/issues/create', async (req, res) => {
  try {
    const { repositoryType, owner, repo, title, body, labels } = req.body;

    if (repositoryType !== 'github') {
      return res.status(400).json({
        success: false,
        error: 'Issues can only be created for GitHub repositories'
      });
    }

    if (!owner || !repo || !title || !body) {
      return res.status(400).json({
        success: false,
        error: 'Owner, repo, title, and body are required'
      });
    }

    // Create issue
    const result = await agent.issueManagement.createIssue(owner, repo, {
      title,
      body,
      labels: labels || []
    });

    if (result.success) {
      res.json({
        success: true,
        issueNumber: result.issueNumber,
        issueUrl: result.issueUrl
      });
    } else {
      res.status(400).json({
        success: false,
        error: result.error || 'Failed to create issue'
      });
    }
  } catch (error) {
    console.error('Error creating issue:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
});

app.post('/api/issues/create-batch', async (req, res) => {
  try {
    const { repositoryType, owner, repo, issues } = req.body;

    if (repositoryType !== 'github') {
      return res.status(400).json({
        success: false,
        error: 'Issues can only be created for GitHub repositories'
      });
    }

    if (!owner || !repo || !issues || !Array.isArray(issues) || issues.length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Owner, repo, and issues array are required'
      });
    }

    // Create issues
    const results = [];
    for (const issueData of issues) {
      const result = await agent.issueManagement.createIssue(owner, repo, {
        title: issueData.title,
        body: issueData.body || issueData.description,
        labels: issueData.labels || []
      });

      results.push({
        title: issueData.title,
        success: result.success,
        issueNumber: result.issueNumber,
        issueUrl: result.issueUrl,
        error: result.error
      });
    }

    res.json({
      success: true,
      results
    });
  } catch (error) {
    console.error('Error creating issues:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
});

// Catch-all route to serve the main HTML file
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

// Start server
server.listen(port, () => {
  console.log(`Code Assistant UI server running at http://localhost:${port}`);
});
