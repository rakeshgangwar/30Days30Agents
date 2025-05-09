# Repository Analysis and Issue Creation Agent

This agent analyzes GitHub repositories and automatically creates issues based on its findings. It leverages AI to identify potential improvements, code quality issues, and feature suggestions.

## Features

- **Repository Analysis**: Clone and analyze GitHub repositories
- **Code Structure Extraction**: Parse code to understand its structure
- **AI-Powered Insights**: Use AI to identify issues and improvements
- **Automatic Issue Creation**: Generate well-structured GitHub issues
- **Flexible Configuration**: Customize analysis depth and focus areas

## Installation

1. Clone this repository
2. Install dependencies:

```bash
npm install
```

3. Copy the example environment file and update it with your credentials:

```bash
cp .env.example .env
# Edit .env with your GitHub token and OpenAI API key
```

4. Ensure Tree-sitter WASM parsers are available in the `parsers` directory

## Usage

### Command Line

To analyze a repository and create issues:

```bash
npm start analyze <owner> <repo>
```

Options:
- `--config`: Path to configuration file
- `--dry-run`: Run analysis without creating issues
- `--output`: Path to output report file

To configure the agent:

```bash
npm start configure --github-token=<token> --openai-key=<key>
```

### Configuration

You can configure the agent through:
- Environment variables
- Configuration files (.yaml or .json)
- Command-line arguments

See [Configuration Guide](../docs/configuration_manager.md) for details.

## Development

### Testing

Run tests:

```bash
# Run all tests
npm test

# Run specific test suites
npm run test:unit
npm run test:integration
npm run test:e2e
```

### Project Structure

```
repository-analysis-agent/
├── src/                   # Source code
│   ├── components/        # Core components
│   ├── app.js             # Main application class
│   └── cli.js             # Command-line interface
├── config/                # Configuration files
├── parsers/               # Tree-sitter WASM parsers
├── templates/             # Issue and prompt templates
└── tests/                 # Test suites
```

## Documentation

For more details, see:
- [Implementation Plan](../docs/implementation_plan.md)
- [Testing Strategy](../docs/testing_strategy.md)
- [Integration Guide](../docs/integration_guide.md)
- [Code Analysis Engine](../docs/code_analysis_engine.md)
- [AI Analysis Coordinator](../docs/ai_analysis_coordinator.md)
- [Issue Management System](../docs/issue_management_system.md)
- [Repository Access Layer](../docs/repository_access_layer.md)
- [Configuration Manager](../docs/configuration_manager.md)

## License

MIT