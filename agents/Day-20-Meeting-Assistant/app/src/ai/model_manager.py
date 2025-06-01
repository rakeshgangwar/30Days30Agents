import os
import torch
import platform
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, Union
from loguru import logger

from .whisper_model import WhisperModel
from .pyannote_model import PyannoteDiarization

class AIModelManager:
    """Manager for AI models used in the Meeting Assistant.
    
    This class handles the loading, caching, and configuration of Whisper and Pyannote models.
    It provides a unified interface for transcription and speaker diarization.
    """
    
    def __init__(
        self,
        whisper_model_size: str = "base",
        device: Optional[str] = None,
        hf_token: Optional[str] = None,
        cache_dir: Optional[Union[str, Path]] = None
    ):
        """
        Initialize the AI Model Manager.
        
        Args:
            whisper_model_size: Size of the Whisper model to use ('tiny', 'base', 'small', 'medium', 'large')
            device: Device to run models on. If None, will use CUDA if available, otherwise CPU
            hf_token: HuggingFace token for accessing Pyannote models
            cache_dir: Directory to cache models. If None, uses default location
        """
        # Set up cache directory
        self.cache_dir = Path(cache_dir) if cache_dir else Path(os.environ.get(
            "MODEL_CACHE_DIR", Path.home() / ".cache" / "meeting_assistant" / "models"
        ))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine device
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Get HuggingFace token
        self.hf_token = hf_token or os.environ.get("HF_TOKEN")
        
        # Initialize models (but don't load them yet)
        self.whisper_model = WhisperModel(model_size=whisper_model_size, device=self.device)
        self.diarization_model = PyannoteDiarization(device=self.device, hf_token=self.hf_token)
        
        # Log system information
        self._log_system_info()
    
    def _log_system_info(self):
        """Log information about the system and GPU availability."""
        logger.info(f"System: {platform.system()} {platform.release()} ({platform.machine()})")
        logger.info(f"Python: {platform.python_version()}")
        logger.info(f"PyTorch: {torch.__version__}")
        logger.info(f"Models cache directory: {self.cache_dir}")
        
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            logger.info(f"GPU(s) available: {gpu_count}")
            for i in range(gpu_count):
                gpu_name = torch.cuda.get_device_name(i)
                gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024 ** 3)  # GB
                logger.info(f"  GPU {i}: {gpu_name} with {gpu_memory:.2f} GB memory")
        else:
            logger.warning("No GPU detected. Models will run on CPU, which may be slow.")
    
    def load_models(self) -> Tuple[bool, bool]:
        """Load both Whisper and Pyannote models.
        
        Returns:
            Tuple of (whisper_success, pyannote_success)
        """
        whisper_success = self.whisper_model.load_model()
        pyannote_success = self.diarization_model.load_model()
        
        return whisper_success, pyannote_success
    
    def process_audio(
        self, 
        audio_path: Union[str, Path], 
        whisper_kwargs: Optional[Dict[str, Any]] = None,
        diarization_kwargs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process an audio file with both transcription and speaker diarization.
        
        Args:
            audio_path: Path to the audio file to process
            whisper_kwargs: Additional arguments for Whisper transcription
            diarization_kwargs: Additional arguments for Pyannote diarization
            
        Returns:
            Dictionary containing both transcription and diarization results
        """
        whisper_kwargs = whisper_kwargs or {}
        diarization_kwargs = diarization_kwargs or {}
        
        # Perform transcription
        logger.info(f"Processing audio file: {audio_path}")
        transcription = self.whisper_model.transcribe(audio_path, **whisper_kwargs)
        
        # Perform diarization
        diarization = self.diarization_model.diarize(audio_path, **diarization_kwargs)
        speaker_segments = self.diarization_model.get_speaker_segments(diarization)
        
        # Combine results
        result = {
            "transcription": transcription,
            "speaker_segments": speaker_segments
        }
        
        logger.success(f"Successfully processed audio file: {audio_path}")
        return result
    
    def test_models(self, test_audio_path: Union[str, Path]) -> Tuple[bool, bool]:
        """Test both Whisper and Pyannote models with a sample audio file.
        
        Args:
            test_audio_path: Path to a test audio file
            
        Returns:
            Tuple of (whisper_success, pyannote_success)
        """
        whisper_success = self.whisper_model.test_transcription(test_audio_path)
        pyannote_success = self.diarization_model.test_diarization(test_audio_path)
        
        return whisper_success, pyannote_success

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
        print("u26a0ufe0f HF_TOKEN environment variable not set")
        print("You need to set this to access Pyannote models")
        print("Example: export HF_TOKEN=your_token_here")
        sys.exit(1)
    
    # Initialize and test models
    model_manager = AIModelManager(whisper_model_size="base", hf_token=hf_token)
    whisper_success, pyannote_success = model_manager.test_models(test_file)
    
    if whisper_success and pyannote_success:
        print("u2705 All models tested successfully!")
    else:
        if not whisper_success:
            print("u274c Whisper model test failed!")
        if not pyannote_success:
            print("u274c Pyannote model test failed!")
        sys.exit(1)
