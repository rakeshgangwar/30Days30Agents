# Talk to Your Repository

The "Talk to Your Repository" feature allows you to have a conversational interface with your codebase. You can ask questions about features, code implementation, architecture, and more, and receive intelligent responses based on the content of your repository.

## Usage

### Command Line Interface

You can use the "Talk to Your Repository" feature through the command line interface in several ways:

#### 1. Using npm script

```bash
# Talk to a local repository
npm run talk -- /path/to/repository

# Talk to a GitHub repository
npm run talk -- owner repo-name
```

#### 2. Using the CLI directly

```bash
# Talk to a local repository
node src/cli.js talk /path/to/repository

# Talk to a GitHub repository
node src/cli.js talk owner repo-name
```

#### 3. Using options

```bash
# Talk to a local repository
node src/cli.js talk --path /path/to/repository

# Talk to a GitHub repository
node src/cli.js talk --owner username --repo repository-name
```

### Examples

```bash
# Talk to a local repository
npm run talk -- /Users/username/Projects/my-project

# Talk to a GitHub repository
npm run talk -- facebook react

# Talk to a repository in the repos directory
npm run talk -- my-repo
```

## How It Works

The "Talk to Your Repository" feature works by:

1. **Repository Analysis**: The system analyzes the repository structure and code to understand its components and relationships.

2. **Vector Database Indexing**: Code snippets are converted to vector embeddings and stored in a vector database for semantic search.

3. **Context Building**: When you ask a question, the system uses semantic search to find the most relevant code snippets based on your query.

4. **AI Processing**: The question, conversation history, and relevant code snippets are sent to an AI model for processing.

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

## Tips for Better Results

1. **Be Specific**: Ask specific questions about the codebase rather than general questions.

2. **Start with Structure**: Begin by asking about the overall structure and architecture of the project.

3. **Follow Up**: Ask follow-up questions to dive deeper into specific areas of interest.

4. **Reference Files**: If you know the file you're interested in, mention it in your question.

5. **Use Technical Terms**: Use technical terms and concepts relevant to the codebase.

## Troubleshooting

### Repository Not Found

If you get an error like "Repository not found", try:

1. Check if the repository exists at the specified path
2. If using a GitHub repository, check if the owner and repo name are correct
3. Try using the full path to the repository

### No Relevant Code Found

If you get responses like "I don't have enough information", try:

1. Ask about the overall structure of the project first
2. Be more specific in your questions
3. Reference specific files or components if you know them

### Other Issues

If you encounter other issues:

1. Check if the repository is accessible
2. Ensure you have the necessary API keys configured
3. Try with a smaller repository first

## Configuration

You can configure the "Talk to Your Repository" feature by editing the configuration file:

```bash
# Configure API keys
npm run configure -- --openai-key YOUR_OPENAI_API_KEY --github-token YOUR_GITHUB_TOKEN
```

## Limitations

1. **Repository Size**: Very large repositories may not be fully indexed due to token limitations.
2. **Binary Files**: Binary files are not analyzed.
3. **Context Window**: There's a limit to how much context can be included in each query.
4. **Language Support**: Some programming languages may have better support than others.

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
