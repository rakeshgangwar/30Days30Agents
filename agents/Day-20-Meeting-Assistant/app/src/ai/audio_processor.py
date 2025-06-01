#!/usr/bin/env python
"""
Audio Processing Pipeline for Meeting Assistant.

This module provides core audio processing functionality including:
- Audio format conversion using ffmpeg
- Transcription using Whisper
- Speaker diarization using Pyannote
- Transcript-speaker alignment algorithm
"""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Union, Optional, Tuple
import json
import numpy as np
from loguru import logger

from .model_manager import AIModelManager


class AudioProcessor:
    """Core audio processing pipeline for Meeting Assistant.
    
    This class handles the complete audio processing workflow including:
    - Audio format conversion
    - Transcription
    - Speaker diarization
    - Alignment of transcripts with speaker segments
    """
    
    # Supported input audio formats
    SUPPORTED_FORMATS = ['.wav', '.mp3', '.m4a', '.webm', '.mp4', '.mpeg', '.mpga', '.ogg', '.oga', '.flac']
    
    # Target format for processing (WAV is most reliable for ML models)
    TARGET_FORMAT = '.wav'
    
    def __init__(
        self,
        model_manager: Optional[AIModelManager] = None,
        whisper_model_size: str = "base",
        device: Optional[str] = None,
        hf_token: Optional[str] = None,
        temp_dir: Optional[Union[str, Path]] = None
    ):
        """
        Initialize the Audio Processor.
        
        Args:
            model_manager: Optional pre-initialized AIModelManager. If None, a new one will be created.
            whisper_model_size: Size of Whisper model to use if creating a new model manager
            device: Device to run models on. If None, will use CUDA if available, otherwise CPU
            hf_token: HuggingFace token for accessing Pyannote models
            temp_dir: Directory to store temporary files. If None, uses system temp directory
        """
        # Initialize model manager if not provided
        self.model_manager = model_manager or AIModelManager(
            whisper_model_size=whisper_model_size,
            device=device,
            hf_token=hf_token
        )
        
        # Set up temporary directory for audio conversion
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "meeting_assistant"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized AudioProcessor with temp directory: {self.temp_dir}")
        
    def convert_audio_format(self, audio_path: Union[str, Path], target_format: str = None) -> Path:
        """
        Convert audio to the target format using ffmpeg.
        
        Args:
            audio_path: Path to the input audio file
            target_format: Target format extension (e.g., '.wav'). If None, uses self.TARGET_FORMAT
            
        Returns:
            Path to the converted audio file
        """
        audio_path = Path(audio_path)
        target_format = target_format or self.TARGET_FORMAT
        
        # Check if file exists
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Check if input format is supported
        if audio_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported audio format: {audio_path.suffix}. Supported formats: {self.SUPPORTED_FORMATS}")
        
        # If already in target format, just return the path
        if audio_path.suffix.lower() == target_format.lower():
            logger.info(f"Audio already in target format {target_format}: {audio_path}")
            return audio_path
        
        # Create output filename
        output_path = self.temp_dir / f"{audio_path.stem}{target_format}"
        
        try:
            logger.info(f"Converting {audio_path} to {target_format} format")
            
            # Run ffmpeg command
            cmd = [
                "ffmpeg",
                "-i", str(audio_path),  # Input file
                "-y",                   # Overwrite output file if exists
                "-ar", "16000",        # Set sample rate to 16kHz (good for ML models)
                "-ac", "1",            # Convert to mono
                str(output_path)        # Output file
            ]
            
            # Execute ffmpeg
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False  # Don't raise exception, we'll handle errors
            )
            
            # Check if conversion was successful
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise RuntimeError(f"Failed to convert audio: {result.stderr}")
            
            logger.success(f"Successfully converted audio to {target_format}: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error during audio conversion: {str(e)}")
            raise
    
    def process_audio(self, audio_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """
        Process an audio file through the complete pipeline.
        
        Args:
            audio_path: Path to the audio file to process
            **kwargs: Additional arguments for processing
                - whisper_kwargs: Arguments for Whisper transcription
                - diarization_kwargs: Arguments for Pyannote diarization
                - skip_conversion: If True, skips audio conversion step
            
        Returns:
            Dictionary containing processed results including:
            - transcription: Full transcription from Whisper
            - speaker_segments: Speaker segments from Pyannote
            - aligned_transcript: Transcript segments aligned with speakers
        """
        # Extract kwargs
        whisper_kwargs = kwargs.get("whisper_kwargs", {})
        diarization_kwargs = kwargs.get("diarization_kwargs", {})
        skip_conversion = kwargs.get("skip_conversion", False)
        
        try:
            # Step 1: Convert audio format if needed
            if not skip_conversion:
                audio_path = self.convert_audio_format(audio_path)
            
            # Step 2: Process with model manager (transcription + diarization)
            logger.info(f"Processing audio with AI models: {audio_path}")
            results = self.model_manager.process_audio(
                audio_path,
                whisper_kwargs=whisper_kwargs,
                diarization_kwargs=diarization_kwargs
            )
            
            # Step 3: Align transcript with speaker segments
            aligned_transcript = self.align_transcript_with_speakers(
                results["transcription"],
                results["speaker_segments"]
            )
            
            # Add aligned transcript to results
            results["aligned_transcript"] = aligned_transcript
            
            logger.success(f"Successfully processed audio file: {audio_path}")
            return results
            
        except Exception as e:
            logger.error(f"Error during audio processing: {str(e)}")
            raise
    
    def align_transcript_with_speakers(self, transcription: Dict[str, Any], speaker_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Align transcript segments with speaker segments.
        
        Args:
            transcription: Transcription result from Whisper
            speaker_segments: Speaker segments from Pyannote
            
        Returns:
            List of dictionaries, each containing:
            - start: Start time in seconds
            - end: End time in seconds
            - speaker: Speaker ID
            - text: Transcribed text for this segment
        """
        # Extract segments from Whisper transcription
        transcript_segments = transcription.get("segments", [])
        
        # If either list is empty, return an empty result
        if not transcript_segments or not speaker_segments:
            logger.warning("Empty transcript or speaker segments, cannot align")
            return []
        
        aligned_results = []
        
        # For each transcript segment, find the overlapping speaker segments
        for t_segment in transcript_segments:
            t_start = t_segment["start"]
            t_end = t_segment["end"]
            t_text = t_segment["text"]
            
            # Find speaker segments that overlap with this transcript segment
            overlapping_speakers = []
            for s_segment in speaker_segments:
                s_start = s_segment["start"]
                s_end = s_segment["end"]
                
                # Check for overlap
                if max(t_start, s_start) < min(t_end, s_end):
                    # Calculate overlap duration
                    overlap_start = max(t_start, s_start)
                    overlap_end = min(t_end, s_end)
                    overlap_duration = overlap_end - overlap_start
                    
                    overlapping_speakers.append({
                        "speaker": s_segment["speaker"],
                        "overlap_duration": overlap_duration,
                        "overlap_start": overlap_start,
                        "overlap_end": overlap_end
                    })
            
            # If we found overlapping speakers
            if overlapping_speakers:
                # Sort by overlap duration (descending)
                overlapping_speakers.sort(key=lambda x: x["overlap_duration"], reverse=True)
                
                # Assign the speaker with the most overlap
                best_match = overlapping_speakers[0]
                
                aligned_results.append({
                    "start": t_start,
                    "end": t_end,
                    "speaker": best_match["speaker"],
                    "text": t_text
                })
            else:
                # No speaker found, use "unknown"
                aligned_results.append({
                    "start": t_start,
                    "end": t_end,
                    "speaker": "unknown",
                    "text": t_text
                })
        
        logger.info(f"Aligned {len(aligned_results)} transcript segments with speakers")
        return aligned_results
    
    def save_results(self, results: Dict[str, Any], output_path: Union[str, Path]) -> Path:
        """
        Save processing results to a JSON file.
        
        Args:
            results: Results from process_audio()
            output_path: Path to save the results
            
        Returns:
            Path to the saved file
        """
        output_path = Path(output_path)
        
        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare results for serialization
        serializable_results = {
            "transcription": {
                "text": results["transcription"]["text"],
                "segments": results["transcription"]["segments"]
            },
            "speaker_segments": results["speaker_segments"],
            "aligned_transcript": results["aligned_transcript"]
        }
        
        # Save to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, ensure_ascii=False)
        
        logger.success(f"Saved processing results to: {output_path}")
        return output_path


# Example usage
if __name__ == "__main__":
    import sys
    import os
    from dotenv import load_dotenv
    
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
    
    # Initialize processor
    processor = AudioProcessor(whisper_model_size="base", hf_token=hf_token)
    
    # Process audio
    try:
        results = processor.process_audio(test_file)
        
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
        output_path = Path(test_file).with_suffix(".json")
        processor.save_results(results, output_path)
        print(f"\nResults saved to: {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
