"""
Task Automation Agent - File Tool

This module provides a tool for file system operations.
"""

import os
from typing import List, Optional
from pydantic_ai.tools import Tool

class FileTool(Tool):
    """
    Tool for file system operations.
    
    This tool provides methods for reading, writing, and listing files.
    """
    
    name = "FileTool"
    description = "Tool for file system operations like reading, writing, and listing files."
    
    def list_files(self, directory: str = ".") -> List[str]:
        """
        List files in a directory.
        
        Args:
            directory: The directory to list files from (default: current directory)
            
        Returns:
            List of filenames in the directory
        """
        try:
            return os.listdir(directory)
        except Exception as e:
            return f"Error listing files in {directory}: {str(e)}"
    
    def read_file(self, file_path: str) -> str:
        """
        Read the contents of a file.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            Contents of the file as a string
        """
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"
    
    def write_file(self, file_path: str, content: str) -> str:
        """
        Write content to a file.
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            
        Returns:
            Success message or error
        """
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing to file {file_path}: {str(e)}"
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if the file exists, False otherwise
        """
        return os.path.isfile(file_path)
    
    def create_directory(self, directory: str) -> str:
        """
        Create a directory.
        
        Args:
            directory: Path to the directory to create
            
        Returns:
            Success message or error
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return f"Successfully created directory {directory}"
        except Exception as e:
            return f"Error creating directory {directory}: {str(e)}"
