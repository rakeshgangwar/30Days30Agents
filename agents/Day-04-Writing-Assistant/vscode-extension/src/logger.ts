import * as vscode from 'vscode';

/**
 * Log levels
 */
export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

/**
 * Logger for the Writing Assistant extension
 */
export class Logger {
  private static instance: Logger;
  private outputChannel: vscode.OutputChannel;
  private logLevel: LogLevel;

  /**
   * Create a new logger
   */
  private constructor() {
    this.outputChannel = vscode.window.createOutputChannel('Writing Assistant');
    this.logLevel = LogLevel.INFO; // Default log level
  }

  /**
   * Get the logger instance
   * @returns The logger instance
   */
  public static getInstance(): Logger {
    if (!Logger.instance) {
      Logger.instance = new Logger();
    }
    return Logger.instance;
  }

  /**
   * Set the log level
   * @param level The log level to set
   */
  public setLogLevel(level: LogLevel): void {
    this.logLevel = level;
    this.info(`Log level set to ${LogLevel[level]}`);
  }

  /**
   * Log a debug message
   * @param message The message to log
   * @param data Optional data to log
   */
  public debug(message: string, data?: any): void {
    this.log(LogLevel.DEBUG, message, data);
  }

  /**
   * Log an info message
   * @param message The message to log
   * @param data Optional data to log
   */
  public info(message: string, data?: any): void {
    this.log(LogLevel.INFO, message, data);
  }

  /**
   * Log a warning message
   * @param message The message to log
   * @param data Optional data to log
   */
  public warn(message: string, data?: any): void {
    this.log(LogLevel.WARN, message, data);
  }

  /**
   * Log an error message
   * @param message The message to log
   * @param error Optional error to log
   */
  public error(message: string, error?: any): void {
    this.log(LogLevel.ERROR, message, error);
  }

  /**
   * Log a message
   * @param level The log level
   * @param message The message to log
   * @param data Optional data to log
   */
  private log(level: LogLevel, message: string, data?: any): void {
    if (level < this.logLevel) {
      return;
    }

    const timestamp = new Date().toISOString();
    const levelString = LogLevel[level].padEnd(5, ' ');
    let logMessage = `[${timestamp}] [${levelString}] ${message}`;

    if (data) {
      if (data instanceof Error) {
        logMessage += `\n${data.stack || data.message}`;
      } else if (typeof data === 'object') {
        try {
          logMessage += `\n${JSON.stringify(data, null, 2)}`;
        } catch (e) {
          logMessage += `\n[Object could not be stringified]`;
        }
      } else {
        logMessage += `\n${data}`;
      }
    }

    this.outputChannel.appendLine(logMessage);

    // Also log to console for development
    if (level === LogLevel.ERROR) {
      console.error(logMessage);
    } else if (level === LogLevel.WARN) {
      console.warn(logMessage);
    } else if (level === LogLevel.INFO) {
      console.info(logMessage);
    } else {
      console.debug(logMessage);
    }
  }

  /**
   * Show the output channel
   */
  public show(): void {
    this.outputChannel.show();
  }

  /**
   * Dispose of the logger
   */
  public dispose(): void {
    this.outputChannel.dispose();
  }
}
