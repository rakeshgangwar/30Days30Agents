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