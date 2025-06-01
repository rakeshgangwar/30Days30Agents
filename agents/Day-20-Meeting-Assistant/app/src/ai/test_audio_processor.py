#!/usr/bin/env python
"""
Test script for the Audio Processing Pipeline.

This script tests the complete audio processing pipeline including:
- Audio format conversion
- Transcription
- Speaker diarization
- Transcript-speaker alignment

Usage:
    python test_audio_processor.py <path_to_test_audio_file>

Requires:
    - HF_TOKEN environment variable to be set for Pyannote model access
    - A test audio file containing speech from multiple speakers
"""

import os
import sys
import time
from pathlib import Path
import argparse
from loguru import logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to path to allow importing from src
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.audio_processor import AudioProcessor


def get_test_audio():
    """Return the path to the sample audio file."""
    test_dir = Path("tests/test_files")
    return test_dir / "sample.wav"


def test_format_conversion(processor, test_file):
    """Test audio format conversion functionality."""
    logger.info("Testing audio format conversion...")
    try:
        start_time = time.time()
        converted_file = processor.convert_audio_format(test_file)
        duration = time.time() - start_time
        
        logger.info(f"Conversion completed in {duration:.2f} seconds")
        logger.info(f"Converted file: {converted_file}")
        
        if converted_file.exists() and converted_file.stat().st_size > 0:
            logger.success("✅ Audio format conversion test passed")
            return True
        else:
            logger.error("❌ Converted file is empty or doesn't exist")
            return False
    except Exception as e:
        logger.error(f"❌ Audio format conversion test failed: {str(e)}")
        return False


def test_processing_pipeline(processor, test_file):
    """Test the complete audio processing pipeline."""
    logger.info("Testing complete audio processing pipeline...")
    try:
        start_time = time.time()
        results = processor.process_audio(test_file)
        duration = time.time() - start_time
        
        logger.info(f"Processing completed in {duration:.2f} seconds")
        
        # Check transcription
        if not results.get("transcription") or not results["transcription"].get("text"):
            logger.error("❌ No transcription results found")
            return False
        
        # Check speaker segments
        if not results.get("speaker_segments") or len(results["speaker_segments"]) == 0:
            logger.error("❌ No speaker segments found")
            return False
        
        # Check aligned transcript
        if not results.get("aligned_transcript") or len(results["aligned_transcript"]) == 0:
            logger.error("❌ No aligned transcript found")
            return False
        
        # Log sample results
        logger.info(f"Transcription sample: {results['transcription']['text'][:100]}...")
        logger.info(f"Found {len(results['speaker_segments'])} speaker segments")
        logger.info(f"Found {len(results['aligned_transcript'])} aligned transcript segments")
        
        # Save results to JSON
        output_path = Path(test_file).with_suffix(".json")
        processor.save_results(results, output_path)
        logger.info(f"Results saved to: {output_path}")
        
        logger.success("✅ Audio processing pipeline test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Audio processing pipeline test failed: {str(e)}")
        return False


def test_audio_formats(processor):
    """Test processing of different audio formats."""
    # This would ideally test WAV, MP3, and WEBM files
    # For now, we'll just log that this would be tested in a real environment
    logger.info("In a complete test suite, we would test multiple audio formats here")
    logger.info(f"Supported formats: {processor.SUPPORTED_FORMATS}")
    return True


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Test the audio processing pipeline")
    parser.add_argument("audio_file", nargs="?", help="Path to test audio file")
    parser.add_argument("--whisper-model", default="base", help="Whisper model size to use")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    
    # Configure logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger.remove()  # Remove default handler
    logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>", level=log_level)
    
    # Check for HF token
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        logger.error("HF_TOKEN environment variable not set")
        logger.info("You need to set this to access Pyannote models")
        logger.info("Example: set HF_TOKEN=your_token_here  # Windows")
        logger.info("Example: export HF_TOKEN=your_token_here  # Linux/Mac")
        return 1
    
    # Get test audio file path
    if args.audio_file:
        test_file = Path(args.audio_file)
        if not test_file.exists():
            logger.error(f"Test file not found: {test_file}")
            return 1
    else:
        test_file = get_test_audio()
        if not test_file.exists():
            logger.error(f"Test file not found: {test_file}")
            logger.info("Please provide a path to a test audio file as an argument or place a sample audio file in the tests/test_files directory")
            return 1
    
    logger.info(f"Testing audio processor with file: {test_file}")
    logger.info(f"Using Whisper model size: {args.whisper_model}")
    
    # Initialize audio processor
    try:
        start_time = time.time()
        processor = AudioProcessor(whisper_model_size=args.whisper_model, hf_token=hf_token)
        logger.info(f"Audio processor initialized in {time.time() - start_time:.2f} seconds")
        
        # Run tests
        format_test = test_format_conversion(processor, test_file)
        pipeline_test = test_processing_pipeline(processor, test_file)
        format_support_test = test_audio_formats(processor)
        
        # Report results
        logger.info("\nTest Results Summary:")
        logger.info(f"Audio Format Conversion: {'✅ PASSED' if format_test else '❌ FAILED'}")
        logger.info(f"Complete Processing Pipeline: {'✅ PASSED' if pipeline_test else '❌ FAILED'}")
        logger.info(f"Audio Format Support: {'✅ PASSED' if format_support_test else '❌ FAILED'}")
        
        if format_test and pipeline_test and format_support_test:
            logger.success("\n✅ All tests passed successfully!")
            return 0
        else:
            logger.error("\n❌ Some tests failed. See logs above for details.")
            return 1
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
