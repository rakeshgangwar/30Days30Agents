#!/usr/bin/env python
"""
Audio Chunking System for Meeting Assistant.

This module provides functionality for splitting large audio files into smaller chunks,
processing them in parallel, and combining the results.
"""

import os
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Union, Optional, Tuple
import json
import numpy as np
from loguru import logger
import subprocess
from datetime import timedelta

from .audio_processor import AudioProcessor


class AudioChunker:
    """
    Audio Chunking System for processing large audio files.
    
    This class handles:
    - Splitting large audio files into manageable chunks (default: 15 minutes)
    - Managing chunk metadata
    - Processing chunks in parallel using asyncio
    - Combining results from all chunks into a cohesive output
    """
    
    # Default chunk duration in seconds (15 minutes)
    DEFAULT_CHUNK_DURATION = 15 * 60
    
    def __init__(
        self,
        audio_processor: Optional[AudioProcessor] = None,
        chunk_duration: int = DEFAULT_CHUNK_DURATION,
        temp_dir: Optional[Union[str, Path]] = None,
        max_workers: int = 3  # Default number of parallel workers
    ):
        """
        Initialize the Audio Chunker.
        
        Args:
            audio_processor: Optional pre-initialized AudioProcessor. If None, a new one will be created.
            chunk_duration: Duration of each chunk in seconds (default: 15 minutes)
            temp_dir: Directory to store temporary files. If None, uses system temp directory
            max_workers: Maximum number of parallel workers for processing chunks
        """
        # Store the audio processor or create a new one when needed
        self.audio_processor = audio_processor
        
        # Set chunk duration
        self.chunk_duration = chunk_duration
        
        # Set up temporary directory for chunks
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "meeting_assistant" / "chunks"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Set maximum number of parallel workers
        self.max_workers = max_workers
        
        logger.info(f"Initialized AudioChunker with chunk duration: {timedelta(seconds=chunk_duration)}")
        logger.info(f"Using temp directory: {self.temp_dir}")
        logger.info(f"Maximum parallel workers: {max_workers}")
    
    def get_audio_duration(self, audio_path: Union[str, Path]) -> float:
        """
        Get the duration of an audio file in seconds using ffprobe.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Duration of the audio file in seconds
        """
        audio_path = Path(audio_path)
        
        # Check if file exists
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            # Run ffprobe command to get duration
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                str(audio_path)
            ]
            
            # Execute ffprobe
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            # Check if command was successful
            if result.returncode != 0:
                logger.error(f"FFprobe error: {result.stderr}")
                raise RuntimeError(f"Failed to get audio duration: {result.stderr}")
            
            # Parse JSON output
            output = json.loads(result.stdout)
            duration = float(output["format"]["duration"])
            
            logger.info(f"Audio duration: {timedelta(seconds=duration)} ({duration:.2f} seconds)")
            return duration
            
        except Exception as e:
            logger.error(f"Error getting audio duration: {str(e)}")
            raise
    
    def split_audio(self, audio_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Split an audio file into chunks of specified duration.
        
        Args:
            audio_path: Path to the audio file to split
            
        Returns:
            List of dictionaries containing chunk metadata:
            - chunk_path: Path to the chunk file
            - start_time: Start time of the chunk in seconds
            - end_time: End time of the chunk in seconds
            - index: Index of the chunk (0-based)
        """
        audio_path = Path(audio_path)
        
        # Check if file exists
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            # Get audio duration
            duration = self.get_audio_duration(audio_path)
            
            # Calculate number of chunks needed
            num_chunks = int(np.ceil(duration / self.chunk_duration))
            
            # If only one chunk is needed, return the original file
            if num_chunks <= 1:
                logger.info(f"Audio file is shorter than chunk duration, no splitting needed")
                return [{
                    "chunk_path": audio_path,
                    "start_time": 0,
                    "end_time": duration,
                    "index": 0,
                    "is_original": True
                }]
            
            # Create a unique directory for this file's chunks
            chunks_dir = self.temp_dir / f"{audio_path.stem}_{os.urandom(4).hex()}"
            chunks_dir.mkdir(parents=True, exist_ok=True)
            
            chunks = []
            
            # Split audio into chunks using ffmpeg
            for i in range(num_chunks):
                start_time = i * self.chunk_duration
                end_time = min((i + 1) * self.chunk_duration, duration)
                chunk_duration = end_time - start_time
                
                # Create output filename for this chunk
                chunk_path = chunks_dir / f"chunk_{i:03d}_{audio_path.stem}{audio_path.suffix}"
                
                # Run ffmpeg command to extract chunk
                cmd = [
                    "ffmpeg",
                    "-i", str(audio_path),
                    "-ss", str(start_time),
                    "-t", str(chunk_duration),
                    "-c", "copy",  # Copy without re-encoding for speed
                    "-y",  # Overwrite output file if exists
                    str(chunk_path)
                ]
                
                # Execute ffmpeg
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                # Check if command was successful
                if result.returncode != 0:
                    logger.error(f"FFmpeg error: {result.stderr}")
                    raise RuntimeError(f"Failed to split audio: {result.stderr}")
                
                # Add chunk metadata to list
                chunks.append({
                    "chunk_path": chunk_path,
                    "start_time": start_time,
                    "end_time": end_time,
                    "index": i,
                    "is_original": False
                })
                
                logger.info(f"Created chunk {i+1}/{num_chunks}: {start_time:.2f}s to {end_time:.2f}s")
            
            logger.success(f"Split audio into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting audio: {str(e)}")
            raise
    
    async def process_chunk(self, chunk: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Process a single audio chunk.
        
        Args:
            chunk: Chunk metadata dictionary
            **kwargs: Additional arguments for processing
            
        Returns:
            Dictionary containing processed results with chunk metadata
        """
        try:
            # Ensure we have an audio processor
            if self.audio_processor is None:
                from .audio_processor import AudioProcessor
                self.audio_processor = AudioProcessor()
            
            # Process the chunk
            logger.info(f"Processing chunk {chunk['index']}: {chunk['start_time']:.2f}s to {chunk['end_time']:.2f}s")
            results = self.audio_processor.process_audio(chunk["chunk_path"], **kwargs)
            
            # Add chunk metadata to results
            results["chunk_metadata"] = {
                "start_time": chunk["start_time"],
                "end_time": chunk["end_time"],
                "index": chunk["index"]
            }
            
            logger.success(f"Successfully processed chunk {chunk['index']}")
            return results
            
        except Exception as e:
            logger.error(f"Error processing chunk {chunk['index']}: {str(e)}")
            raise
    
    async def process_chunks_parallel(self, chunks: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """
        Process multiple chunks in parallel using asyncio.
        
        Args:
            chunks: List of chunk metadata dictionaries
            **kwargs: Additional arguments for processing
            
        Returns:
            List of dictionaries containing processed results for each chunk
        """
        # Create a semaphore to limit concurrent processing
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def process_with_semaphore(chunk):
            async with semaphore:
                return await self.process_chunk(chunk, **kwargs)
        
        # Create tasks for all chunks
        tasks = [process_with_semaphore(chunk) for chunk in chunks]
        
        # Wait for all tasks to complete
        logger.info(f"Processing {len(chunks)} chunks in parallel with max {self.max_workers} workers")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Chunk {i} processing failed: {str(result)}")
            else:
                processed_results.append(result)
        
        logger.success(f"Successfully processed {len(processed_results)}/{len(chunks)} chunks")
        return processed_results
    
    def combine_results(self, chunk_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Combine results from multiple chunks into a single cohesive output.
        
        Args:
            chunk_results: List of processing results for each chunk
            
        Returns:
            Dictionary containing combined results
        """
        if not chunk_results:
            logger.warning("No chunk results to combine")
            return {}
        
        # Sort chunks by index
        chunk_results.sort(key=lambda x: x["chunk_metadata"]["index"])
        
        # Initialize combined results
        combined_results = {
            "transcription": {
                "text": "",
                "segments": []
            },
            "speaker_segments": [],
            "aligned_transcript": []
        }
        
        # Combine results from each chunk
        for result in chunk_results:
            chunk_start = result["chunk_metadata"]["start_time"]
            
            # Append transcription text
            if combined_results["transcription"]["text"]:
                combined_results["transcription"]["text"] += " " + result["transcription"]["text"]
            else:
                combined_results["transcription"]["text"] = result["transcription"]["text"]
            
            # Adjust and append transcription segments
            for segment in result["transcription"]["segments"]:
                adjusted_segment = segment.copy()
                adjusted_segment["start"] += chunk_start
                adjusted_segment["end"] += chunk_start
                combined_results["transcription"]["segments"].append(adjusted_segment)
            
            # Adjust and append speaker segments
            for segment in result["speaker_segments"]:
                adjusted_segment = segment.copy()
                adjusted_segment["start"] += chunk_start
                adjusted_segment["end"] += chunk_start
                combined_results["speaker_segments"].append(adjusted_segment)
            
            # Adjust and append aligned transcript
            for segment in result["aligned_transcript"]:
                adjusted_segment = segment.copy()
                adjusted_segment["start"] += chunk_start
                adjusted_segment["end"] += chunk_start
                combined_results["aligned_transcript"].append(adjusted_segment)
        
        logger.success(f"Combined results from {len(chunk_results)} chunks")
        return combined_results
    
    async def process_audio(self, audio_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Process a large audio file by splitting it into chunks, processing them in parallel,
        and combining the results.
        
        Args:
            audio_path: Path to the audio file to process
            **kwargs: Additional arguments for processing
            
        Returns:
            Dictionary containing combined processed results
        """
        try:
            # Split audio into chunks
            chunks = self.split_audio(audio_path)
            
            # If only one chunk, process it directly
            if len(chunks) == 1 and chunks[0].get("is_original", False):
                logger.info("Audio file is small enough to process directly")
                if self.audio_processor is None:
                    from .audio_processor import AudioProcessor
                    self.audio_processor = AudioProcessor()
                return self.audio_processor.process_audio(audio_path, **kwargs)
            
            # Process chunks in parallel
            chunk_results = await self.process_chunks_parallel(chunks, **kwargs)
            
            # Combine results
            combined_results = self.combine_results(chunk_results)
            
            logger.success(f"Successfully processed audio file with chunking: {audio_path}")
            return combined_results
            
        except Exception as e:
            logger.error(f"Error during chunked audio processing: {str(e)}")
            raise
    
    def save_results(self, results: Dict[str, Any], output_path: Union[str, Path]) -> Path:
        """
        Save processing results to a JSON file.
        
        Args:
            results: Results from process_audio()
            output_path: Path to save the results
            
        Returns:
            Path to the saved file
        """
        # Delegate to audio processor's save_results method
        if self.audio_processor is None:
            from .audio_processor import AudioProcessor
            self.audio_processor = AudioProcessor()
        
        return self.audio_processor.save_results(results, output_path)


# Example usage
if __name__ == "__main__":
    import sys
    import os
    from dotenv import load_dotenv
    import asyncio
    
    # Load environment variables
    load_dotenv()
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        print("Please provide a path to a test audio file as an argument")
        sys.exit(1)
    
    # Get HuggingFace token from environment
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("⚠️ HF_TOKEN environment variable not set")
        print("You need to set this to access Pyannote models")
        print("Example: export HF_TOKEN=your_token_here")
        sys.exit(1)
    
    # Initialize chunker
    from audio_processor import AudioProcessor
    processor = AudioProcessor(whisper_model_size="base", hf_token=hf_token)
    chunker = AudioChunker(audio_processor=processor, chunk_duration=60)  # 1 minute chunks for testing
    
    # Process audio
    async def main():
        try:
            results = await chunker.process_audio(test_file)
            
            # Print sample of results
            print("\nTranscription sample:")
            print(results["transcription"]["text"][:200] + "...")
            
            print("\nSpeaker segments sample:")
            for segment in results["speaker_segments"][:3]:
                print(f"Speaker {segment['speaker']} from {segment['start']:.2f}s to {segment['end']:.2f}s")
            
            print("\nAligned transcript sample:")
            for segment in results["aligned_transcript"][:3]:
                print(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] Speaker {segment['speaker']}: {segment['text']}")
            
            # Save results
            output_path = Path(test_file).with_suffix(".chunked.json")
            chunker.save_results(results, output_path)
            print(f"\nResults saved to: {output_path}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    # Run the async main function
    asyncio.run(main())
