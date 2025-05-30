import * as vscode from 'vscode';
import { PreferencesManager } from './preferencesManager';
import { UserPreferences, LLMModel, TextTone, ModelInfo, ApiService } from 'writing-assistant-connector';
import { Logger } from './logger';

/**
 * Manages the preferences webview panel
 */
export class PreferencesPanel {
  public static currentPanel: PreferencesPanel | undefined;
  private readonly _panel: vscode.WebviewPanel;
  private readonly _extensionUri: vscode.Uri;
  private readonly _preferencesManager: PreferencesManager;
  private readonly _apiService: ApiService;
  private _disposables: vscode.Disposable[] = [];
  private _availableModels: ModelInfo[] = [];
  private _modelsLoading: boolean = false;
  private _logger: Logger;

  /**
   * Create or show a preferences panel
   * @param extensionUri The URI of the extension
   * @param preferencesManager The preferences manager
   * @param apiService The API service
   */
  public static createOrShow(
    extensionUri: vscode.Uri,
    preferencesManager: PreferencesManager,
    apiService: ApiService
  ): PreferencesPanel {
    const column = vscode.window.activeTextEditor
      ? vscode.window.activeTextEditor.viewColumn
      : undefined;

    // If we already have a panel, show it
    if (PreferencesPanel.currentPanel) {
      PreferencesPanel.currentPanel._panel.reveal(column);
      return PreferencesPanel.currentPanel;
    }

    // Otherwise, create a new panel
    const panel = vscode.window.createWebviewPanel(
      'writing-assistant.preferences',
      'Writing Assistant Preferences',
      column || vscode.ViewColumn.One,
      {
        // Enable JavaScript in the webview
        enableScripts: true,
        // Restrict the webview to only load resources from the extension
        localResourceRoots: [extensionUri]
      }
    );

    PreferencesPanel.currentPanel = new PreferencesPanel(panel, extensionUri, preferencesManager, apiService);
    return PreferencesPanel.currentPanel;
  }

  /**
   * Create a new preferences panel
   * @param panel The webview panel
   * @param extensionUri The URI of the extension
   * @param preferencesManager The preferences manager
   * @param apiService The API service
   */
  private constructor(
    panel: vscode.WebviewPanel,
    extensionUri: vscode.Uri,
    preferencesManager: PreferencesManager,
    apiService: ApiService
  ) {
    this._panel = panel;
    this._extensionUri = extensionUri;
    this._preferencesManager = preferencesManager;
    this._apiService = apiService;
    this._logger = Logger.getInstance();

    // Fetch available models
    this._fetchModels();

    // Set the webview's initial html content
    this._update();

    // Listen for when the panel is disposed
    // This happens when the user closes the panel or when the panel is closed programmatically
    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

    // Handle messages from the webview
    this._panel.webview.onDidReceiveMessage(
      async message => {
        switch (message.command) {
          case 'savePreferences':
            await this._savePreferences(message.preferences);
            return;
          case 'loadPreferences':
            await this._loadPreferences();
            return;
          case 'setUserId':
            await this._setUserId(message.userId);
            return;
          case 'refreshModels':
            await this._fetchModels(true);
            await this._update();
            return;
        }
      },
      null,
      this._disposables
    );
  }

  /**
   * Fetch available models from the API
   * @param forceRefresh Whether to force a refresh of the cached models
   */
  private async _fetchModels(forceRefresh: boolean = false): Promise<void> {
    if (this._modelsLoading) {
      return;
    }

    this._modelsLoading = true;
    try {
      this._logger.debug('Fetching available models', { forceRefresh });
      this._availableModels = await this._apiService.getAvailableModels(forceRefresh);
      this._logger.debug('Fetched models', { count: this._availableModels.length });
    } catch (error) {
      this._logger.error('Failed to fetch models', error);
      // If API call fails, use the static enum values
      this._availableModels = Object.entries(LLMModel).map(([key, value]) => ({
        id: value,
        name: key,
        provider: value.split('/')[0]
      }));
      this._logger.debug('Using fallback models', { count: this._availableModels.length });
    } finally {
      this._modelsLoading = false;
    }
  }

