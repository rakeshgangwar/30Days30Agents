import * as vscode from 'vscode';

/**
 * Manages webview panels for displaying Writing Assistant results
 */
export class ResultPanel {
  public static currentPanel: ResultPanel | undefined;
  private readonly _panel: vscode.WebviewPanel;
  private readonly _extensionUri: vscode.Uri;
  private _disposables: vscode.Disposable[] = [];

  /**
   * Create or show a result panel
   * @param extensionUri The URI of the extension
   * @param title The title of the panel
   * @param content The content to display
   * @param viewType The type of view (used for persistence)
   */
  public static createOrShow(
    extensionUri: vscode.Uri,
    title: string,
    content: string,
    viewType: string = 'writing-assistant.result'
  ): ResultPanel {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    // If we already have a panel, show it
    if (ResultPanel.currentPanel) {
      ResultPanel.currentPanel._panel.reveal(column);
      ResultPanel.currentPanel.update(title, content);
      return ResultPanel.currentPanel;
    }

    // Otherwise, create a new panel
    const panel = vscode.window.createWebviewPanel(
      viewType,
      title,
      column || vscode.ViewColumn.One,
      {
        // Enable JavaScript in the webview
        enableScripts: true,
        // Restrict the webview to only load resources from the extension
        localResourceRoots: [extensionUri]
      }
    );

    ResultPanel.currentPanel = new ResultPanel(panel, extensionUri, title, content);
    return ResultPanel.currentPanel;
  }

  /**
   * Create a new result panel
   * @param panel The webview panel
   * @param extensionUri The URI of the extension
   * @param title The title of the panel
   * @param content The content to display
   */
  private constructor(
    panel: vscode.WebviewPanel,
    extensionUri: vscode.Uri,
    title: string,
    content: string
  ) {
    this._panel = panel;
    this._extensionUri = extensionUri;

    // Set the webview's initial html content
    this.update(title, content);

    // Listen for when the panel is disposed
    // This happens when the user closes the panel or when the panel is closed programmatically
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

    // Handle messages from the webview
    this._panel.webview.onDidReceiveMessage(
      message => {
        switch (message.command) {
          case 'copyToClipboard':
            vscode.env.clipboard.writeText(message.text);
            vscode.window.showInformationMessage('Copied to clipboard');
            return;
          case 'insertIntoEditor':
            const editor = vscode.window.activeTextEditor;
            if (editor) {
              editor.edit(editBuilder => {
                editBuilder.replace(editor.selection, message.text);
              });
              vscode.window.showInformationMessage('Text inserted into editor');
            }
            return;
        }
      },
      null,
      this._disposables
    );
  }

  /**
   * Update the content of the panel
   * @param title The title of the panel
   * @param content The content to display
   */
  public update(title: string, content: string): void {
    this._panel.title = title;
    this._panel.webview.html = this._getHtmlForWebview(title, content);
  }

  /**
   * Dispose of the panel
   */
  public dispose(): void {
    ResultPanel.currentPanel = undefined;

    // Clean up our resources
    this._panel.dispose();

    while (this._disposables.length) {
      const x = this._disposables.pop();
      if (x) {
        x.dispose();
      }
    }
  }

  /**
   * Generate the HTML for the webview
   * @param title The title of the panel
   * @param content The content to display
   * @returns The HTML for the webview
   */
  private _getHtmlForWebview(title: string, content: string): string {
    // Convert markdown to HTML (simple version)
    const htmlContent = this._markdownToHtml(content);

    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${title}</title>
        <style>
            body {
                font-family: var(--vscode-editor-font-family);
                font-size: var(--vscode-editor-font-size);
                color: var(--vscode-editor-foreground);
                background-color: var(--vscode-editor-background);
                padding: 20px;
                line-height: 1.6;
            }
            h1 {
                color: var(--vscode-titleBar-activeForeground);
                border-bottom: 1px solid var(--vscode-panel-border);
                padding-bottom: 10px;
            }
            h2, h3 {
                color: var(--vscode-titleBar-activeForeground);
                margin-top: 20px;
            }
            pre {
                background-color: var(--vscode-textCodeBlock-background);
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
            }
            code {
                font-family: var(--vscode-editor-font-family);
                background-color: var(--vscode-textCodeBlock-background);
                padding: 2px 5px;
                border-radius: 3px;
            }
            .actions {
                margin-top: 20px;
                display: flex;
                gap: 10px;
            }
            button {
                background-color: var(--vscode-button-background);
                color: var(--vscode-button-foreground);
                border: none;
                padding: 8px 12px;
                cursor: pointer;
                border-radius: 3px;
            }
            button:hover {
                background-color: var(--vscode-button-hoverBackground);
            }
        </style>
    </head>
    <body>
        <h1>${title}</h1>
        <div class="content">
            ${htmlContent}
        </div>
        <div class="actions">
            <button id="copyBtn">Copy to Clipboard</button>
            <button id="insertBtn">Insert into Editor</button>
        </div>
        <script>
            const vscode = acquireVsCodeApi();
            const copyBtn = document.getElementById('copyBtn');
            const insertBtn = document.getElementById('insertBtn');
            const content = document.querySelector('.content').innerText;
            
            copyBtn.addEventListener('click', () => {
                vscode.postMessage({
                    command: 'copyToClipboard',
                    text: content
                });
            });
            
            insertBtn.addEventListener('click', () => {
                vscode.postMessage({
                    command: 'insertIntoEditor',
                    text: content
                });
            });
        </script>
    </body>
    </html>`;
  }

  /**
   * Convert markdown to HTML (simple version)
   * @param markdown The markdown to convert
   * @returns The HTML
   */
  private _markdownToHtml(markdown: string): string {
    // This is a very simple markdown to HTML converter
    // In a real extension, you would use a proper markdown library
    let html = markdown
      // Headers
      .replace(/^# (.*$)/gm, '<h1>$1</h1>')
      .replace(/^## (.*$)/gm, '<h2>$1</h2>')
      .replace(/^### (.*$)/gm, '<h3>$1</h3>')
      // Bold
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Italic
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // Code blocks
      .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
      // Inline code
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      // Lists
      .replace(/^\* (.*$)/gm, '<ul><li>$1</li></ul>')
      .replace(/^- (.*$)/gm, '<ul><li>$1</li></ul>')
      // Paragraphs
      .replace(/^\s*$/gm, '</p><p>');

    // Wrap in paragraphs
    html = '<p>' + html + '</p>';
    // Fix duplicate paragraph tags
    html = html.replace(/<\/p><p><\/p><p>/g, '</p><p>');
    
    return html;
  }
}
