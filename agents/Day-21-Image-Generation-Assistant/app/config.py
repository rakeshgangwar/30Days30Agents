"""Configuration module for Image Generation Assistant."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class ImageGenerationConfig:
    """Configuration for image generation parameters."""
    default_model: str = "dall-e-3"
    default_size: str = "1024x1024"
    default_quality: str = "standard"
    default_style: str = "vivid"
    max_prompt_length: int = 1000
    max_negative_prompt_length: int = 500

@dataclass
class StorageConfig:
    """Configuration for image storage."""
    images_dir: Path = Path("generated_images")
    metadata_dir: Path = Path("metadata")
    max_storage_mb: int = 1000
    cleanup_after_days: int = 30

@dataclass
class LLMConfig:
    """Configuration for LLM model used for prompt enhancement."""
    model: str = "openai:gpt-4o-mini"
    max_tokens: int = 500
    temperature: float = 0.7

@dataclass
class APIConfig:
    """Configuration for external API settings."""
    openai_api_key: Optional[str] = None
    fal_api_key: Optional[str] = None
    rate_limit_requests_per_minute: int = 50
    request_timeout: int = 60

@dataclass
class FalConfig:
    """Configuration specific to Fal.ai integration."""
    default_model: str = "fal-ai/fast-sdxl"
    enable_queue_monitoring: bool = True
    max_queue_wait_time: int = 300  # 5 minutes
    enable_streaming: bool = True

@dataclass
class AppConfig:
    """Main application configuration."""
    image_generation: ImageGenerationConfig
    storage: StorageConfig
    llm: LLMConfig
    api: APIConfig
    fal: FalConfig
    
    def __post_init__(self):
        """Initialize directories and validate configuration."""
        # Create directories if they don't exist
        self.storage.images_dir.mkdir(exist_ok=True)
        self.storage.metadata_dir.mkdir(exist_ok=True)
        
        # Set API keys from environment
        if not self.api.openai_api_key:
            self.api.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api.fal_api_key:
            self.api.fal_api_key = os.getenv("FAL_KEY")
            
        # At least one API key must be present
        if not self.api.openai_api_key and not self.api.fal_api_key:
            raise ValueError("Either OPENAI_API_KEY or FAL_KEY environment variable is required")

# Global configuration instance
def get_config() -> AppConfig:
    """Get the global application configuration."""
    return AppConfig(
        image_generation=ImageGenerationConfig(),
        storage=StorageConfig(),
        llm=LLMConfig(),
        api=APIConfig(),
        fal=FalConfig()
    )

# Supported image generation models (expanded with Fal.ai models)
SUPPORTED_MODELS = {
    # OpenAI DALL-E models
    "dall-e-3": {
        "provider": "openai",
        "sizes": ["1024x1024", "1792x1024", "1024x1792"],
        "qualities": ["standard", "hd"],
        "styles": ["vivid", "natural"],
        "max_images": 1
    },
    "dall-e-2": {
        "provider": "openai",
        "sizes": ["256x256", "512x512", "1024x1024"],
        "qualities": ["standard"],
        "styles": ["natural"],
        "max_images": 10
    },
    
    # Fal.ai models
    "fal-ai/fast-sdxl": {
        "provider": "fal",
        "sizes": ["square", "portrait", "landscape", "square_hd"],
        "qualities": ["standard"],
        "styles": ["base", "photographic", "anime", "digital-art", "comic-book", "fantasy-art", "line-art", "neon-punk"],
        "max_images": 4,
        "supports_negative_prompt": True
    },
    "fal-ai/flux/schnell": {
        "provider": "fal",
        "sizes": ["square", "portrait", "landscape", "square_hd"],
        "qualities": ["standard"],
        "styles": ["natural"],
        "max_images": 4,
        "supports_negative_prompt": False
    },
    "fal-ai/flux/dev": {
        "provider": "fal",
        "sizes": ["square", "portrait", "landscape", "square_hd"],
        "qualities": ["standard"],
        "styles": ["natural"],
        "max_images": 4,
        "supports_negative_prompt": False,
        "requires_premium": True
    },
    "fal-ai/stable-diffusion-v3-medium": {
        "provider": "fal",
        "sizes": ["square", "portrait", "landscape"],
        "qualities": ["standard"],
        "styles": ["natural"],
        "max_images": 4,
        "supports_negative_prompt": True
    },
    "fal-ai/aura-flow": {
        "provider": "fal",
        "sizes": ["square", "portrait", "landscape"],
        "qualities": ["standard"],
        "styles": ["natural"],
        "max_images": 4,
        "supports_negative_prompt": False
    }
}

# Enhanced style keywords (compatible with both OpenAI and Fal.ai)
STYLE_KEYWORDS = {
    "photorealistic": "photorealistic, high detail, professional photography, 8k resolution",
    "artistic": "artistic, creative, expressive, masterpiece",
    "cartoon": "cartoon style, animated, colorful, comic book art",
    "oil_painting": "oil painting, classical art style, textured, renaissance",
    "watercolor": "watercolor painting, soft, flowing, delicate",
    "digital_art": "digital art, modern, clean, concept art",
    "vintage": "vintage style, retro, nostalgic, aged",
    "minimalist": "minimalist, simple, clean lines, geometric",
    "cyberpunk": "cyberpunk, neon, futuristic, dark, sci-fi",
    "fantasy": "fantasy art, magical, ethereal, mystical",
    "anime": "anime style, manga, japanese animation, cel-shaded",
    "photographic": "photographic, realistic, detailed, sharp",
    "comic_book": "comic book style, bold colors, dramatic lighting",
    "line_art": "line art, black and white, sketch, outline",
    "neon_punk": "neon punk, vibrant colors, electric, glow effects"
}

# Fal.ai specific image size mappings
FAL_SIZE_MAPPINGS = {
    "square": "square",
    "portrait": "portrait",
    "landscape": "landscape", 
    "square_hd": "square_hd",
    "1024x1024": "square",
    "1024x1792": "portrait",
    "1792x1024": "landscape",
    "512x512": "square",
    "768x1024": "portrait",
    "1024x768": "landscape"
} 