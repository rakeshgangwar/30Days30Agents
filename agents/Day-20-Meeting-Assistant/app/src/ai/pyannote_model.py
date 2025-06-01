import os
import torch
import logging
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
from loguru import logger

class PyannoteDiarization:
    """Wrapper for Pyannote.audio speaker diarization model."""
    
    def __init__(self, device: Optional[str] = None, hf_token: Optional[str] = None):
        """
        Initialize the Pyannote speaker diarization model.
        
        Args:
            device: Device to run the model on. If None, will use CUDA if available, otherwise CPU.
            hf_token: HuggingFace token for accessing the Pyannote models. If None, will try to get from environment.
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.hf_token = hf_token or os.environ.get("HF_TOKEN")
        self.pipeline = None
        
        if not self.hf_token:
            logger.warning("No HuggingFace token provided. You will need to set HF_TOKEN environment variable")
        
        # Create cache directory if it doesn't exist
        self.cache_dir = Path(os.environ.get("MODEL_CACHE_DIR", Path.home() / ".cache" / "meeting_assistant" / "models"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initializing Pyannote diarization model on device: {self.device}")
        
        # Log GPU information if available
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)  # Convert to GB
            logger.info(f"GPU detected: {gpu_name} with {gpu_memory:.2f} GB memory")
        else:
            logger.warning("No GPU detected. Using CPU for diarization, which may be slow.")
    
    def load_model(self) -> bool:
        """Load the Pyannote speaker diarization model.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from pyannote.audio import Pipeline
            
            if not self.hf_token:
                raise ValueError("HuggingFace token is required to access Pyannote models")
            
            logger.info("Loading Pyannote speaker diarization pipeline")
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.hf_token,
                cache_dir=str(self.cache_dir)
            )
            
            # Move model to the appropriate device
            self.pipeline.to(torch.device(self.device))
            
            logger.success("Successfully loaded Pyannote speaker diarization model")
            return True
        except Exception as e:
            logger.error(f"Failed to load Pyannote model: {str(e)}")
            return False
    
    def diarize(self, audio_path: Union[str, Path], **kwargs) -> Any:
        """Perform speaker diarization on an audio file.
        
        Args:
            audio_path: Path to the audio file to diarize
            **kwargs: Additional arguments to pass to the diarization pipeline
        
        Returns:
            Diarization results from Pyannote
        """
        if self.pipeline is None:
            success = self.load_model()
            if not success:
                raise RuntimeError("Failed to load Pyannote model. Cannot perform diarization.")
        
        try:
            logger.info(f"Performing speaker diarization on: {audio_path}")
            diarization = self.pipeline(str(audio_path), **kwargs)
            logger.success(f"Successfully diarized audio file: {audio_path}")
            return diarization
        except Exception as e:
            logger.error(f"Error during diarization: {str(e)}")
            raise
    
    def get_speaker_segments(self, diarization_result) -> List[Dict[str, Any]]:
        """Extract speaker segments from diarization results.
        
        Args:
            diarization_result: The result from the diarize() method
            
        Returns:
            List of dictionaries with speaker segments, each containing:
            - start: Start time in seconds
            - end: End time in seconds
            - speaker: Speaker ID
        """
        segments = []
        for turn, _, speaker in diarization_result.itertracks(yield_label=True):
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
        return segments
    
    def test_diarization(self, test_audio_path: Union[str, Path]) -> bool:
        """Test the diarization functionality with a sample audio file.
        
        Args:
            test_audio_path: Path to a test audio file
            
        Returns:
            True if diarization was successful, False otherwise
        """
        try:
            diarization = self.diarize(test_audio_path)
            segments = self.get_speaker_segments(diarization)
            
            if segments:
                logger.info(f"Test diarization successful. Found {len(segments)} speaker segments")
                # Log a few sample segments
                for i, segment in enumerate(segments[:3]):
                    logger.info(f"Segment {i+1}: Speaker {segment['speaker']} from {segment['start']:.2f}s to {segment['end']:.2f}s")
                return True
            else:
                logger.warning("Test diarization produced no speaker segments")
                return False
        except Exception as e:
            logger.error(f"Test diarization failed: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    # This will only run when this file is executed directly
    import sys
    import os
    
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
    
    diarization_model = PyannoteDiarization(hf_token=hf_token)
    success = diarization_model.test_diarization(test_file)
    
    if success:
        print("✅ Pyannote diarization test successful!")
    else:
        print("❌ Pyannote diarization test failed!")
        sys.exit(1)
