# GitHub API Integration

This document provides details about the implementation of the GitHub API integration in the Code Assistant project.

## Table of Contents

1. [Overview](#overview)
2. [Implementation Details](#implementation-details)
3. [Usage](#usage)
4. [Error Handling](#error-handling)
5. [Future Improvements](#future-improvements)

## Overview

The GitHub API integration is a critical component of the Code Assistant, enabling it to create issues in GitHub repositories based on the findings from code analysis. It uses the Octokit REST client to interact with the GitHub API, providing a robust and reliable way to create and manage issues.

## Implementation Details

The GitHub API integration is implemented in the `IssueManagementSystem` component. It uses the Octokit REST client to interact with the GitHub API, providing methods for creating issues, checking for duplicates, and managing issue tracking.

### Key Components

#### IssueManagementSystem Class

The `IssueManagementSystem` class is responsible for creating, formatting, and submitting GitHub issues:

```javascript
const { Octokit } = require('@octokit/rest');

class IssueManagementSystem {
  constructor(config, storageManager) {
    this.config = {
      createIssues: config.createIssues !== undefined ? config.createIssues : true,
      maxIssuesToCreate: config.maxIssuesToCreate || 10,
      labelPrefix: config.labelPrefix || 'ai-analysis',
      priorityThreshold: config.priorityThreshold || 'Low',
      issueTemplate: config.issueTemplate || 'default',
      dryRun: config.dryRun !== undefined ? config.dryRun : false,
      ...config
    };
    
    this.storageManager = storageManager;
    
    // Initialize GitHub client if credentials are provided
    if (config.github && config.github.token) {
      this.initializeGitHub(config.github);
    }
  }
  
  initializeGitHub(config) {
    try {
      if (!config || !config.token) {
        console.warn('GitHub token not provided');
        this.githubInitialized = false;
        return false;
      }

      this.octokit = new Octokit({
        auth: config.token
      });
      
      this.githubInitialized = true;
      console.log('GitHub client initialized successfully');
      return true;
    } catch (error) {
      console.error('Failed to initialize GitHub client:', error.message);
      this.githubInitialized = false;
      return false;
    }
  }
  
  async createIssue(owner, repo, issueData) {
    if (!this.githubInitialized) {
      return { success: false, error: 'GitHub client not initialized' };
    }
    
    try {
      // Create the issue using GitHub API
      const response = await this.octokit.issues.create({
        owner,
        repo,
        title: issueData.title,
        body: issueData.body,
        labels: issueData.labels
      });
      
      return {
        success: true,
        issueNumber: response.data.number,
        issueUrl: response.data.html_url
      };
    } catch (error) {
      console.error('Error creating GitHub issue:', error.message);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  async checkForDuplicateIssue(owner, repo, title) {
    if (!this.githubInitialized) {
      return false; // Cannot check for duplicates without GitHub client
    }
    
    try {
      // Search for open issues with similar titles
      const response = await this.octokit.search.issuesAndPullRequests({
        q: `repo:${owner}/${repo} is:issue is:open "${title.substring(0, 50)}"`
      });
      
      // Check if any issues have very similar titles
      return response.data.items.some(issue => {
        const similarity = this.calculateTitleSimilarity(issue.title, title);
        return similarity > 0.8; // 80% similarity threshold
      });
    } catch (error) {
      console.error('Error checking for duplicate issues:', error.message);
      return false; // Assume no duplicates if check fails
    }
  }
}
```

### Key Features

- **GitHub API Integration**: Uses the Octokit REST client to interact with the GitHub API
- **Issue Creation**: Creates issues in GitHub repositories based on analysis findings
- **Duplicate Detection**: Checks for duplicate issues to avoid creating duplicates
- **Issue Formatting**: Formats findings into well-structured GitHub issues
- **Issue Tracking**: Tracks created issues for reporting and statistics

## Usage

The GitHub API integration is used by the `IssueManagementSystem` to create issues in GitHub repositories:

```javascript
// Initialize the IssueManagementSystem
const issueManagementSystem = new IssueManagementSystem({
  createIssues: true,
  maxIssuesToCreate: 10,
  labelPrefix: 'ai-analysis',
  priorityThreshold: 'Low',
  github: {
    token: process.env.GITHUB_TOKEN
  }
}, storageManager);

// Create issues from findings
const result = await issueManagementSystem.createIssuesFromFindings('owner', 'repo', findings);
```

## Error Handling

The GitHub API integration includes robust error handling:

1. **Initialization Errors**: If the GitHub client fails to initialize, the error is logged and the system falls back to dry run mode
2. **API Call Errors**: If an API call fails, the error is logged and returned in the result
3. **Duplicate Detection**: If a duplicate issue is detected, it's skipped and marked as a duplicate in the result

## Future Improvements

Future improvements to the GitHub API integration could include:

1. **Rate Limiting**: Implement rate limiting and backoff strategies to handle GitHub API rate limits
2. **Issue Templates**: Support for custom issue templates based on finding types
3. **Issue Updates**: Update existing issues instead of creating duplicates
4. **Issue Comments**: Add comments to existing issues with additional information
5. **Pull Request Creation**: Create pull requests with fixes for simple issues
6. **Assignees and Reviewers**: Automatically assign issues to team members based on expertise
