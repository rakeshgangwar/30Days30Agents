import * as vscode from 'vscode';
import {
  ApiService,
  ApiServiceConfig,
  TextTone,
  SummaryFormat,
  RequestFactory
} from 'writing-assistant-connector';
import { StatusBarManager } from './statusBar';
import { ResultPanel } from './webviewPanel';
import { PreferencesManager } from './preferencesManager';
import { PreferencesPanel } from './preferencesPanel';
import { Logger, LogLevel } from './logger';

// This method is called when the extension is activated
export function activate(context: vscode.ExtensionContext) {
  // Initialize logger
  const logger = Logger.getInstance();

  // Set log level based on configuration
  const config = vscode.workspace.getConfiguration('writingAssistant');
  const debugMode = config.get<boolean>('debugMode') || false;
  logger.setLogLevel(debugMode ? LogLevel.DEBUG : LogLevel.INFO);

  logger.info('Writing Assistant extension is now active');

  // Initialize the API service
  const apiService = initializeApiService();
  logger.debug('API service initialized', {
    baseUrl: config.get<string>('apiUrl'),
    hasApiKey: !!config.get<string>('apiKey')
  });

  // Initialize the preferences manager
  const preferencesManager = new PreferencesManager(apiService, context);
  logger.debug('Preferences manager initialized', {
    userId: preferencesManager.getUserId()
  });

  // Create status bar item
  const statusBarManager = new StatusBarManager(apiService);
  context.subscriptions.push(statusBarManager);
  logger.debug('Status bar manager initialized');

  // Register commands
  const draftCommand = vscode.commands.registerCommand('writing-assistant.draft', async () => {
    await handleDraftCommand(apiService);
  });

  const analyzeCommand = vscode.commands.registerCommand('writing-assistant.analyzeGrammarStyle', async () => {
    await handleAnalyzeCommand(apiService);
  });

  const summarizeCommand = vscode.commands.registerCommand('writing-assistant.summarize', async () => {
    await handleSummarizeCommand(apiService);
  });

  const adjustToneCommand = vscode.commands.registerCommand('writing-assistant.adjustTone', async () => {
    await handleAdjustToneCommand(apiService);
  });

  // Register preferences command
  const preferencesCommand = vscode.commands.registerCommand('writing-assistant.preferences', () => {
    PreferencesPanel.createOrShow(context.extensionUri, preferencesManager);
  });

  // Register panel command
  const showPanelCommand = vscode.commands.registerCommand('writing-assistant.showPanel', () => {
    // Create a welcome panel with information about the extension
    const content = `
# Writing Assistant

Welcome to the Writing Assistant extension for VS Code!

## Available Commands

- **Draft with AI**: Generate text based on a prompt
- **Analyze Grammar & Style**: Check your text for grammar, style, and spelling issues
- **Summarize Text**: Create concise summaries of your text
- **Adjust Tone**: Change the tone of your text
- **Preferences**: Configure your Writing Assistant settings

## How to Use

1. Select text in your editor (or leave empty to use the entire document)
2. Right-click and select a command from the "Writing Assistant" menu
3. Or use the toolbar buttons at the top of the editor
4. Or use keyboard shortcuts:
   - Draft: Ctrl+Alt+D (Cmd+Alt+D on Mac)
   - Analyze: Ctrl+Alt+A (Cmd+Alt+A on Mac)
   - Summarize: Ctrl+Alt+S (Cmd+Alt+S on Mac)
   - Adjust Tone: Ctrl+Alt+T (Cmd+Alt+T on Mac)

## User Preferences

You can set your preferences by running the "Writing Assistant: Preferences" command.
This allows you to:
- Set your user ID to sync preferences across devices
- Choose your preferred LLM model
- Set your default tone for text adjustments
`;
    ResultPanel.createOrShow(context.extensionUri, 'Writing Assistant', content, 'writing-assistant.welcome');
  });

  // Try to sync preferences on startup
  preferencesManager.syncWithVSCodeSettings().catch(error => {
    console.error('Failed to sync preferences on startup:', error);
  });

  // Add commands to the extension context
  context.subscriptions.push(draftCommand);
  context.subscriptions.push(analyzeCommand);
  context.subscriptions.push(summarizeCommand);
  context.subscriptions.push(adjustToneCommand);
  context.subscriptions.push(preferencesCommand);
  context.subscriptions.push(showPanelCommand);
}