  /**
   * Update the content of the panel
   */
  private async _update(): Promise<void> {
    // Get current preferences
    let preferences: UserPreferences = {
      preferred_model: undefined,
      default_tone: undefined
    };

    let userId = this._preferencesManager.getUserId();

    try {
      if (userId) {
        preferences = await this._preferencesManager.loadPreferences();
      } else {
        // If no user ID, use VS Code settings
        await this._preferencesManager.syncWithVSCodeSettings();
        preferences = this._preferencesManager.getPreferences() || preferences;
      }
    } catch (error) {
      // If loading fails, use empty preferences
      vscode.window.showErrorMessage(`Failed to load preferences: ${error instanceof Error ? error.message : String(error)}`);
    }

    // Update the webview content
    this._panel.webview.html = this._getHtmlForWebview(userId, preferences);
  }

  /**
   * Save preferences
   * @param preferences The preferences to save
   */
  private async _savePreferences(preferences: UserPreferences): Promise<void> {
    try {
      // Save to backend if we have a user ID
      if (this._preferencesManager.getUserId()) {
        await this._preferencesManager.savePreferences(preferences);
        vscode.window.showInformationMessage('Preferences saved successfully');
      }

      // Always update VS Code settings
      await this._preferencesManager.applyToVSCodeSettings(preferences);
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to save preferences: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Load preferences
   */
  private async _loadPreferences(): Promise<void> {
    try {
      const userId = this._preferencesManager.getUserId();
      if (!userId) {
        // Prompt for user ID if not set
        const newUserId = await this._preferencesManager.promptForUserId();
        if (!newUserId) {
          return; // User cancelled
        }
      }

      // Load preferences from backend
      const preferences = await this._preferencesManager.loadPreferences();

      // Update VS Code settings
      await this._preferencesManager.applyToVSCodeSettings(preferences);

      // Update the webview
      await this._update();

      vscode.window.showInformationMessage('Preferences loaded successfully');
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to load preferences: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Set the user ID
   * @param userId The user ID to set
   */
  private async _setUserId(userId: string): Promise<void> {
    try {
      await this._preferencesManager.setUserId(userId);
      await this._update();
      vscode.window.showInformationMessage(`User ID set to ${userId}`);
    } catch (error) {
      vscode.window.showErrorMessage(`Failed to set user ID: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Dispose of the panel
   */
  public dispose(): void {
    PreferencesPanel.currentPanel = undefined;

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
   * @param userId The current user ID
   * @param preferences The current preferences
   * @returns The HTML for the webview
   */
  private _getHtmlForWebview(userId: string | undefined, preferences: UserPreferences): string {
    // Get available models and tones
    const models = this._availableModels.length > 0
      ? this._availableModels.map(model => ({
          label: model.name || model.id,
          value: model.id,
          provider: model.provider || model.id.split('/')[0]
        }))
      : Object.entries(LLMModel).map(([key, value]) => ({
          label: key,
          value,
          provider: value.split('/')[0]
        }));

    const tones = Object.entries(TextTone).map(([key, value]) => ({ label: key, value }));

    return `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Writing Assistant Preferences</title>
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
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input, select {
                width: 100%;
                padding: 8px;
                background-color: var(--vscode-input-background);
                color: var(--vscode-input-foreground);
                border: 1px solid var(--vscode-input-border);
                border-radius: 3px;
            }
            button {
                background-color: var(--vscode-button-background);
                color: var(--vscode-button-foreground);
                border: none;
                padding: 8px 12px;
                cursor: pointer;
                border-radius: 3px;
                margin-right: 10px;
            }
            button:hover {
                background-color: var(--vscode-button-hoverBackground);
            }
            .actions {
                margin-top: 20px;
                display: flex;
                gap: 10px;
            }
            .user-id-section {
                margin-bottom: 20px;
                padding-bottom: 20px;
                border-bottom: 1px solid var(--vscode-panel-border);
            }
        </style>
    </head>
    <body>
        <h1>Writing Assistant Preferences</h1>

        <div class="user-id-section">
            <div class="form-group">
                <label for="userId">User ID</label>
                <div style="display: flex; gap: 10px;">
                    <input type="text" id="userId" value="${userId || ''}" placeholder="Enter your user ID">
                    <button id="setUserIdBtn">Set User ID</button>
                </div>
                <p style="font-size: 0.9em; color: var(--vscode-descriptionForeground);">
                    Setting a user ID allows your preferences to be stored on the server and used across devices.
                </p>
            </div>
        </div>

        <div class="form-group">
            <label for="preferredModel">Preferred LLM Model</label>
            <div style="display: flex; gap: 10px; margin-bottom: 5px;">
                <select id="preferredModel" style="flex-grow: 1;">
                    <option value="">Default</option>
                    ${(() => {
                        // Group models by provider
                        const groupedModels = models.reduce<Record<string, Array<{label: string, value: string, provider: string}>>>((acc, model) => {
                            const provider = model.provider || 'other';
                            if (!acc[provider]) {
                                acc[provider] = [];
                            }
                            acc[provider].push(model);
                            return acc;
                        }, {});

                        // Generate options with optgroups
                        return Object.entries(groupedModels).map(([provider, providerModels]) => `
                            <optgroup label="${provider}">
                                ${providerModels.map(model => `
                                    <option value="${model.value}" ${preferences.preferred_model === model.value ? 'selected' : ''}>
                                        ${model.label}
                                    </option>
                                `).join('')}
                            </optgroup>
                        `).join('');
                    })()}
                </select>
                <button id="refreshModelsBtn" title="Refresh models list">↻</button>
            </div>
            <p style="font-size: 0.9em; color: var(--vscode-descriptionForeground);">
                Models are fetched from OpenRouter. Click refresh to update the list.
            </p>
        </div>

        <div class="form-group">
            <label for="defaultTone">Default Tone</label>
            <select id="defaultTone">
                <option value="">Default</option>
                ${tones.map(tone => `
                    <option value="${tone.value}" ${preferences.default_tone === tone.value ? 'selected' : ''}>
                        ${tone.label}
                    </option>
                `).join('')}
            </select>
        </div>

        <div class="actions">
            <button id="saveBtn">Save Preferences</button>
            <button id="loadBtn">Load from Server</button>
        </div>

        <script>
            const vscode = acquireVsCodeApi();

            // Elements
            const userIdInput = document.getElementById('userId');
            const setUserIdBtn = document.getElementById('setUserIdBtn');
            const preferredModelSelect = document.getElementById('preferredModel');
            const defaultToneSelect = document.getElementById('defaultTone');
            const saveBtn = document.getElementById('saveBtn');
            const loadBtn = document.getElementById('loadBtn');
            const refreshModelsBtn = document.getElementById('refreshModelsBtn');

            // Set user ID
            setUserIdBtn.addEventListener('click', () => {
                const userId = userIdInput.value.trim();
                if (userId) {
                    vscode.postMessage({
                        command: 'setUserId',
                        userId: userId
                    });
                }
            });

            // Save preferences
            saveBtn.addEventListener('click', () => {
                const preferences = {
                    preferred_model: preferredModelSelect.value || undefined,
                    default_tone: defaultToneSelect.value || undefined
                };

                vscode.postMessage({
                    command: 'savePreferences',
                    preferences: preferences
                });
            });

            // Load preferences
            loadBtn.addEventListener('click', () => {
                vscode.postMessage({
                    command: 'loadPreferences'
                });
            });

            // Refresh models
            refreshModelsBtn.addEventListener('click', () => {
                refreshModelsBtn.disabled = true;
                refreshModelsBtn.textContent = '⟳';
                refreshModelsBtn.style.opacity = '0.5';

                vscode.postMessage({
                    command: 'refreshModels'
                });

                // Re-enable button after a delay
                setTimeout(() => {
                    refreshModelsBtn.disabled = false;
                    refreshModelsBtn.textContent = '↻';
                    refreshModelsBtn.style.opacity = '1';
                }, 2000);
            });
        </script>
    </body>
    </html>`;
  }
}
