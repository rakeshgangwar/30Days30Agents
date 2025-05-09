// Issue Management System Component
// This component creates, formats, and submits GitHub issues

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
      // In a real implementation, we would initialize the GitHub client (Octokit) here
      // For now, we'll just set a flag
      this.githubInitialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize GitHub client:', error.message);
      this.githubInitialized = false;
      return false;
    }
  }
  
  async createIssuesFromFindings(owner, repo, findings, options = {}) {
    if (!this.githubInitialized && !this.config.dryRun) {
      return { 
        success: false, 
        error: 'GitHub client not initialized and not in dry run mode',
        results: [],
        summary: { total: 0, created: 0, duplicates: 0, errors: 0 }
      };
    }
    
    const repositoryId = `${owner}/${repo}`;
    const results = [];
    let createdCount = 0;
    let duplicateCount = 0;
    let errorCount = 0;
    
    // Apply limit if specified
    const limit = options.limit || this.config.maxIssuesToCreate;
    const limitedFindings = limit ? findings.slice(0, limit) : findings;
    
    // Skip low priority findings if configured to do so
    const skipLowPriority = options.skipLowPriority || (this.config.priorityThreshold !== 'Low');
    const filteredFindings = skipLowPriority 
      ? limitedFindings.filter(finding => finding.priority !== 'Low')
      : limitedFindings;
    
    for (const finding of filteredFindings) {
      try {
        // Format the finding into an issue
        const issueData = this.formatFinding(finding);
        
        // Check for duplicate issues
        const isDuplicate = await this.checkForDuplicateIssue(owner, repo, issueData.title);
        
        if (isDuplicate) {
          results.push({
            finding,
            success: false,
            isDuplicate: true
          });
          duplicateCount++;
          continue;
        }
        
        if (this.config.dryRun) {
          // In dry run mode, don't actually create issues
          results.push({
            finding,
            success: true,
            dryRun: true,
            issueData
          });
          createdCount++;
        } else {
          // Create the issue
          const issue = await this.createIssue(owner, repo, issueData);
          
          if (issue.success) {
            // Record the created issue
            await this.recordCreatedIssue(repositoryId, {
              issueNumber: issue.issueNumber,
              issueUrl: issue.issueUrl,
              title: issueData.title,
              labels: issueData.labels
            });
            
            results.push({
              finding,
              success: true,
              issueNumber: issue.issueNumber,
              issueUrl: issue.issueUrl
            });
            
            createdCount++;
          } else {
            results.push({
              finding,
              success: false,
              error: issue.error
            });
            
            errorCount++;
          }
        }
      } catch (error) {
        console.error('Error creating GitHub issue:', error.message);
        
        results.push({
          finding,
          success: false,
          error: error.message
        });
        
        errorCount++;
      }
      
      // Add a small delay between issue creation to avoid rate limiting
      if (!this.config.dryRun) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
    
    return {
      success: true,
      results,
      summary: {
        total: filteredFindings.length,
        created: createdCount,
        duplicates: duplicateCount,
        errors: errorCount
      }
    };
  }
  
  formatFinding(finding) {
    // Format a finding into an issue
    let title;
    let body;
    let labels = [this.config.labelPrefix];
    
    // Add priority label
    labels.push(`${this.config.labelPrefix}:priority:${finding.priority.toLowerCase()}`);
    
    // Add source-specific labels and format title/body
    if (finding.source === 'file') {
      labels.push(`${this.config.labelPrefix}:file`);
      title = this.createFileIssueTitle(finding);
      body = this.createFileIssueBody(finding);
    } else {
      labels.push(`${this.config.labelPrefix}:repository`);
      title = this.createRepositoryIssueTitle(finding);
      body = this.createRepositoryIssueBody(finding);
    }
    
    // Add type label based on finding content
    const type = this.detectFindingType(finding);
    labels.push(`${this.config.labelPrefix}:${type.toLowerCase()}`);
    
    return {
      title,
      body,
      labels
    };
  }
  
  createFileIssueTitle(finding) {
    // Create a title for a file-specific issue
    let title = finding.title;
    
    // Add file path if available
    if (finding.filePath) {
      const shortPath = this.shortenPath(finding.filePath);
      title = `[${shortPath}] ${title}`;
    }
    
    // Add priority prefix for high-priority issues
    if (finding.priority === 'Critical' || finding.priority === 'High') {
      title = `[${finding.priority}] ${title}`;
    }
    
    return title;
  }
  
  createRepositoryIssueTitle(finding) {
    // Create a title for a repository-level issue
    let title = finding.title;
    
    // Add priority prefix for high-priority issues
    if (finding.priority === 'Critical' || finding.priority === 'High') {
      title = `[${finding.priority}] ${title}`;
    }
    
    return title;
  }
  
  shortenPath(filePath) {
    // Shorten file path to make it more readable
    const parts = filePath.split('/');
    if (parts.length <= 2) return filePath;
    
    // Keep the last two parts
    return `.../${parts[parts.length - 2]}/${parts[parts.length - 1]}`;
  }
  
  createFileIssueBody(finding) {
    // Create a body for a file-specific issue
    return `
## Issue Description

${finding.description}

## Location

File: \`${finding.filePath}\`
${finding.location ? `Location: ${finding.location}` : ''}

## Suggested Solution

${finding.suggestion}

## Priority

**${finding.priority}**

---
*This issue was automatically generated by the Repository Analysis Agent.*
    `.trim();
  }
  
  createRepositoryIssueBody(finding) {
    // Create a body for a repository-level issue
    return `
## Issue Description

${finding.description}

## Affected Area

${finding.area}

## Suggested Solution

${finding.suggestion}

## Priority

**${finding.priority}**

---
*This issue was automatically generated by the Repository Analysis Agent.*
    `.trim();
  }
  
  detectFindingType(finding) {
    const title = finding.title.toLowerCase();
    const description = finding.description ? finding.description.toLowerCase() : '';
    
    if (title.includes('bug') || description.includes('bug') || 
        title.includes('error') || description.includes('error')) {
      return 'Bug';
    } else if (title.includes('security') || description.includes('security') ||
               title.includes('vulnerability') || description.includes('vulnerability')) {
      return 'Security';
    } else if (title.includes('performance') || description.includes('performance')) {
      return 'Performance';
    } else if (title.includes('documentation') || description.includes('documentation')) {
      return 'Documentation';
    } else if (title.includes('refactor') || description.includes('refactor') ||
               title.includes('code smell') || description.includes('code smell')) {
      return 'Refactoring';
    } else if (title.includes('feature') || description.includes('feature') ||
               title.includes('enhancement') || description.includes('enhancement')) {
      return 'Enhancement';
    } else {
      return 'Other';
    }
  }
  
  async createIssue(owner, repo, issueData) {
    if (!this.githubInitialized) {
      return { success: false, error: 'GitHub client not initialized' };
    }
    
    try {
      // In a real implementation, we would call the GitHub API here
      // For now, we'll return a mock response
      
      // Mock implementation with a delay to simulate API call
      await new Promise(resolve => setTimeout(resolve, 100));
      
      return {
        success: true,
        issueNumber: Math.floor(Math.random() * 1000) + 1,
        issueUrl: `https://github.com/${owner}/${repo}/issues/${Math.floor(Math.random() * 1000) + 1}`
      };
    } catch (error) {
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
      // In a real implementation, we would call the GitHub API here
      // For now, we'll return a mock response
      
      // Mock implementation with a delay to simulate API call
      await new Promise(resolve => setTimeout(resolve, 50));
      
      // Always return false for testing
      return false;
    } catch (error) {
      console.error('Error checking for duplicate issues:', error.message);
      return false; // Assume no duplicates if check fails
    }
  }
  
  calculateTitleSimilarity(title1, title2) {
    // Simple Jaccard similarity for titles
    const words1 = new Set(title1.toLowerCase().split(/\s+/));
    const words2 = new Set(title2.toLowerCase().split(/\s+/));
    
    const intersection = new Set([...words1].filter(word => words2.has(word)));
    const union = new Set([...words1, ...words2]);
    
    return intersection.size / union.size;
  }
  
  async recordCreatedIssue(repositoryId, issueData) {
    if (!this.storageManager) {
      return false;
    }
    
    try {
      // Get existing issues for this repository
      const existingIssues = await this.getRepositoryIssues(repositoryId);
      
      // Add the new issue
      existingIssues.push({
        issueNumber: issueData.issueNumber,
        issueUrl: issueData.issueUrl,
        title: issueData.title,
        createdAt: new Date().toISOString(),
        labels: issueData.labels
      });
      
      // Save updated issues
      await this.storageManager.saveData(`issues/${repositoryId}`, existingIssues);
      
      return true;
    } catch (error) {
      console.error('Error recording created issue:', error.message);
      return false;
    }
  }
  
  async getRepositoryIssues(repositoryId) {
    if (!this.storageManager) {
      return [];
    }
    
    try {
      return await this.storageManager.loadData(`issues/${repositoryId}`) || [];
    } catch (error) {
      console.error('Error loading repository issues:', error.message);
      return [];
    }
  }
  
  async getIssueStats() {
    if (!this.storageManager) {
      return {
        totalIssues: 0,
        issuesByRepository: {},
        issuesByPriority: {
          Critical: 0,
          High: 0,
          Medium: 0,
          Low: 0
        },
        issuesByLabel: {}
      };
    }
    
    try {
      // Get all repository IDs
      const repositoryIds = await this.storageManager.listDataKeys('issues');
      
      // Collect stats for each repository
      const stats = {
        totalIssues: 0,
        issuesByRepository: {},
        issuesByPriority: {
          Critical: 0,
          High: 0,
          Medium: 0,
          Low: 0
        },
        issuesByLabel: {}
      };
      
      // Process each repository
      for (const repoId of repositoryIds) {
        const issues = await this.getRepositoryIssues(repoId);
        
        stats.totalIssues += issues.length;
        stats.issuesByRepository[repoId] = issues.length;
        
        // Count by priority and label
        issues.forEach(issue => {
          if (!issue.labels) return;
          
          // Count by label
          issue.labels.forEach(label => {
            stats.issuesByLabel[label] = (stats.issuesByLabel[label] || 0) + 1;
            
            // Count by priority
            if (label.includes('priority:')) {
              const priority = label.replace(/.*priority:/, '');
              const normalizedPriority = priority.charAt(0).toUpperCase() + priority.slice(1);
              if (stats.issuesByPriority[normalizedPriority] !== undefined) {
                stats.issuesByPriority[normalizedPriority]++;
              }
            }
          });
        });
      }
      
      return stats;
    } catch (error) {
      console.error('Error getting issue stats:', error.message);
      return {
        totalIssues: 0,
        issuesByRepository: {},
        issuesByPriority: {
          Critical: 0,
          High: 0,
          Medium: 0,
          Low: 0
        },
        issuesByLabel: {}
      };
    }
  }
}

module.exports = IssueManagementSystem;