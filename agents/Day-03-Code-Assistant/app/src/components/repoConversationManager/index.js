/**
 * Repository Conversation Manager
 *
 * This component manages conversations with a repository, allowing users to
 * ask questions about the codebase and receive intelligent responses.
 */

const path = require('path');
const fs = require('fs').promises;
const readline = require('readline');

class RepoConversationManager {
  constructor(options = {}) {
    this.options = {
      historyPath: options.historyPath || path.join(process.cwd(), 'storage', 'conversations'),
      maxHistoryLength: options.maxHistoryLength || 20,
      ...options
    };

    this.repositoryAccess = options.repositoryAccess;
    this.codeAnalysis = options.codeAnalysis;
    this.aiAnalysis = options.aiAnalysis;
    this.vectorDatabase = options.vectorDatabase;

    this.conversations = new Map();
    this.initialized = false;
  }

  async initialize() {
    if (this.initialized) return true;

    try {
      // Create history directory if it doesn't exist
      await fs.mkdir(this.options.historyPath, { recursive: true });

      this.initialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize RepoConversationManager:', error.message);
      return false;
    }
  }

  /**
   * Start a new conversation with a repository
   * @param {string} repoPath - Path to the repository
   * @param {Object} options - Conversation options
   * @returns {Object} - Conversation session
   */
  async startConversation(repoPath, options = {}) {
    if (!this.initialized) {
      await this.initialize();
    }

    const sessionId = options.sessionId || `session_${Date.now()}`;

    // Create a new conversation session
    const session = {
      id: sessionId,
      repoPath,
      history: [],
      startTime: new Date(),
      lastActivity: new Date()
    };

    // Store the session
    this.conversations.set(sessionId, session);

    // Generate repository summary if requested
    if (options.generateSummary) {
      await this.generateRepositorySummary(sessionId);
    }

    // Index repository with vector database if available
    if (this.vectorDatabase && options.indexRepository !== false) {
      console.log('Indexing repository with vector database...');
      const repoId = `repo_${path.basename(repoPath)}_${Date.now()}`;
      session.repoId = repoId;

      try {
        await this.indexRepositoryWithVectorDb(repoId, repoPath);
        console.log('Repository indexed successfully.');
      } catch (error) {
        console.error('Error indexing repository:', error.message);
      }
    }

    return {
      success: true,
      sessionId,
      message: 'Conversation started. You can now ask questions about the repository.'
    };
  }

