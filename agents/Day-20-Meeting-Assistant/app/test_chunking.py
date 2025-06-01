#!/usr/bin/env python
"""
Simple test script for audio chunking functionality.
"""

import os
import sys
import asyncio
from pathlib import Path
import time
import argparse
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the AudioChunker directly
sys.path.insert(0, str(Path(__file__).resolve().parent))
from src.ai.audio_chunker import AudioChunker
from src.ai.audio_processor import AudioProcessor


async def test_chunking(audio_file, chunk_duration=300, max_workers=2):
    """
    Test audio chunking functionality.
    
    Args:
        audio_file: Path to the audio file
        chunk_duration: Duration of each chunk in seconds
        max_workers: Maximum number of parallel workers
    """
    # Get HuggingFace token from environment
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        logger.error("HF_TOKEN environment variable not set")
        return False
    
    try:
        # Initialize processor and chunker
        logger.info(f"Testing audio chunking with {audio_file}")
        logger.info(f"Chunk duration: {chunk_duration} seconds")
        logger.info(f"Max workers: {max_workers}")
        
        # Create temp directories
        temp_dir = Path("temp_chunks")
        temp_dir.mkdir(exist_ok=True)
        
        # Initialize processor and chunker
        processor = AudioProcessor(whisper_model_size="base", hf_token=hf_token, temp_dir=temp_dir)
        chunker = AudioChunker(
            audio_processor=processor,
            chunk_duration=chunk_duration,
            max_workers=max_workers,
            temp_dir=temp_dir
        )
        
        # Test audio splitting
        logger.info("Testing audio splitting...")
        start_time = time.time()
        chunks = chunker.split_audio(audio_file)
        split_time = time.time() - start_time
        logger.info(f"Split audio into {len(chunks)} chunks in {split_time:.2f} seconds")
        
        # Print chunk information
        for i, chunk in enumerate(chunks):
            logger.info(f"Chunk {i+1}: {chunk['start_time']:.2f}s to {chunk['end_time']:.2f}s")
        
        # Test audio duration detection
        duration = chunker.get_audio_duration(audio_file)
        logger.info(f"Audio duration: {duration:.2f} seconds")
        
        # Process the first chunk only for quick testing
        if len(chunks) > 0:
            logger.info("Testing processing of the first chunk...")
            first_chunk = chunks[0]
            result = await chunker.process_chunk(first_chunk)
            logger.info(f"Successfully processed first chunk: {first_chunk['start_time']:.2f}s to {first_chunk['end_time']:.2f}s")
            
            # Print sample of results
            logger.info("\nTranscription sample:")
            logger.info(result["transcription"]["text"][:200] + "...")
            
            # Save results
            output_path = Path(audio_file).with_suffix(".chunk0.json")
            chunker.save_results(result, output_path)
            logger.info(f"Results saved to: {output_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test audio chunking functionality")
    parser.add_argument("audio_file", help="Path to the audio file to test")
    parser.add_argument(
        "--chunk-duration", 
        type=int, 
        default=300, 
        help="Duration of each chunk in seconds (default: 300s)"
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
    
    # Run the test
    success = await test_chunking(
        args.audio_file,
        chunk_duration=args.chunk_duration,
        max_workers=args.max_workers
    )
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
