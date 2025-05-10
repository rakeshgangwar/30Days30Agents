import * as vscode from 'vscode';
import { ApiService, UserPreferences } from 'writing-assistant-connector';

/**
 * Manages user preferences for the Writing Assistant extension
 *
 * This class handles syncing VS Code settings with the backend preferences API
 */
export class PreferencesManager {
  private apiService: ApiService;
  private userId: string | undefined;
  private context: vscode.ExtensionContext;
  private _preferences: UserPreferences | undefined;

  /**
   * Create a new preferences manager
   * @param apiService The API service to use for communicating with the backend
   * @param context The VS Code extension context
   */
  constructor(apiService: ApiService, context: vscode.ExtensionContext) {
    this.apiService = apiService;
    this.context = context;

    // Try to get the user ID from settings or global state
    const config = vscode.workspace.getConfiguration('writingAssistant');
    this.userId = config.get<string>('userId') || context.globalState.get<string>('writingAssistant.userId');
  }

  /**
   * Get the current user ID
   * @returns The current user ID or undefined if not set
   */
  public getUserId(): string | undefined {
    return this.userId;
  }

  /**
   * Set the user ID
   * @param userId The user ID to set
   */
  public async setUserId(userId: string): Promise<void> {
    this.userId = userId;

    // Update both global state and settings
    await this.context.globalState.update('writingAssistant.userId', userId);

    // Update VS Code settings
    const config = vscode.workspace.getConfiguration('writingAssistant');
    await config.update('userId', userId, vscode.ConfigurationTarget.Global);
  }

  /**
   * Get the current preferences
   * @returns The current preferences or undefined if not loaded
   */
  public getPreferences(): UserPreferences | undefined {
    return this._preferences;
  }

  /**
   * Load preferences from the backend
   * @returns The loaded preferences
   * @throws Error if no user ID is set or if the API call fails
   */
  public async loadPreferences(): Promise<UserPreferences> {
    if (!this.userId) {
      throw new Error('No user ID set. Please set a user ID first.');
    }

    try {
      const preferences = await this.apiService.getUserPreferences(this.userId);
      this._preferences = preferences;
      return preferences;
    } catch (error) {
      throw new Error(`Failed to load preferences: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Save preferences to the backend
   * @param preferences The preferences to save
   * @returns The saved preferences
   * @throws Error if no user ID is set or if the API call fails
   */
  public async savePreferences(preferences: UserPreferences): Promise<UserPreferences> {
    if (!this.userId) {
      throw new Error('No user ID set. Please set a user ID first.');
    }

    try {
      const savedPreferences = await this.apiService.updateUserPreferences(this.userId, preferences);
      this._preferences = savedPreferences;
      return savedPreferences;
    } catch (error) {
      throw new Error(`Failed to save preferences: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  /**
   * Sync VS Code settings with backend preferences
   * @returns The synced preferences
   * @throws Error if the API call fails
   */
  public async syncWithVSCodeSettings(): Promise<UserPreferences> {
    // Get VS Code settings
    const config = vscode.workspace.getConfiguration('writingAssistant');
    const preferredModel = config.get<string>('preferredModel');
    const defaultTone = config.get<string>('defaultTone');

    // Create preferences object
    const preferences: UserPreferences = {
      preferred_model: preferredModel,
      default_tone: defaultTone
    };

    // If we have a user ID, save to backend
    if (this.userId) {
      try {
        return await this.savePreferences(preferences);
      } catch (error) {
        // If saving fails, just return the local preferences
        this._preferences = preferences;
        return preferences;
      }
    } else {
      // If no user ID, just store locally
      this._preferences = preferences;
      return preferences;
    }
  }

  /**
   * Apply backend preferences to VS Code settings
   * @param preferences The preferences to apply
   */
  public async applyToVSCodeSettings(preferences: UserPreferences): Promise<void> {
    const config = vscode.workspace.getConfiguration('writingAssistant');

    // Only update if the values are different
    if (preferences.preferred_model && preferences.preferred_model !== config.get<string>('preferredModel')) {
      await config.update('preferredModel', preferences.preferred_model, vscode.ConfigurationTarget.Global);
    }

    if (preferences.default_tone && preferences.default_tone !== config.get<string>('defaultTone')) {
      await config.update('defaultTone', preferences.default_tone, vscode.ConfigurationTarget.Global);
    }
  }

  /**
   * Prompt the user to enter a user ID
   * @returns The entered user ID or undefined if cancelled
   */
  public async promptForUserId(): Promise<string | undefined> {
    const userId = await vscode.window.showInputBox({
      prompt: 'Enter your Writing Assistant user ID',
      placeHolder: 'user123',
      value: this.userId
    });

    if (userId) {
      await this.setUserId(userId);
    }

    return userId;
  }
}