  /**
   * Generate a summary of the repository
   * @param {string} sessionId - Conversation session ID
   * @returns {Object} - Summary result
   */
  async generateRepositorySummary(sessionId) {
    const session = this.conversations.get(sessionId);
    if (!session) {
      return {
        success: false,
        error: 'Session not found'
      };
    }

    try {
      // Get repository name from path
      const repoName = path.basename(session.repoPath);

      // Create repository info
      const repositoryInfo = {
        name: repoName,
        description: `Repository ${repoName}`,
        path: session.repoPath
      };

      // List files
      const files = await this.repositoryAccess.listRepositoryFiles(session.repoPath);

      // Read a sample of files for analysis
      const sampleSize = Math.min(files.length, 20);
      const sampleFiles = files.slice(0, sampleSize);

      const fileContents = [];
      for (const filePath of sampleFiles) {
        const content = await this.repositoryAccess.readFileContent(filePath);
        if (content.success) {
          fileContents.push({
            path: filePath,
            content: content.content
          });
        }
      }

      // Analyze files
      const analysisResults = await this.codeAnalysis.analyzeFiles(fileContents);

      // Generate repository summary
      const summaryPrompt = `
        You are a code analysis assistant. Please provide a brief summary of this repository.

        Repository: ${repositoryInfo.name}
        Path: ${repositoryInfo.path}

        Files analyzed: ${fileContents.length}/${files.length}

        Key file types:
        ${this.summarizeFileTypes(files)}

        Please provide:
        1. A brief overview of what this repository appears to be
        2. The main technologies and frameworks used
        3. The key components or modules identified
        4. Any notable patterns or architecture observed
      `;

      const summaryResponse = await this.aiAnalysis.aiInteractor.analyzeWithAI(summaryPrompt, {
        maxTokens: 1000
      });

      if (summaryResponse.success) {
        // Add summary to conversation history
        session.summary = summaryResponse.response;

        // Add system message to history
        session.history.push({
          role: 'system',
          content: `Repository summary: ${summaryResponse.response}`,
          timestamp: new Date()
        });

        return {
          success: true,
          summary: summaryResponse.response
        };
      } else {
        return {
          success: false,
          error: 'Failed to generate summary'
        };
      }
    } catch (error) {
      console.error('Error generating repository summary:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Ask a question about the repository
   * @param {string} sessionId - Conversation session ID
   * @param {string} question - User's question
   * @returns {Object} - Response
   */
  /**
   * Index a repository with the vector database
   * @param {string} repoId - Repository identifier
   * @param {string} repoPath - Path to the repository
   * @returns {Promise<Object>} - Result
   */
  async indexRepositoryWithVectorDb(repoId, repoPath) {
    if (!this.vectorDatabase) {
      return {
        success: false,
        error: 'Vector database not available'
      };
    }

    try {
      // Index repository
      const result = await this.vectorDatabase.indexRepository(
        repoId,
        repoPath,
        this.repositoryAccess,
        this.codeAnalysis
      );

      return result;
    } catch (error) {
      console.error('Error indexing repository with vector database:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async askQuestion(sessionId, question) {
    const session = this.conversations.get(sessionId);
    if (!session) {
      return {
        success: false,
        error: 'Session not found'
      };
    }

    try {
      // Update session activity
      session.lastActivity = new Date();

      // Add user question to history
      session.history.push({
        role: 'user',
        content: question,
        timestamp: new Date()
      });

      // Find relevant code snippets if vector database is available
      let relevantCode = '';
      if (this.vectorDatabase && session.repoId) {
        console.log('Searching vector database for relevant code...');
        const searchResults = await this.vectorDatabase.searchSimilarCode(
          session.repoId,
          question,
          { limit: 5 }
        );

        if (searchResults.success && searchResults.results.length > 0) {
          console.log(`Found ${searchResults.results.length} relevant code snippets.`);
          relevantCode = searchResults.results.map(result =>
            `File: ${result.filePath}\n${result.content}`
          ).join('\n\n');
        } else {
          console.log('No relevant code snippets found in vector database.');
        }
      }

      // If no vector database or no results, find relevant files based on keywords
      if (!relevantCode) {
        relevantCode = await this.findRelevantCodeByKeywords(session.repoPath, question);
      }

      // Prepare conversation history for context
      const conversationContext = session.history
        .slice(-this.options.maxHistoryLength)
        .map(msg => `${msg.role}: ${msg.content}`)
        .join('\n\n');

      // Create prompt for AI
      const prompt = `
        You are a code assistant helping with questions about a repository.

        Repository: ${path.basename(session.repoPath)}

        ${session.summary ? `Repository summary: ${session.summary}` : ''}

        Recent conversation:
        ${conversationContext}

        Relevant code snippets:
        ${relevantCode}

        User question: ${question}

        Please provide a helpful, accurate, and concise response to the user's question.
        If the relevant code snippets don't contain enough information to answer the question,
        acknowledge that and provide the best response you can based on the available information.
      `;

      // Call AI
      const aiResponse = await this.aiAnalysis.aiInteractor.analyzeWithAI(prompt, {
        maxTokens: 2000
      });

      if (aiResponse.success) {
        // Add assistant response to history
        session.history.push({
          role: 'assistant',
          content: aiResponse.response,
          timestamp: new Date()
        });

        // Save conversation history
        await this.saveConversationHistory(sessionId);

        return {
          success: true,
          response: aiResponse.response
        };
      } else {
        return {
          success: false,
          error: 'Failed to generate response'
        };
      }
    } catch (error) {
      console.error('Error processing question:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Find relevant code based on keywords in the question
   * @param {string} repoPath - Path to the repository
   * @param {string} question - User's question
   * @returns {string} - Relevant code snippets
   */
  async findRelevantCodeByKeywords(repoPath, question) {
    try {
      // Extract keywords from question
      const keywords = this.extractKeywords(question);

      // List files
      const files = await this.repositoryAccess.listRepositoryFiles(repoPath);

      // Score files based on path relevance to keywords
      const scoredFiles = files.map(filePath => {
        const score = keywords.reduce((sum, keyword) => {
          return sum + (filePath.toLowerCase().includes(keyword.toLowerCase()) ? 1 : 0);
        }, 0);

        return { filePath, score };
      });

      // Sort by score and take top 5
      const topFiles = scoredFiles
        .filter(file => file.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, 5)
        .map(file => file.filePath);

      // If no files match keywords, take a sample of important files
      if (topFiles.length === 0) {
        const importantPatterns = [
          /main\.(js|ts|py|java|go|rb)$/,
          /index\.(js|ts|py|java|go|rb)$/,
          /app\.(js|ts|py|java|go|rb)$/,
          /config\.(js|ts|py|java|go|rb|json|yaml|yml)$/,
          /package\.json$/,
          /README\.md$/
        ];

        for (const pattern of importantPatterns) {
          const matches = files.filter(file => pattern.test(file));
          if (matches.length > 0) {
            topFiles.push(...matches.slice(0, 2));
            if (topFiles.length >= 5) break;
          }
        }
      }

      // Read content of top files
      let relevantCode = '';
      for (const filePath of topFiles) {
        const content = await this.repositoryAccess.readFileContent(filePath);
        if (content.success) {
          // Truncate large files
          const truncatedContent = content.content.length > 1000
            ? content.content.substring(0, 1000) + '...'
            : content.content;

          relevantCode += `File: ${filePath}\n${truncatedContent}\n\n`;
        }
      }

      return relevantCode;
    } catch (error) {
      console.error('Error finding relevant code:', error.message);
      return '';
    }
  }

  /**
   * Extract keywords from a question
   * @param {string} question - User's question
   * @returns {string[]} - Keywords
   */
  extractKeywords(question) {
    // Remove common words and punctuation
    const commonWords = ['a', 'an', 'the', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'like', 'through', 'over', 'before', 'between', 'after', 'since', 'without', 'under', 'within', 'along', 'following', 'across', 'behind', 'beyond', 'plus', 'except', 'but', 'up', 'out', 'around', 'down', 'off', 'above', 'near', 'and', 'or', 'but', 'so', 'because', 'if', 'when', 'where', 'how', 'what', 'why', 'who', 'which', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'can', 'could', 'will', 'would', 'shall', 'should', 'may', 'might', 'must', 'of'];

    // Split question into words
    const words = question.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 2 && !commonWords.includes(word));

    // Return unique keywords
    return [...new Set(words)];
  }

  /**
   * Summarize file types in the repository
   * @param {string[]} files - List of file paths
   * @returns {string} - Summary of file types
   */
  summarizeFileTypes(files) {
    const extensions = {};

    files.forEach(filePath => {
      const ext = path.extname(filePath).toLowerCase();
      if (ext) {
        extensions[ext] = (extensions[ext] || 0) + 1;
      }
    });

    return Object.entries(extensions)
      .sort((a, b) => b[1] - a[1])
      .map(([ext, count]) => `${ext}: ${count} files`)
      .join('\n');
  }

  /**
   * Save conversation history to disk
   * @param {string} sessionId - Conversation session ID
   */
  async saveConversationHistory(sessionId) {
    const session = this.conversations.get(sessionId);
    if (!session) return;

    try {
      // Ensure history path exists
      await fs.mkdir(this.options.historyPath, { recursive: true });

      // Create a sanitized version of the session for storage
      const sanitizedSession = {
        id: session.id,
        repoPath: session.repoPath,
        repoId: session.repoId,
        history: session.history,
        summary: session.summary,
        startTime: session.startTime,
        lastActivity: session.lastActivity
      };

      const historyPath = path.join(this.options.historyPath, `${sessionId}.json`);
      await fs.writeFile(historyPath, JSON.stringify(sanitizedSession, null, 2));
    } catch (error) {
      console.error('Error saving conversation history:', error.message);
    }
  }

  /**
   * Start an interactive CLI conversation
   * @param {string} sessionId - Conversation session ID
   */
  async startInteractiveSession(sessionId) {
    const session = this.conversations.get(sessionId);
    if (!session) {
      console.error('Session not found');
      return;
    }

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    console.log('\nTalk to Your Repository');
    console.log('======================');
    console.log(`Repository: ${path.basename(session.repoPath)}`);
    console.log('Type "exit" to end the conversation\n');

    if (session.summary) {
      console.log('Repository Summary:');
      console.log(session.summary);
      console.log('');
    }

    const askQuestion = () => {
      rl.question('You: ', async (question) => {
        if (question.toLowerCase() === 'exit') {
          console.log('\nEnding conversation. Goodbye!');
          rl.close();
          return;
        }

        console.log('\nProcessing your question...');

        const response = await this.askQuestion(sessionId, question);

        if (response.success) {
          console.log(`\nAssistant: ${response.response}\n`);
        } else {
          console.log(`\nError: ${response.error}\n`);
        }

        askQuestion();
      });
    };

    askQuestion();
  }
}

module.exports = RepoConversationManager;