// This method is called when the extension is deactivated
export function deactivate() {
  console.log('Writing Assistant extension is now deactivated');
}

// Initialize the API service with configuration from settings
function initializeApiService(): ApiService {
  const config = vscode.workspace.getConfiguration('writingAssistant');
  const apiServiceConfig: ApiServiceConfig = {
    baseUrl: config.get<string>('apiUrl') || 'http://localhost:8000',
    apiKey: config.get<string>('apiKey') || '',
    timeout: 60000, // 60 seconds
    maxRetries: 3,
    retryDelay: 1000
  };

  return new ApiService(apiServiceConfig);
}

// Get the selected text or the entire document if nothing is selected
function getSelectedText(): string {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    return '';
  }

  const selection = editor.selection;
  if (selection.isEmpty) {
    // No text selected, get the entire document
    const document = editor.document;
    return document.getText();
  } else {
    // Return the selected text
    return editor.document.getText(selection);
  }
}

// Replace the selected text or insert at cursor position
function replaceSelectedText(text: string): void {
  const editor = vscode.window.activeTextEditor;
  if (!editor) {
    return;
  }

  const selection = editor.selection;
  editor.edit(editBuilder => {
    editBuilder.replace(selection, text);
  });
}

// Show the result in a new editor or webview panel
function showResultInNewEditor(title: string, content: string): void {
  const logger = Logger.getInstance();

  // Get user preference for display mode
  const config = vscode.workspace.getConfiguration('writingAssistant');
  const displayMode = config.get<string>('resultDisplayMode') || 'editor';

  logger.debug('Showing result', { title, displayMode, contentLength: content.length });

  if (displayMode === 'webview') {
    // Show in webview panel
    logger.debug('Using webview panel for display');
    ResultPanel.createOrShow(vscode.Uri.file(__dirname), title, content);
  } else {
    // Show in text editor (default)
    logger.debug('Using text editor for display');
    try {
      vscode.workspace.openTextDocument({ content }).then(document => {
        vscode.window.showTextDocument(document, { preview: false }).then(editor => {
          // Use the title to set the document language and for display purposes
          vscode.languages.setTextDocumentLanguage(document, 'markdown');

          // If we wanted to set the editor title, we would need a custom editor
          // For now, we'll just use the title in the content
          if (title && !content.startsWith('# ')) {
            // Insert title at the beginning if it doesn't already have a title
            editor.edit(editBuilder => {
              editBuilder.insert(new vscode.Position(0, 0), `# ${title}\n\n`);
            });
          }
        });
      });
    } catch (error) {
      logger.error('Error showing result in editor', error);
      vscode.window.showErrorMessage(`Error showing result: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
}

// Handle the Draft command
async function handleDraftCommand(apiService: ApiService): Promise<void> {
  const logger = Logger.getInstance();
  logger.debug('Draft command triggered');

  try {
    // Get prompt from user
    const prompt = await vscode.window.showInputBox({
      prompt: 'Enter a prompt for the AI to draft text',
      placeHolder: 'Write a paragraph about...'
    });

    if (!prompt) {
      logger.debug('Draft command cancelled - no prompt provided');
      return; // User cancelled
    }

    logger.info(`Generating draft with prompt: "${prompt.substring(0, 50)}${prompt.length > 50 ? '...' : ''}"`);

    // Show progress
    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: 'Generating draft...',
        cancellable: true
      },
      async () => {
        // Get configuration
        const config = vscode.workspace.getConfiguration('writingAssistant');
        const preferredModel = config.get<string>('preferredModel');
        logger.debug('Using model', { model: preferredModel });

        // Create request
        const request = RequestFactory.createDraftRequest(prompt, {
          model: preferredModel,
          temperature: 0.7
        });

        // Get context from selected text if any
        const selectedText = getSelectedText();
        if (selectedText) {
          logger.debug(`Using selected text as context (${selectedText.length} characters)`);
          request.context = selectedText;
        }

        // Generate draft
        logger.debug('Sending draft request to API', { requestId: 'draft-' + Date.now() });
        const response = await apiService.generateDraft(request);
        logger.debug('Received draft response', {
          model: response.model_used,
          textLength: response.text.length
        });

        // Show result in new editor
        showResultInNewEditor('AI Draft', response.text);
        logger.info('Draft generated successfully');
      }
    );
  } catch (error) {
    logger.error('Error generating draft', error);
    vscode.window.showErrorMessage(`Error generating draft: ${error instanceof Error ? error.message : String(error)}`);
  }
}

// Handle the Analyze Grammar & Style command
async function handleAnalyzeCommand(apiService: ApiService): Promise<void> {
  const logger = Logger.getInstance();
  logger.debug('Analyze Grammar & Style command triggered');

  try {
    const text = getSelectedText();
    if (!text) {
      logger.debug('Analyze command cancelled - no text selected');
      vscode.window.showWarningMessage('Please select some text to analyze.');
      return;
    }

    logger.info(`Analyzing text (${text.length} characters)`);

    // Show progress
    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: 'Analyzing text...',
        cancellable: true
      },
      async () => {
        // Get configuration
        const config = vscode.workspace.getConfiguration('writingAssistant');
        const preferredModel = config.get<string>('preferredModel');
        logger.debug('Using model', { model: preferredModel });

        // Create request
        const request = RequestFactory.createAnalyzeGrammarStyleRequest(text, {
          model: preferredModel,
          check_grammar: true,
          check_style: true,
          check_spelling: true
        });

        // Analyze text
        logger.debug('Sending analyze request to API', { requestId: 'analyze-' + Date.now() });
        const response = await apiService.analyzeGrammarStyle(request);
        logger.debug('Received analyze response', {
          model: response.model_used,
          issuesCount: response.issues.length,
          improvedTextLength: response.improved_text.length
        });

        // Format results
        let resultContent = '# Grammar & Style Analysis\n\n';
        resultContent += `**Issues Found:** ${response.issues.length}\n\n`;

        if (response.issues.length > 0) {
          resultContent += '## Issues\n\n';
          response.issues.forEach((issue, index) => {
            resultContent += `### Issue ${index + 1}: ${issue.type} (${issue.severity})\n`;
            resultContent += `**Description:** ${issue.description}\n`;
            resultContent += `**Suggestion:** ${issue.suggestion}\n\n`;
          });
        }

        resultContent += '## Improved Text\n\n';
        resultContent += response.improved_text;

        // Show result in new editor
        showResultInNewEditor('Grammar & Style Analysis', resultContent);
        logger.info(`Analysis completed with ${response.issues.length} issues found`);
      }
    );
  } catch (error) {
    logger.error('Error analyzing text', error);
    vscode.window.showErrorMessage(`Error analyzing text: ${error instanceof Error ? error.message : String(error)}`);
  }
}

