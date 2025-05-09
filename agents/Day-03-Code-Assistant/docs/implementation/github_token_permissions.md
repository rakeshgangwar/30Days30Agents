# GitHub Token Permissions

This document provides information about the GitHub token permissions required for the Repository Analysis and Issue Creation Agent.

## Table of Contents

1. [Overview](#overview)
2. [Required Permissions](#required-permissions)
3. [Creating a GitHub Token](#creating-a-github-token)
4. [Security Considerations](#security-considerations)
5. [Token Management](#token-management)

## Overview

The Repository Analysis and Issue Creation Agent requires a GitHub token to:

1. Clone repositories for analysis
2. Create issues based on analysis findings
3. Check for existing issues to avoid duplicates
4. Apply labels to created issues

## Required Permissions

The GitHub token requires the following permissions:

### For Public Repositories Only

If you're only working with public repositories, you need:

- `public_repo`: Access public repositories

### For Private Repositories

If you need to access private repositories, you need:

- `repo`: Full control of private repositories, including:
  - `repo:status`: Access commit status
  - `repo_deployment`: Access deployment status
  - `public_repo`: Access public repositories
  - `repo:invite`: Access repository invitations
  - `security_events`: Read and write security events

### Recommended Scopes

For most users, the following scopes are recommended:

- `repo`: Full control of private repositories (or `public_repo` for public repositories only)
- `read:org`: Read organization membership

## Creating a GitHub Token

To create a GitHub token with the required permissions:

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Click "Generate new token"
3. Give the token a descriptive name (e.g., "Repository Analysis Agent")
4. Select the appropriate scopes (at minimum, select "repo" or "public_repo")
5. Click "Generate token"
6. Copy the token and store it securely

## Security Considerations

GitHub tokens provide access to your GitHub account and repositories. To ensure security:

1. **Limit Permissions**: Only grant the permissions that are absolutely necessary
2. **Secure Storage**: Store the token securely, never commit it to version control
3. **Regular Rotation**: Rotate tokens regularly to limit the impact of potential leaks
4. **Token Expiration**: Consider using tokens with expiration dates
5. **Environment Variables**: Use environment variables to provide tokens to the application
6. **Audit Usage**: Regularly audit token usage in GitHub's security log

## Token Management

The Repository Analysis and Issue Creation Agent manages GitHub tokens as follows:

1. **Storage**: Tokens are stored in the `.credentials.yaml` file in the `config` directory
2. **Environment Variables**: Tokens can be provided via the `GITHUB_TOKEN` environment variable
3. **CLI Configuration**: Tokens can be configured using the CLI command:
   ```
   npm start configure --github-token=<token>
   ```
4. **Usage**: The token is used by the `IssueManagementSystem` component to create issues via the GitHub API

### Token Validation

The agent validates the GitHub token by:

1. Checking if the token is provided
2. Initializing the GitHub client with the token
3. Testing the token with a simple API call

If the token is invalid or missing, the agent will:

1. Log a warning message
2. Continue in "dry run" mode if possible
3. Skip issue creation

## Troubleshooting

If you encounter issues with your GitHub token:

1. **Token Scope**: Ensure the token has the required scopes
2. **Token Validity**: Check if the token has expired
3. **Rate Limiting**: Check if you've hit GitHub's API rate limits
4. **Token Revocation**: Ensure the token hasn't been revoked
5. **Network Issues**: Check for network connectivity problems

For more information about GitHub tokens, see the [GitHub documentation on creating a personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token).
