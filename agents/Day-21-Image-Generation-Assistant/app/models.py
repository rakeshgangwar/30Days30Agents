"""Data models for Image Generation Assistant."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, validator, HttpUrl


class ImageSize(str, Enum):
    """Supported image sizes."""
    SQUARE_256 = "256x256"
    SQUARE_512 = "512x512"
    SQUARE_1024 = "1024x1024"
    LANDSCAPE = "1792x1024"
    PORTRAIT = "1024x1792"


class FalImageSize(str, Enum):
    """Fal.ai specific image sizes."""
    SQUARE = "square"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    SQUARE_HD = "square_hd"


class ImageQuality(str, Enum):
    """Image quality options."""
    STANDARD = "standard"
    HD = "hd"


class ImageStyle(str, Enum):
    """Image style options."""
    VIVID = "vivid"
    NATURAL = "natural"


class FalImageStyle(str, Enum):
    """Fal.ai specific image styles."""
    BASE = "base"
    PHOTOGRAPHIC = "photographic"
    ANIME = "anime"
    DIGITAL_ART = "digital-art"
    COMIC_BOOK = "comic-book"
    FANTASY_ART = "fantasy-art"
    LINE_ART = "line-art"
    NEON_PUNK = "neon-punk"


class GenerationModel(str, Enum):
    """Supported image generation models."""
    DALL_E_3 = "dall-e-3"
    DALL_E_2 = "dall-e-2"
    FAL_FAST_SDXL = "fal-ai/fast-sdxl"
    FAL_FLUX_SCHNELL = "fal-ai/flux/schnell"
    FAL_FLUX_DEV = "fal-ai/flux/dev"
    FAL_SD3_MEDIUM = "fal-ai/stable-diffusion-v3-medium"
    FAL_AURA_FLOW = "fal-ai/aura-flow"


class ProviderType(str, Enum):
    """Image generation providers."""
    OPENAI = "openai"
    FAL = "fal"


class ImageGenerationParams(BaseModel):
    """Parameters for image generation."""
    prompt: str = Field(..., min_length=1, max_length=1000, description="The text prompt for image generation")
    negative_prompt: Optional[str] = Field(None, max_length=500, description="What to avoid in the image")
    model: GenerationModel = Field(GenerationModel.DALL_E_3, description="The model to use for generation")
    size: Union[ImageSize, FalImageSize, str] = Field("1024x1024", description="The size of the generated image")
    quality: ImageQuality = Field(ImageQuality.STANDARD, description="The quality of the generated image")
    style: Union[ImageStyle, FalImageStyle, str] = Field("vivid", description="The style of the generated image")
    num_images: int = Field(1, ge=1, le=10, description="Number of images to generate")
    seed: Optional[int] = Field(None, description="Random seed for reproducible results (Fal.ai models)")
    guidance_scale: Optional[float] = Field(None, ge=1.0, le=20.0, description="Guidance scale for Fal.ai models")
    num_inference_steps: Optional[int] = Field(None, ge=1, le=100, description="Number of inference steps for Fal.ai models")
    
    @validator('negative_prompt')
    def validate_negative_prompt(cls, v):
        """Validate negative prompt is not empty if provided."""
        if v is not None and len(v.strip()) == 0:
            return None
        return v

    def get_provider(self) -> ProviderType:
        """Get the provider type based on the model."""
        if self.model.value.startswith("fal-ai/"):
            return ProviderType.FAL
        else:
            return ProviderType.OPENAI

    def validate_params(self) -> bool:
        """Validate parameter combinations for the selected model."""
        from config import SUPPORTED_MODELS
        
        model_config = SUPPORTED_MODELS.get(self.model.value)
        if not model_config:
            return False
            
        # Check num_images limit
        max_images = model_config.get("max_images", 1)
        if self.num_images > max_images:
            return False
            
        return True

    def to_openai_params(self) -> Dict[str, Any]:
        """Convert to OpenAI API parameters."""
        params = {
            "model": self.model.value,
            "prompt": self.prompt,
            "n": self.num_images,
            "size": str(self.size),
            "quality": self.quality.value,
            "response_format": "url"
        }
        
        # Add style for DALL-E 3
        if self.model == GenerationModel.DALL_E_3:
            params["style"] = self.style
            
        return params

    def to_fal_params(self) -> Dict[str, Any]:
        """Convert to Fal.ai API parameters."""
        from config import FAL_SIZE_MAPPINGS
        
        params = {
            "prompt": self.prompt,
            "num_images": self.num_images,
        }
        
        # Map size
        if isinstance(self.size, str) and self.size in FAL_SIZE_MAPPINGS:
            params["image_size"] = FAL_SIZE_MAPPINGS[self.size]
        else:
            params["image_size"] = str(self.size)
            
        # Add style if not natural/base
        if self.style and self.style not in ["natural", "base", "vivid"]:
            params["style"] = self.style
            
        # Add negative prompt if supported
        if self.negative_prompt:
            params["negative_prompt"] = self.negative_prompt
            
        # Add optional Fal-specific parameters
        if self.seed is not None:
            params["seed"] = self.seed
        if self.guidance_scale is not None:
            params["guidance_scale"] = self.guidance_scale
        if self.num_inference_steps is not None:
            params["num_inference_steps"] = self.num_inference_steps
            
        return params


class GeneratedImage(BaseModel):
    """Represents a generated image."""
    url: Optional[HttpUrl] = Field(None, description="URL of the generated image")
    local_path: Optional[Path] = Field(None, description="Local file path of the saved image")
    revised_prompt: Optional[str] = Field(None, description="The revised prompt used by the model")
    seed: Optional[int] = Field(None, description="Seed used for generation (if available)")
    
    class Config:
        arbitrary_types_allowed = True


class ImageGenerationResult(BaseModel):
    """Result of an image generation request."""
    request_id: str = Field(..., description="Unique identifier for this generation request")
    images: List[GeneratedImage] = Field(..., description="List of generated images")
    original_prompt: str = Field(..., description="The original user prompt")
    enhanced_prompt: Optional[str] = Field(None, description="LLM-enhanced version of the prompt")
    parameters: ImageGenerationParams = Field(..., description="Parameters used for generation")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the image was generated")
    success: bool = Field(..., description="Whether the generation was successful")
    error_message: Optional[str] = Field(None, description="Error message if generation failed")
    generation_time_seconds: Optional[float] = Field(None, description="Time taken to generate the image")
    provider: Optional[ProviderType] = Field(None, description="Provider used for generation")
    queue_position: Optional[int] = Field(None, description="Queue position for Fal.ai requests")
    
    def save_metadata(self, metadata_dir: Path) -> Path:
        """Save generation metadata to a JSON file."""
        metadata_file = metadata_dir / f"{self.request_id}.json"
        
        # Convert to dict and handle Path serialization
        data = self.dict()
        for image in data["images"]:
            if image["local_path"]:
                image["local_path"] = str(image["local_path"])
        
        with open(metadata_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
            
        return metadata_file
    
    @classmethod
    def load_metadata(cls, metadata_file: Path) -> 'ImageGenerationResult':
        """Load generation metadata from a JSON file."""
        with open(metadata_file, 'r') as f:
            data = json.load(f)
            
        # Convert local_path strings back to Path objects
        for image in data["images"]:
            if image["local_path"]:
                image["local_path"] = Path(image["local_path"])
                
        return cls(**data)


class PromptEnhancementRequest(BaseModel):
    """Request for prompt enhancement using LLM."""
    original_prompt: str = Field(..., description="The original user prompt")
    style_preference: Optional[str] = Field(None, description="Preferred artistic style")
    additional_context: Optional[str] = Field(None, description="Additional context or requirements")
    enhance_creativity: bool = Field(True, description="Whether to enhance creativity and detail")
    target_provider: Optional[ProviderType] = Field(None, description="Target provider for optimization")


class PromptEnhancementResult(BaseModel):
    """Result of prompt enhancement."""
    original_prompt: str = Field(..., description="The original prompt")
    enhanced_prompt: str = Field(..., description="The enhanced prompt")
    enhancement_reason: str = Field(..., description="Explanation of what was enhanced")
    suggested_params: Optional[Dict[str, Any]] = Field(None, description="Suggested generation parameters")


class ImageHistory(BaseModel):
    """History of generated images."""
    total_images: int = Field(0, description="Total number of images generated")
    generations: List[ImageGenerationResult] = Field(default_factory=list, description="List of generation results")
    
    def add_generation(self, result: ImageGenerationResult):
        """Add a new generation result to history."""
        self.generations.append(result)
        self.total_images += len(result.images)
    
    def get_recent_generations(self, limit: int = 10) -> List[ImageGenerationResult]:
        """Get the most recent generation results."""
        return sorted(self.generations, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def search_by_prompt(self, search_term: str) -> List[ImageGenerationResult]:
        """Search generations by prompt content."""
        search_term = search_term.lower()
        return [
            gen for gen in self.generations 
            if search_term in gen.original_prompt.lower() 
            or (gen.enhanced_prompt and search_term in gen.enhanced_prompt.lower())
        ]

    def get_by_provider(self, provider: ProviderType) -> List[ImageGenerationResult]:
        """Get generations filtered by provider."""
        return [gen for gen in self.generations if gen.provider == provider]


class ImageUpscaleRequest(BaseModel):
    """Request for image upscaling."""
    image_path: Path = Field(..., description="Path to the image to upscale")
    scale_factor: int = Field(2, ge=2, le=4, description="Scaling factor (2x, 3x, or 4x)")
    enhance_quality: bool = Field(True, description="Whether to apply quality enhancement")
    
    class Config:
        arbitrary_types_allowed = True


class ImageVariationRequest(BaseModel):
    """Request for creating image variations."""
    base_image_path: Path = Field(..., description="Path to the base image")
    prompt_variation: Optional[str] = Field(None, description="Variation in the prompt")
    style_variation: Optional[str] = Field(None, description="Style variation to apply")
    num_variations: int = Field(3, ge=1, le=10, description="Number of variations to create")
    
    class Config:
        arbitrary_types_allowed = True


class FalQueueStatus(BaseModel):
    """Status of a Fal.ai queue request."""
    request_id: str = Field(..., description="Request ID")
    status: str = Field(..., description="Queue status")
    position: Optional[int] = Field(None, description="Position in queue")
    logs: Optional[List[Dict[str, Any]]] = Field(None, description="Processing logs")


class AgentResponse(BaseModel):
    """Response from the Image Generation Assistant."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message to the user")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")
    suggestions: Optional[List[str]] = Field(None, description="Suggested next actions")
    images: Optional[List[Path]] = Field(None, description="Paths to generated or processed images")
    
    class Config:
        arbitrary_types_allowed = True 