// Handle the Summarize command
async function handleSummarizeCommand(apiService: ApiService): Promise<void> {
  const logger = Logger.getInstance();
  logger.debug('Summarize command triggered');

  try {
    const text = getSelectedText();
    if (!text) {
      logger.debug('Summarize command cancelled - no text selected');
      vscode.window.showWarningMessage('Please select some text to summarize.');
      return;
    }

    logger.info(`Summarizing text (${text.length} characters)`);

    // Ask for format
    const formatOptions = [
      { label: 'Paragraph', value: SummaryFormat.PARAGRAPH },
      { label: 'Bullet Points', value: SummaryFormat.BULLETS }
    ];

    const selectedFormat = await vscode.window.showQuickPick(
      formatOptions,
      { placeHolder: 'Select summary format' }
    );

    if (!selectedFormat) {
      logger.debug('Summarize command cancelled - no format selected');
      return; // User cancelled
    }

    const format = selectedFormat.value;
    logger.debug('Selected format', { format: selectedFormat.label });

    // Show progress
    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: 'Summarizing text...',
        cancellable: true
      },
      async () => {
        // Get configuration
        const config = vscode.workspace.getConfiguration('writingAssistant');
        const preferredModel = config.get<string>('preferredModel');
        logger.debug('Using model', { model: preferredModel });

        // Create request
        const request = RequestFactory.createSummarizeRequest(text, {
          model: preferredModel,
          format: format
        });

        // Summarize text
        logger.debug('Sending summarize request to API', { requestId: 'summarize-' + Date.now() });
        const response = await apiService.summarize(request);
        logger.debug('Received summarize response', {
          model: response.model_used,
          summaryLength: response.summary.length
        });

        // Show result in new editor
        showResultInNewEditor('Summary', response.summary);
        logger.info('Summary generated successfully');
      }
    );
  } catch (error) {
    logger.error('Error summarizing text', error);
    vscode.window.showErrorMessage(`Error summarizing text: ${error instanceof Error ? error.message : String(error)}`);
  }
}

