// Storage Manager Component
// This component manages persistent storage for the application

const fs = require('fs').promises;
const path = require('path');

class StorageManager {
  constructor(options = {}) {
    this.options = {
      storagePath: options.storagePath || path.join(process.cwd(), 'storage'),
      ...options
    };
    this.initialized = false;
  }
  
  async initialize() {
    if (this.initialized) return true;
    
    try {
      // Create storage directory if it doesn't exist
      await fs.mkdir(this.options.storagePath, { recursive: true });
      
      // Create subdirectories for different types of data
      await fs.mkdir(path.join(this.options.storagePath, 'issues'), { recursive: true });
      await fs.mkdir(path.join(this.options.storagePath, 'cache'), { recursive: true });
      await fs.mkdir(path.join(this.options.storagePath, 'reports'), { recursive: true });
      
      this.initialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize storage:', error.message);
      return false;
    }
  }
  
  async saveData(key, data) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      const filePath = this.getFilePath(key);
      
      // Create directory if it doesn't exist
      await fs.mkdir(path.dirname(filePath), { recursive: true });
      
      // Serialize and save data
      const serializedData = JSON.stringify(data, null, 2);
      await fs.writeFile(filePath, serializedData, 'utf8');
      
      return true;
    } catch (error) {
      console.error(`Failed to save data for key ${key}:`, error.message);
      return false;
    }
  }
  
  async loadData(key) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      const filePath = this.getFilePath(key);
      
      // Check if file exists
      try {
        await fs.access(filePath);
      } catch (error) {
        // File doesn't exist
        return null;
      }
      
      // Read and parse data
      const fileContent = await fs.readFile(filePath, 'utf8');
      return JSON.parse(fileContent);
    } catch (error) {
      console.error(`Failed to load data for key ${key}:`, error.message);
      return null;
    }
  }
  
  async deleteData(key) {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      const filePath = this.getFilePath(key);
      
      // Check if file exists
      try {
        await fs.access(filePath);
      } catch (error) {
        // File doesn't exist
        return true;
      }
      
      // Delete file
      await fs.unlink(filePath);
      return true;
    } catch (error) {
      console.error(`Failed to delete data for key ${key}:`, error.message);
      return false;
    }
  }
  
  async listDataKeys(prefix = '') {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      const directoryPath = path.join(this.options.storagePath, prefix);
      
      // Check if directory exists
      try {
        await fs.access(directoryPath);
      } catch (error) {
        // Directory doesn't exist
        return [];
      }
      
      // List files in directory
      const files = await fs.readdir(directoryPath, { withFileTypes: true });
      
      // Process files and directories
      const keys = [];
      
      for (const file of files) {
        const filePath = path.join(prefix, file.name);
        
        if (file.isDirectory()) {
          // Recursively list files in subdirectory
          const subKeys = await this.listDataKeys(filePath);
          keys.push(...subKeys);
        } else if (file.isFile() && file.name.endsWith('.json')) {
          // Add file to keys
          keys.push(filePath.replace(/\.json$/, ''));
        }
      }
      
      return keys;
    } catch (error) {
      console.error(`Failed to list data keys for prefix ${prefix}:`, error.message);
      return [];
    }
  }
  
  getFilePath(key) {
    // Add .json extension if not present
    const fileName = key.endsWith('.json') ? key : `${key}.json`;
    return path.join(this.options.storagePath, fileName);
  }
  
  async clearStorage() {
    if (!this.initialized) {
      await this.initialize();
    }
    
    try {
      // List all files and directories in storage
      const items = await fs.readdir(this.options.storagePath);
      
      // Delete each item
      for (const item of items) {
        const itemPath = path.join(this.options.storagePath, item);
        const stats = await fs.stat(itemPath);
        
        if (stats.isDirectory()) {
          // Remove directory recursively
          await this.removeDirectory(itemPath);
        } else {
          // Remove file
          await fs.unlink(itemPath);
        }
      }
      
      return true;
    } catch (error) {
      console.error('Failed to clear storage:', error.message);
      return false;
    }
  }
  
  async removeDirectory(dirPath) {
    try {
      // List all files and directories in directory
      const items = await fs.readdir(dirPath);
      
      // Delete each item
      for (const item of items) {
        const itemPath = path.join(dirPath, item);
        const stats = await fs.stat(itemPath);
        
        if (stats.isDirectory()) {
          // Remove directory recursively
          await this.removeDirectory(itemPath);
        } else {
          // Remove file
          await fs.unlink(itemPath);
        }
      }
      
      // Remove empty directory
      await fs.rmdir(dirPath);
      return true;
    } catch (error) {
      console.error(`Failed to remove directory ${dirPath}:`, error.message);
      return false;
    }
  }
}

module.exports = StorageManager;