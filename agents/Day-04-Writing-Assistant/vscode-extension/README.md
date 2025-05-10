# Writing Assistant for VS Code

A VS Code extension that integrates with the Writing Assistant service to help improve your writing with AI assistance.

## Features

- **Draft with AI**: Generate text based on a prompt
- **Analyze Grammar & Style**: Check your text for grammar, style, and spelling issues
- **Summarize Text**: Create concise summaries of your text in paragraph or bullet point format
- **Adjust Tone**: Change the tone of your text to match your desired style

## Requirements

- VS Code 1.80.0 or higher
- Running instance of the Writing Assistant backend service

## Extension Settings

This extension contributes the following settings:

* `writingAssistant.apiUrl`: URL of the Writing Assistant API (default: http://localhost:8000)
* `writingAssistant.apiKey`: API key for the Writing Assistant service
* `writingAssistant.preferredModel`: Preferred LLM model to use
* `writingAssistant.defaultTone`: Default tone for text adjustments

## Usage

1. Select text in your editor (or leave unselected to use the entire document)
2. Open the Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
3. Type "Writing Assistant" to see available commands
4. Choose the desired action

## Commands

- `Writing Assistant: Draft with AI` - Generate text based on a prompt
- `Writing Assistant: Analyze Grammar & Style` - Check text for issues
- `Writing Assistant: Summarize Text` - Create a summary of the selected text
- `Writing Assistant: Adjust Tone` - Change the tone of the selected text

## Development

### Building the Extension

1. Install dependencies:
   ```
   npm install
   ```

2. Build the extension:
   ```
   npm run compile
   ```

3. Package the extension:
   ```
   npm run package
   ```

### Running the Extension

1. Press F5 to open a new window with your extension loaded
2. Run a command from the Command Palette

## License

MIT
