# Contributing to FreshRSS MCP Server

Thank you for considering contributing to the FreshRSS MCP Server! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

Before submitting a bug report:

- Check the issue tracker to see if the problem has already been reported
- Ensure you're using the latest version
- Collect relevant information about the issue (error messages, steps to reproduce, etc.)

When submitting a bug report, please include:

1. The version of the software you're using
2. Your operating system and version
3. Detailed steps to reproduce the problem
4. Expected behavior and what went wrong
5. Any error messages or logs (make sure to redact sensitive information)

### Suggesting Enhancements

Enhancement suggestions are welcome! When submitting an enhancement suggestion, please include:

1. A clear and descriptive title
2. A detailed explanation of the proposed functionality
3. Any potential implementation details you can think of
4. Why this enhancement would be useful to users

### Pull Requests

1. Fork the repository
2. Create a new branch from `main`
3. Make your changes
4. Run tests and ensure they pass
5. Submit a pull request

#### Pull Request Guidelines

- Follow the existing code style and conventions
- Update documentation if needed
- Add tests for new features
- Make sure all existing tests pass
- Keep your PR focused on a single topic
- Reference any relevant issues

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/freshrss-server.git
   cd freshrss-server
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Build the project:
   ```bash
   npm run build
   ```

### Environment Setup

To test the server, you'll need:

1. A running FreshRSS instance
2. API credentials for that instance

Create a `.env` file in the root directory with:

```
FRESHRSS_API_URL=https://your-freshrss-instance.com
FRESHRSS_USERNAME=your-username
FRESHRSS_PASSWORD=your-password
```

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes that don't affect code behavior
- `refactor:` for code changes that neither fix bugs nor add features
- `test:` for adding or modifying tests
- `chore:` for routine tasks, maintenance, etc.

For example:
```
feat: add support for category filtering
fix: resolve connection timeout issue
docs: update installation instructions
```

## Questions?

Feel free to open an issue with your question, or reach out to the maintainers.

Thank you for your contributions!
