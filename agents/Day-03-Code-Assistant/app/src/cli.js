#!/usr/bin/env node
/**
 * Command-line interface for the Repository Analysis and Issue Creation Agent
 */

const RepositoryAnalysisAgent = require('./app');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

// Parse command-line arguments
const yargs = require('yargs');
const argv = yargs
  .usage('Usage: $0 <command> [options]')
  .command('analyze <owner> <repo>', 'Analyze a GitHub repository', (yargs) => {
    yargs
      .positional('owner', {
        describe: 'GitHub repository owner',
        type: 'string',
        demandOption: true
      })
      .positional('repo', {
        describe: 'GitHub repository name',
        type: 'string',
        demandOption: true
      })
      .option('config', {
        describe: 'Path to configuration file',
        type: 'string'
      })
      .option('dry-run', {
        describe: 'Run analysis without creating issues',
        type: 'boolean',
        default: false
      })
      .option('output', {
        describe: 'Path to output report file',
        type: 'string'
      });
  })
  .command('configure', 'Configure the agent', (yargs) => {
    yargs
      .option('github-token', {
        describe: 'GitHub API token',
        type: 'string'
      })
      .option('openai-key', {
        describe: 'OpenAI API key',
        type: 'string'
      });
  })
  .command('talk [owner] [repo]', 'Talk to a repository', (yargs) => {
    yargs
      .positional('owner', {
        describe: 'GitHub repository owner or local repository path',
        type: 'string'
      })
      .positional('repo', {
        describe: 'GitHub repository name (if owner is a GitHub username)',
        type: 'string'
      })
      .option('path', {
        describe: 'Path to local repository (alternative to positional arguments)',
        type: 'string'
      })
      .option('config', {
        describe: 'Path to configuration file',
        type: 'string'
      })
      .check((argv) => {
        // If path option is provided, use that
        if (argv.path) {
          return true;
        }

        // If owner is provided but no repo, treat owner as a local path
        if (argv.owner && !argv.repo) {
          argv.path = argv.owner;
          delete argv.owner;
          return true;
        }

        // If both owner and repo are provided, use them as GitHub repo
        if (argv.owner && argv.repo) {
          return true;
        }

        throw new Error('Either provide a local repository path or owner/repo combination');
      });
  })
  .demandCommand(1, 'You must provide a command')
  .help()
  .argv;

/**
 * Main function that processes commands
 */
