import * as vscode from 'vscode';
import {
  ApiService,
  ApiServiceConfig,
  DraftRequest,
  AnalyzeGrammarStyleRequest,
  SummarizeRequest,
  AdjustToneRequest,
  TextTone,
  SummaryFormat,
  RequestFactory
} from 'writing-assistant-connector';

// This method is called when the extension is activated
export function activate(context: vscode.ExtensionContext) {
  console.log('Writing Assistant extension is now active');

  // Initialize the API service
  const apiService = initializeApiService();

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

  // Add commands to the extension context
  context.subscriptions.push(draftCommand);
  context.subscriptions.push(analyzeCommand);
  context.subscriptions.push(summarizeCommand);
  context.subscriptions.push(adjustToneCommand);
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

// Show the result in a new editor
function showResultInNewEditor(title: string, content: string): void {
  vscode.workspace.openTextDocument({ content }).then(document => {
    vscode.window.showTextDocument(document, { preview: false });
    vscode.languages.setTextDocumentLanguage(document, 'markdown');
  });
}

// Handle the Draft command
async function handleDraftCommand(apiService: ApiService): Promise<void> {
  try {
    // Get prompt from user
    const prompt = await vscode.window.showInputBox({
      prompt: 'Enter a prompt for the AI to draft text',
      placeHolder: 'Write a paragraph about...'
    });

    if (!prompt) {
      return; // User cancelled
    }

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

        // Create request
        const request = RequestFactory.createDraftRequest(prompt, {
          model: preferredModel,
          temperature: 0.7
        });

        // Get context from selected text if any
        const selectedText = getSelectedText();
        if (selectedText) {
          request.context = selectedText;
        }

        // Generate draft
        const response = await apiService.generateDraft(request);

        // Show result in new editor
        showResultInNewEditor('AI Draft', response.text);
      }
    );
  } catch (error) {
    vscode.window.showErrorMessage(`Error generating draft: ${error instanceof Error ? error.message : String(error)}`);
  }
}

// Handle the Analyze Grammar & Style command
async function handleAnalyzeCommand(apiService: ApiService): Promise<void> {
  try {
    const text = getSelectedText();
    if (!text) {
      vscode.window.showWarningMessage('Please select some text to analyze.');
      return;
    }

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

        // Create request
        const request = RequestFactory.createAnalyzeGrammarStyleRequest(text, {
          model: preferredModel,
          check_grammar: true,
          check_style: true,
          check_spelling: true
        });

        // Analyze text
        const response = await apiService.analyzeGrammarStyle(request);

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
      }
    );
  } catch (error) {
    vscode.window.showErrorMessage(`Error analyzing text: ${error instanceof Error ? error.message : String(error)}`);
  }
}

// Handle the Summarize command
async function handleSummarizeCommand(apiService: ApiService): Promise<void> {
  try {
    const text = getSelectedText();
    if (!text) {
      vscode.window.showWarningMessage('Please select some text to summarize.');
      return;
    }

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
      return; // User cancelled
    }

    const format = selectedFormat.value;

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

        // Create request
        const request = RequestFactory.createSummarizeRequest(text, {
          model: preferredModel,
          format: format
        });

        // Summarize text
        const response = await apiService.summarize(request);

        // Show result in new editor
        showResultInNewEditor('Summary', response.summary);
      }
    );
  } catch (error) {
    vscode.window.showErrorMessage(`Error summarizing text: ${error instanceof Error ? error.message : String(error)}`);
  }
}

// Handle the Adjust Tone command
async function handleAdjustToneCommand(apiService: ApiService): Promise<void> {
  try {
    const text = getSelectedText();
    if (!text) {
      vscode.window.showWarningMessage('Please select some text to adjust the tone of.');
      return;
    }

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
      return; // User cancelled
    }

    const targetTone = selectedTone.value;

    // Show progress
    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: `Adjusting tone to ${selectedTone}...`,
        cancellable: true
      },
      async () => {
        // Get configuration
        const preferredModel = config.get<string>('preferredModel');

        // Create request
        const request = RequestFactory.createAdjustToneRequest(text, targetTone, {
          model: preferredModel,
          preserve_meaning: true
        });

        // Adjust tone
        const response = await apiService.adjustTone(request);

        // Ask if user wants to replace the selected text
        const action = await vscode.window.showInformationMessage(
          'Tone adjusted successfully. What would you like to do?',
          'Replace Selected Text',
          'Show in New Editor'
        );

        if (action === 'Replace Selected Text') {
          replaceSelectedText(response.adjusted_text);
        } else {
          // Show result in new editor
          showResultInNewEditor('Adjusted Text', response.adjusted_text);
        }
      }
    );
  } catch (error) {
    vscode.window.showErrorMessage(`Error adjusting tone: ${error instanceof Error ? error.message : String(error)}`);
  }
}
