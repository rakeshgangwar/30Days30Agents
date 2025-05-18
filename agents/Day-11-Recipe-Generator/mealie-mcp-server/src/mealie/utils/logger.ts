/**
 * Logger utility for MCP server
 * 
 * This logger is transport-aware and ensures logs don't interfere with stdio transport.
 */

/**
 * Logger configuration
 */
export interface LoggerConfig {
  /**
   * Whether to use stdio transport
   */
  usingStdio: boolean;
  
  /**
   * Minimum log level to display
   */
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
}

/**
 * Creates a logger instance
 * @param config Logger configuration
 * @returns Logger object
 */
export function createLogger(config: LoggerConfig) {
  const { usingStdio, logLevel = 'info' } = config;
  
  // Log level priorities
  const logLevels = {
    debug: 0,
    info: 1,
    warn: 2,
    error: 3
  };
  
  // Minimum log level to display
  const minLevel = logLevels[logLevel];
  
  /**
   * Logs a message at the specified level
   * @param level Log level
   * @param message Message to log
   * @param args Additional arguments
   */
  function log(level: 'debug' | 'info' | 'warn' | 'error', message: string, ...args: any[]) {
    // Skip if log level is below minimum
    if (logLevels[level] < minLevel) {
      return;
    }
    
    const timestamp = new Date().toISOString();
    const formattedMessage = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
    
    if (usingStdio) {
      // When using stdio, write to stderr to avoid interfering with the JSON-RPC protocol
      process.stderr.write(`${formattedMessage}\n`);
      if (args.length > 0) {
        process.stderr.write(`${JSON.stringify(args)}\n`);
      }
    } else {
      // When using HTTP, use normal console
      switch (level) {
        case 'debug':
        case 'info':
          console.log(formattedMessage, ...args);
          break;
        case 'warn':
          console.warn(formattedMessage, ...args);
          break;
        case 'error':
          console.error(formattedMessage, ...args);
          break;
      }
    }
  }
  
  return {
    debug: (message: string, ...args: any[]) => log('debug', message, ...args),
    info: (message: string, ...args: any[]) => log('info', message, ...args),
    warn: (message: string, ...args: any[]) => log('warn', message, ...args),
    error: (message: string, ...args: any[]) => log('error', message, ...args)
  };
}
