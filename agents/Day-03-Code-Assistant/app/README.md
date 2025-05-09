# Repository Analysis and Issue Creation Agent

This agent analyzes GitHub repositories and automatically creates issues based on its findings. It leverages AI to identify potential improvements, code quality issues, and feature suggestions. It also allows you to have a conversational interface with your codebase.

## Features

- **Repository Analysis**: Clone and analyze GitHub repositories
- **Code Structure Extraction**: Parse code to understand its structure
- **AI-Powered Insights**: Use AI to identify issues and improvements
- **Automatic Issue Creation**: Generate well-structured GitHub issues
- **Flexible Configuration**: Customize analysis depth and focus areas
- **Talk to Your Repository**: Have a conversational interface with your codebase
- **Web Interface**: User-friendly web interface for repository interaction and issue creation

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

### Web Interface

To start the web interface:

```bash
npm run web
```

Then open your browser to http://localhost:3000 to access the web interface.

### Command Line

To analyze a repository and create issues:

```bash
npm start analyze <owner> <repo>
```

Options:
- `--config`: Path to configuration file
- `--dry-run`: Run analysis without creating issues
- `--output`: Path to output report file

To talk to a repository:

```bash
# Talk to a local repository
npm run talk -- /path/to/repository

# Talk to a GitHub repository
npm run talk -- owner repo-name
```

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
├── public/                # Web interface files
│   ├── index.html         # Main HTML file
│   ├── styles.css         # CSS styles
│   └── app.js             # Client-side JavaScript
├── src/                   # Source code
│   ├── components/        # Core components
│   ├── app.js             # Main application class
│   ├── cli.js             # Command-line interface
│   └── server.js          # Web server
├── config/                # Configuration files
├── parsers/               # Tree-sitter WASM parsers
├── templates/             # Issue and prompt templates
├── storage/               # Storage for conversations, vector databases, etc.
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
- [Talk to Your Repository](../docs/features/talk-to-your-repo.md)
- [Web Interface](../docs/features/web-interface.md)

## License

MIT