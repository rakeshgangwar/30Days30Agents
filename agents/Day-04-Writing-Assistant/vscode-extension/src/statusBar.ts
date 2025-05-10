import * as vscode from 'vscode';
import { ApiService } from 'writing-assistant-connector';

/**
 * Manages the Writing Assistant status bar item
 */
export class StatusBarManager {
  private statusBarItem: vscode.StatusBarItem;
  private apiService: ApiService;
  private healthCheckInterval: NodeJS.Timeout | undefined;

  constructor(apiService: ApiService) {
    this.apiService = apiService;
    this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    this.statusBarItem.command = 'writing-assistant.showPanel';
    this.statusBarItem.text = '$(pencil) Writing Assistant';
    this.statusBarItem.tooltip = 'Open Writing Assistant Panel';
    this.statusBarItem.show();

    // Start health check
    this.startHealthCheck();
  }

  /**
   * Start periodic health check
   */
  private startHealthCheck() {
    // Check health immediately
    this.checkHealth();

    // Then check every 30 seconds
    this.healthCheckInterval = setInterval(() => {
      this.checkHealth();
    }, 30000);
  }

  /**
   * Check API health and update status bar
   */
  private async checkHealth() {
    try {
      const isHealthy = await this.apiService.checkHealth();
      if (isHealthy) {
        this.statusBarItem.text = '$(check) Writing Assistant';
        this.statusBarItem.tooltip = 'Writing Assistant: Connected';
        this.statusBarItem.backgroundColor = undefined;
      } else {
        this.statusBarItem.text = '$(warning) Writing Assistant';
        this.statusBarItem.tooltip = 'Writing Assistant: Not Connected';
        this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
      }
    } catch (error) {
      this.statusBarItem.text = '$(error) Writing Assistant';
      this.statusBarItem.tooltip = `Writing Assistant: Error - ${error instanceof Error ? error.message : String(error)}`;
      this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
    }
  }

  /**
   * Dispose of resources
   */
  dispose() {
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
    }
    this.statusBarItem.dispose();
  }
}
