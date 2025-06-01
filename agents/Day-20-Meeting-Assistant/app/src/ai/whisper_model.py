import os
import torch
import logging
from pathlib import Path
from typing import Optional, Union, Dict, Any
from loguru import logger

class WhisperModel:
    """Wrapper for OpenAI's Whisper model for speech-to-text transcription."""
    
    def __init__(self, model_size: str = "base", device: Optional[str] = None):
        """
        Initialize the Whisper model.
        
        Args:
            model_size: Size of the Whisper model to use. Options: 'tiny', 'base', 'small', 'medium', 'large'
            device: Device to run the model on. If None, will use CUDA if available, otherwise CPU.
        """
        self.model_size = model_size
        self.model = None
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Initializing Whisper model (size={model_size}) on device: {self.device}")
        
        # Create cache directory if it doesn't exist
        self.cache_dir = Path(os.environ.get("MODEL_CACHE_DIR", Path.home() / ".cache" / "meeting_assistant" / "models"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Log GPU information if available
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)  # Convert to GB
            logger.info(f"GPU detected: {gpu_name} with {gpu_memory:.2f} GB memory")
        else:
            logger.warning("No GPU detected. Using CPU for Whisper, which may be slow.")
    
    def load_model(self):
        """Load the Whisper model into memory."""
        try:
            import whisper
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size, device=self.device, download_root=str(self.cache_dir))
            logger.success(f"Successfully loaded Whisper {self.model_size} model")
            return True
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {str(e)}")
            return False
    
    def transcribe(self, audio_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """Transcribe an audio file using the Whisper model.
        
        Args:
            audio_path: Path to the audio file to transcribe
            **kwargs: Additional arguments to pass to whisper.transcribe()
                      See https://github.com/openai/whisper/blob/main/whisper/transcribe.py
        
        Returns:
            Dictionary containing the transcription results
        """
        if self.model is None:
            success = self.load_model()
            if not success:
                raise RuntimeError("Failed to load Whisper model. Cannot transcribe.")
        
        try:
            logger.info(f"Transcribing audio file: {audio_path}")
            result = self.model.transcribe(str(audio_path), **kwargs)
            logger.success(f"Successfully transcribed audio file: {audio_path}")
            return result
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise
    
    def test_transcription(self, test_audio_path: Union[str, Path]) -> bool:
        """Test the transcription functionality with a sample audio file.
        
        Args:
            test_audio_path: Path to a test audio file
            
        Returns:
            True if transcription was successful, False otherwise
        """
        try:
            result = self.transcribe(test_audio_path)
            if result and "text" in result and result["text"].strip():
                logger.info(f"Test transcription successful. Sample text: {result['text'][:100]}...")
                return True
            else:
                logger.warning("Test transcription produced empty or invalid results")
                return False
        except Exception as e:
            logger.error(f"Test transcription failed: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    # This will only run when this file is executed directly
    import sys
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    else:
        print("Please provide a path to a test audio file as an argument")
        sys.exit(1)
    
    whisper_model = WhisperModel(model_size="base")
    success = whisper_model.test_transcription(test_file)
    
    if success:
        print("✅ Whisper model test successful!")
    else:
        print("❌ Whisper model test failed!")
        sys.exit(1)