// Handle the Adjust Tone command
async function handleAdjustToneCommand(apiService: ApiService): Promise<void> {
  const logger = Logger.getInstance();
  logger.debug('Adjust Tone command triggered');

  try {
    const text = getSelectedText();
    if (!text) {
      logger.debug('Adjust Tone command cancelled - no text selected');
      vscode.window.showWarningMessage('Please select some text to adjust the tone of.');
      return;
    }

    logger.info(`Adjusting tone of text (${text.length} characters)`);

    // Get available tones
    const toneOptions = [
      { label: 'Professional', value: TextTone.PROFESSIONAL },
      { label: 'Casual', value: TextTone.CASUAL },
      { label: 'Friendly', value: TextTone.FRIENDLY },
      { label: 'Formal', value: TextTone.FORMAL },
      { label: 'Academic', value: TextTone.ACADEMIC },
      { label: 'Technical', value: TextTone.TECHNICAL },
      { label: 'Persuasive', value: TextTone.PERSUASIVE },
      { label: 'Enthusiastic', value: TextTone.ENTHUSIASTIC },
      { label: 'Confident', value: TextTone.CONFIDENT },
      { label: 'Empathetic', value: TextTone.EMPATHETIC }
    ];

    // Get configuration
    const config = vscode.workspace.getConfiguration('writingAssistant');

    // Ask for target tone
    const selectedTone = await vscode.window.showQuickPick(
      toneOptions,
      {
        placeHolder: 'Select target tone'
      }
    );

    if (!selectedTone) {
      logger.debug('Adjust Tone command cancelled - no tone selected');
      return; // User cancelled
    }

    const targetTone = selectedTone.value;
    logger.debug('Selected tone', { tone: selectedTone.label });

    // Show progress
    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: `Adjusting tone to ${selectedTone.label}...`,
        cancellable: true
      },
      async () => {
        // Get configuration
        const preferredModel = config.get<string>('preferredModel');
        logger.debug('Using model', { model: preferredModel });

        // Create request
        const request = RequestFactory.createAdjustToneRequest(text, targetTone, {
          model: preferredModel,
          preserve_meaning: true
        });

        // Adjust tone
        logger.debug('Sending adjust tone request to API', { requestId: 'adjust-tone-' + Date.now() });
        const response = await apiService.adjustTone(request);
        logger.debug('Received adjust tone response', {
          model: response.model_used,
          adjustedTextLength: response.adjusted_text.length
        });

        // Ask if user wants to replace the selected text
        const action = await vscode.window.showInformationMessage(
          'Tone adjusted successfully. What would you like to do?',
          'Replace Selected Text',
          'Show in New Editor'
        );

        if (action === 'Replace Selected Text') {
          logger.debug('Replacing selected text with adjusted text');
          replaceSelectedText(response.adjusted_text);
        } else {
          logger.debug('Showing adjusted text in new editor');
          // Show result in new editor
          showResultInNewEditor('Adjusted Text', response.adjusted_text);
        }

        logger.info(`Tone adjusted successfully to ${selectedTone.label}`);
      }
    );
  } catch (error) {
    logger.error('Error adjusting tone', error);
    vscode.window.showErrorMessage(`Error adjusting tone: ${error instanceof Error ? error.message : String(error)}`);
  }
}
