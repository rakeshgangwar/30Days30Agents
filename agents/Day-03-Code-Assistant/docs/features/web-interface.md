# Web Interface

The Code Assistant provides a user-friendly web interface for interacting with repositories and creating issues.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Implementation Details](#implementation-details)
4. [Usage Guide](#usage-guide)
5. [Technical Architecture](#technical-architecture)
6. [Future Enhancements](#future-enhancements)

## Overview

The web interface provides a graphical user interface for the Code Assistant, making it easier to:

- Connect to GitHub or local repositories
- Have conversations with your codebase
- Create issues based on your findings

This interface is designed to be intuitive and accessible, allowing users to leverage the power of the Code Assistant without needing to use the command line.

## Features

### Repository Selection

- Choose between local and GitHub repositories
- Input repository details (path or owner/name)
- View and select from recently used repositories

### Talk to Your Repository

- Chat-like interface for asking questions about your codebase
- Real-time responses using WebSockets
- Markdown formatting for code snippets and explanations
- Conversation history preservation

### Issue Creation

- **AI-Powered Analysis**: Analyze repositories to automatically identify potential issues
- **Issue Review**: Review and select which issues to create
- **Batch Creation**: Create multiple issues at once
- **Priority Levels**: Issues are categorized by priority (Critical, High, Medium, Low)

## Implementation Details

The web interface is implemented using:

- **Frontend**: HTML, CSS, JavaScript with Tailwind CSS for styling
- **Backend**: Express.js server with Socket.IO for real-time communication
- **API**: RESTful API endpoints for repository connection, chat, and issue creation

### Key Components

#### Frontend

- `index.html`: Main HTML structure
- `styles.css`: Custom styling on top of Tailwind CSS
- `app.js`: Client-side JavaScript for UI interactions and API calls

#### Backend

- `server.js`: Express server with Socket.IO integration
- API endpoints for repository connection, chat, and issue creation
- WebSocket handlers for real-time communication

## Usage Guide

### Starting the Web Interface

```bash
npm run web
```

Then open your browser to http://localhost:3000

### Connecting to a Repository

1. Select the repository type (Local or GitHub)
2. For local repositories, enter the full path to the repository
3. For GitHub repositories, enter the owner and repository name
4. Click "Connect to Repository"
5. The connection status will be displayed in the repository section
6. Once connected, the form will collapse and show the connected repository name
7. You can click "Change Repository" to connect to a different repository

### Talking to Your Repository

1. Once connected, you'll see a repository summary
2. Type your question in the chat input
3. Receive AI-powered responses about your codebase
4. Continue the conversation with follow-up questions

### Creating Issues

1. Click "Analyze Repository" to start the AI analysis
2. Wait for the analysis to complete (this may take a few minutes)
3. Review the findings displayed in the list
4. Select the issues you want to create (or use "Select All")
5. Click "Create Selected Issues" to submit them to GitHub
6. You'll receive confirmation of which issues were created successfully

## Technical Architecture

The web interface follows a client-server architecture:

```
Client (Browser)                 Server
+----------------+              +----------------+
|                |  HTTP/WS     |                |
|  HTML/CSS/JS   |<------------>|  Express.js    |
|                |              |  Socket.IO     |
+----------------+              +----------------+
                                       |
                                       v
                               +----------------+
                               |                |
                               |  Repository    |
                               |  Analysis      |
                               |  Agent         |
                               |                |
                               +----------------+
                                       |
                                       v
                               +----------------+
                               |                |
                               |  GitHub API    |
                               |  OpenAI API    |
                               |                |
                               +----------------+
```

### Real-time Communication

The interface uses Socket.IO for real-time communication between the client and server:

- **Repository Connection**: Emits `connect-repo` event and listens for `repo-connected` response
- **Chat Messages**: Emits `chat-message` event and listens for `chat-response`
- **Thinking Indicator**: Server emits `chat-thinking` event to show when the AI is processing

The server uses the `askQuestion` method from the `RepoConversationManager` to process user questions and generate responses.

## Future Enhancements

Planned improvements for the web interface include:

1. **User Authentication**: Add user login to manage multiple repositories
2. **Repository Dashboard**: Overview of all connected repositories
3. **Code Visualization**: Visual representation of code structure and relationships
4. **Collaborative Features**: Allow multiple users to discuss the same repository
5. **Custom Themes**: Light and dark mode support
6. **Mobile Optimization**: Responsive design for mobile devices
7. **File Browser**: Browse and view repository files directly in the interface
8. **Code Editor**: Edit files and create pull requests
9. **Analytics**: Track usage patterns and popular questions
10. **Offline Support**: Progressive Web App features for offline use
