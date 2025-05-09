# Talk to Your Repository

The "Talk to Your Repository" feature allows you to have a conversational interface with your codebase. You can ask questions about features, code implementation, architecture, and more, and receive intelligent responses based on the content of your repository.

## Table of Contents

1. [Overview](#overview)
2. [Usage](#usage)
3. [How It Works](#how-it-works)
4. [Example Queries](#example-queries)
5. [Implementation Details](#implementation-details)
6. [Future Enhancements](#future-enhancements)

## Overview

The "Talk to Your Repository" feature provides a natural language interface to your codebase, allowing you to:

- Ask questions about code implementation
- Understand the architecture and structure of the repository
- Find specific features or functionality
- Get explanations of complex code sections
- Receive summaries of the codebase

This feature is particularly useful for:

- Onboarding new developers to a project
- Understanding unfamiliar codebases
- Quickly finding information without having to search through files
- Getting high-level overviews of project architecture

## Usage

### Command Line Interface

You can use the "Talk to Your Repository" feature through the command line interface:

```bash
# Talk to a local repository
node src/cli.js talk /path/to/repository

# Talk to a GitHub repository
node src/cli.js talk --owner username --repo repository-name
```

### Interactive Session

Once you start a conversation, you'll enter an interactive session where you can ask questions about the repository:

```
Talk to Your Repository
======================
Repository: my-project
Type "exit" to end the conversation

Repository Summary:
This repository appears to be a Node.js web application built with Express.js.
It uses MongoDB for data storage and includes user authentication features.
The main components include user management, product catalog, and order processing.

You: What is the main entry point of the application?
Assistant: The main entry point of the application is the `app.js` file in the root directory. This file initializes the Express application, sets up middleware, connects to the MongoDB database, and defines the routes. The server is started by listening on a port defined in the environment variables or defaulting to port 3000.

You: How is authentication implemented?
Assistant: Authentication is implemented using JSON Web Tokens (JWT) through the `jsonwebtoken` package. The implementation is located in the `src/middleware/auth.js` file.

When a user logs in (via `src/controllers/userController.js`), their credentials are verified against the database, and if valid, a JWT token is generated with the user's ID and role. This token is then returned to the client.

For protected routes, the `auth` middleware is used, which:
1. Extracts the token from the Authorization header
2. Verifies the token using the JWT_SECRET environment variable
3. Decodes the user information and attaches it to the request object
4. Allows the request to proceed if the token is valid

The middleware also supports role-based access control by checking the user's role against the required roles for specific routes.
```

## How It Works

The "Talk to Your Repository" feature works by:

1. **Repository Analysis**: The system analyzes the repository structure and code to understand its components and relationships.

2. **Vector Database Indexing**: Code snippets are converted to vector embeddings and stored in a vector database for semantic search.

3. **Context Building**: When you ask a question, the system uses semantic search to find the most relevant code snippets based on your query.

4. **AI Processing**: The question, conversation history, and relevant code snippets are sent to an AI model (OpenAI's GPT-4 by default) for processing.

5. **Response Generation**: The AI generates a response based on the repository context and your question.

6. **Conversation History**: The system maintains a history of your conversation to provide context for future questions.

## Example Queries

Here are some example questions you can ask:

- "What is the overall architecture of this project?"
- "How is authentication implemented?"
- "Where is the database connection configured?"
- "Explain how the user registration process works."
- "What are the main components of this application?"
- "How are API routes organized?"
- "What testing framework is used in this project?"
- "Show me the main data models."
- "How does the error handling work?"
- "What dependencies does this project use?"

## Implementation Details

The "Talk to Your Repository" feature is implemented through several components:

### RepoConversationManager

The `RepoConversationManager` class is responsible for:

- Managing conversation sessions
- Finding relevant code snippets for queries
- Generating repository summaries
- Processing questions and generating responses
- Maintaining conversation history

### Vector Database Integration

The feature includes vector database integration for efficient semantic code search:

- Code snippets are converted to vector embeddings using OpenAI's text-embedding-3-small model
- Embeddings are stored in an efficient vector database (HNSWLib)
- Semantic search finds the most relevant code snippets for each query
- This significantly improves response quality and relevance

### AI Analysis Coordinator

The `AIAnalysisCoordinator` is used to:

- Prepare prompts for the AI model
- Process AI responses
- Handle API interactions

## Future Enhancements

We plan to enhance the "Talk to Your Repository" feature with:

1. **Multi-Repository Support**: Allow conversations that span multiple related repositories.

2. **Code Generation**: Add the ability to generate code based on natural language descriptions.

3. **Visualization**: Provide visual representations of code relationships and architecture.

4. **Integration with IDEs**: Add plugins for popular IDEs like VS Code and IntelliJ.

5. **Custom Instructions**: Allow users to provide custom instructions or context for the conversation.

6. **Memory Management**: Implement more sophisticated memory management for longer conversations.

7. **Multilingual Support**: Add support for multiple programming languages and natural languages.

8. **Vector Database Optimization**: Further optimize the vector database for larger codebases and more efficient retrieval.

## Conclusion

The "Talk to Your Repository" feature provides a powerful natural language interface to your codebase, making it easier to understand, navigate, and work with repositories. By leveraging AI and code analysis, it offers intelligent responses to your questions about the code, saving time and improving productivity.
