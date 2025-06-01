#!/usr/bin/env python
"""
Test script for Whisper and Pyannote models.

This script tests the installation and configuration of both Whisper and Pyannote models
by processing a sample audio file and verifying the results.

Usage:
    python test_models.py <path_to_test_audio_file>

Requires:
    - HF_TOKEN environment variable to be set for Pyannote model access
    - A test audio file containing speech from multiple speakers
"""

import os
import sys
import time
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to allow importing from src
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.model_manager import AIModelManager

def get_test_audio():
    """Return the path to the sample audio file."""
    test_dir = Path("tests/test_files")
    return test_dir / "sample.wav"

def main():
    # Configure logging
    logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    
    # Check for HF token
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        logger.error("HF_TOKEN environment variable not set")
        logger.info("You need to set this to access Pyannote models")
        logger.info("Example: set HF_TOKEN=your_token_here  # Windows")
        logger.info("Example: export HF_TOKEN=your_token_here  # Linux/Mac")
        return 1
    
    # Get test audio file path
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        if not os.path.exists(test_file):
            logger.error(f"Test file not found: {test_file}")
            return 1
    else:
        test_file = get_test_audio()
        if not test_file.exists():
            logger.error(f"Test file not found: {test_file}")
            logger.info("Please provide a path to a test audio file as an argument or place a sample audio file in the tests/test_files directory")
            return 1
    
    logger.info(f"Testing AI models with audio file: {test_file}")
    
    # Initialize model manager
    try:
        start_time = time.time()
        model_manager = AIModelManager(whisper_model_size="base", hf_token=hf_token)
        logger.info(f"Model manager initialized in {time.time() - start_time:.2f} seconds")
        
        # Test models
        logger.info("Testing Whisper and Pyannote models...")
        start_time = time.time()
        whisper_success, pyannote_success = model_manager.test_models(test_file)
        logger.info(f"Model testing completed in {time.time() - start_time:.2f} seconds")
        
        # Report results
        if whisper_success and pyannote_success:
            logger.success("✅ All models tested successfully!")
            return 0
        else:
            if not whisper_success:
                logger.error("❌ Whisper model test failed!")
            if not pyannote_success:
                logger.error("❌ Pyannote model test failed!")
            return 1
    except Exception as e:
        logger.error(f"Error during model testing: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