async function main() {
  const command = argv._[0];

  if (command === 'analyze') {
    const { owner, repo } = argv;

    // Initialize agent
    const agent = new RepositoryAnalysisAgent({
      config: {
        configPath: argv.config ? path.dirname(argv.config) : undefined,
        configFile: argv.config ? path.basename(argv.config) : undefined
      }
    });

    try {
      // Run analysis
      console.log(`Analyzing repository ${owner}/${repo}...`);
      const result = await agent.analyzeRepository(owner, repo, {
        dryRun: argv.dryRun
      });

      if (!result.success) {
        console.error(`Analysis failed: ${result.error}`);
        process.exit(1);
      }

      // Output report
      console.log('\nAnalysis Summary:');
      console.log(`- Repository: ${result.repositoryInfo.name}`);
      console.log(`- Files Analyzed: ${result.report.summary.analyzedFiles}/${result.report.summary.totalFiles}`);
      console.log(`- Total Findings: ${result.report.summary.totalFindings}`);
      console.log('\nFindings by Priority:');
      Object.entries(result.report.summary.findingsByPriority).forEach(([priority, count]) => {
        console.log(`- ${priority}: ${count}`);
      });

      // Save report to file if specified
      if (argv.output) {
        fs.writeFileSync(argv.output, JSON.stringify(result.report, null, 2));
        console.log(`\nReport saved to ${argv.output}`);
      }
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  } else if (command === 'configure') {
    // Initialize agent
    const agent = new RepositoryAnalysisAgent();

    try {
      // Initialize configuration
      await agent.configManager.initialize();

      // Update credentials if provided
      if (argv.githubToken || argv.openaiKey) {
        const credentials = agent.configManager.getCredentials() || {};

        if (argv.githubToken) {
          credentials.githubToken = argv.githubToken;
        }

        if (argv.openaiKey) {
          credentials.openaiApiKey = argv.openaiKey;
        }

        await agent.configManager.saveCredentials(credentials);
        console.log('Credentials updated successfully.');
      } else {
        console.log('No credentials provided. Use --github-token and/or --openai-key options.');
      }
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  } else if (command === 'talk') {
    // Initialize agent
    const agent = new RepositoryAnalysisAgent({
      config: {
        configPath: argv.config ? path.dirname(argv.config) : undefined,
        configFile: argv.config ? path.basename(argv.config) : undefined
      }
    });

    try {
      let sessionResult;

      // Start conversation with repository
      if (argv.path) {
        // Use local repository
        const repoPath = path.resolve(argv.path);
        console.log(`Starting conversation with local repository at ${repoPath}...`);

        // Check if path exists
        let finalRepoPath = repoPath;
        try {
          const stats = fs.statSync(finalRepoPath);
          if (!stats.isDirectory()) {
            console.error(`Error: ${finalRepoPath} is not a directory`);
            process.exit(1);
          }
        } catch (error) {
          // Try looking in the repos directory
          const reposPath = path.join(process.cwd(), 'repos', path.basename(repoPath));
          try {
            const repoStats = fs.statSync(reposPath);
            if (repoStats.isDirectory()) {
              console.log(`Repository not found at ${finalRepoPath}`);
              console.log(`Found repository at ${reposPath}`);
              finalRepoPath = reposPath;
            } else {
              console.error(`Error: ${finalRepoPath} does not exist and ${reposPath} is not a directory`);
              process.exit(1);
            }
          } catch (repoError) {
            console.error(`Error: Repository not found at ${finalRepoPath} or ${reposPath}`);
            process.exit(1);
          }
        }

        sessionResult = await agent.startConversation(finalRepoPath, {
          generateSummary: true
        });
      } else if (argv.owner && argv.repo) {
        // Check if repository already exists in repos directory
        const reposDir = path.join(process.cwd(), 'repos');
        const repoName = `${argv.repo}`;
        const repoPath = path.join(reposDir, repoName);

        console.log(`Looking for GitHub repository ${argv.owner}/${argv.repo}...`);

        try {
          const stats = fs.statSync(repoPath);
          if (stats.isDirectory()) {
            console.log(`Repository ${argv.owner}/${argv.repo} already exists at ${repoPath}`);
            console.log(`Using existing repository...`);
            sessionResult = await agent.startConversation(repoPath, {
              generateSummary: true
            });
          } else {
            // Clone GitHub repository
            console.log(`Starting conversation with GitHub repository ${argv.owner}/${argv.repo}...`);
            sessionResult = await agent.cloneAndStartConversation(argv.owner, argv.repo, {
              generateSummary: true
            });
          }
        } catch (error) {
          // Repository doesn't exist, clone it
          console.log(`Repository ${argv.owner}/${argv.repo} not found locally. Cloning from GitHub...`);
          sessionResult = await agent.cloneAndStartConversation(argv.owner, argv.repo, {
            generateSummary: true
          });
        }
      } else {
        console.error('Either provide a local repository path or owner/repo combination');
        process.exit(1);
      }

      if (!sessionResult.success) {
        console.error(`Failed to start conversation: ${sessionResult.error}`);
        process.exit(1);
      }

      console.log(`Conversation started with session ID: ${sessionResult.sessionId}`);

      // Start interactive session
      await agent.startInteractiveSession(sessionResult.sessionId);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  } else {
    console.error('Unknown command. Use --help for usage information.');
    process.exit(1);
  }
}

// Run the application
main().catch(error => {
  console.error('Unhandled error:', error);
  process.exit(1);
});