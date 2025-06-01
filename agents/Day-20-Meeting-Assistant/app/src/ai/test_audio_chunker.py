#!/usr/bin/env python
"""
Test script for the Audio Chunking System.

This script tests the functionality of the AudioChunker class, including:
- Audio file splitting
- Parallel processing
- Result combination
"""

import os
import sys
import asyncio
from pathlib import Path
import time
import argparse
from dotenv import load_dotenv
from loguru import logger

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.ai.audio_processor import AudioProcessor
from src.ai.audio_chunker import AudioChunker
from config.settings import settings


async def test_audio_chunking(audio_file: str, chunk_duration: int = 60, max_workers: int = 2):
    """
    Test the audio chunking system with a given audio file.
    
    Args:
        audio_file: Path to the audio file to test
        chunk_duration: Duration of each chunk in seconds (default: 60s for testing)
        max_workers: Maximum number of parallel workers (default: 2)
    """
    logger.info(f"Testing audio chunking with file: {audio_file}")
    logger.info(f"Chunk duration: {chunk_duration} seconds")
    logger.info(f"Max workers: {max_workers}")
    
    # Get HuggingFace token from environment
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        logger.error("HF_TOKEN environment variable not set")
        logger.error("You need to set this to access Pyannote models")
        logger.error("Example: set HF_TOKEN=your_token_here")
        return False
    
    try:
        # Initialize processor and chunker
        logger.info("Initializing AudioProcessor and AudioChunker...")
        processor = AudioProcessor(whisper_model_size="base", hf_token=hf_token)
        chunker = AudioChunker(
            audio_processor=processor,
            chunk_duration=chunk_duration,
            max_workers=max_workers
        )
        
        # Test audio duration detection
        logger.info("Testing audio duration detection...")
        duration = chunker.get_audio_duration(audio_file)
        logger.success(f"Audio duration: {duration:.2f} seconds")
        
        # Test audio splitting
        logger.info("Testing audio splitting...")
        start_time = time.time()
        chunks = chunker.split_audio(audio_file)
        split_time = time.time() - start_time
        logger.success(f"Split audio into {len(chunks)} chunks in {split_time:.2f} seconds")
        
        # Print chunk information
        for i, chunk in enumerate(chunks):
            logger.info(f"Chunk {i+1}: {chunk['start_time']:.2f}s to {chunk['end_time']:.2f}s")
        
        # Test parallel processing
        logger.info("Testing parallel processing...")
        start_time = time.time()
        results = await chunker.process_audio(audio_file)
        process_time = time.time() - start_time
        logger.success(f"Processed audio in {process_time:.2f} seconds")
        
        # Save results
        output_path = Path(audio_file).with_suffix(".chunked.json")
        chunker.save_results(results, output_path)
        logger.success(f"Results saved to: {output_path}")
        
        # Print sample of results
        logger.info("\nTranscription sample:")
        logger.info(results["transcription"]["text"][:200] + "...")
        
        logger.info("\nSpeaker segments sample:")
        for segment in results["speaker_segments"][:3]:
            logger.info(f"Speaker {segment['speaker']} from {segment['start']:.2f}s to {segment['end']:.2f}s")
        
        logger.info("\nAligned transcript sample:")
        for segment in results["aligned_transcript"][:3]:
            logger.info(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] Speaker {segment['speaker']}: {segment['text']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test the Audio Chunking System")
    parser.add_argument("audio_file", help="Path to the audio file to test")
    parser.add_argument(
        "--chunk-duration", 
        type=int, 
        default=60, 
        help="Duration of each chunk in seconds (default: 60s for testing)"
    )
    parser.add_argument(
        "--max-workers", 
        type=int, 
        default=2, 
        help="Maximum number of parallel workers (default: 2)"
    )
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Configure logger
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    # Run the test
    success = await test_audio_chunking(
        args.audio_file,
        chunk_duration=args.chunk_duration,
        max_workers=args.max_workers
    )
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
