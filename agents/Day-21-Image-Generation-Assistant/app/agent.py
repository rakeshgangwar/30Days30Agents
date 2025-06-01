"""Image Generation Assistant Agent using Pydantic AI."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
import json

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, format_as_xml

from config import get_config, STYLE_KEYWORDS, SUPPORTED_MODELS
from models import (
    ImageGenerationParams, AgentResponse, PromptEnhancementRequest,
    ImageUpscaleRequest, ImageVariationRequest, ImageSize, ImageQuality,
    ImageStyle, FalImageSize, FalImageStyle, GenerationModel, ProviderType
)
from services import (
    UnifiedImageGenerationService, PromptEnhancementService,
    ImageStorageService, ImageProcessingService
)


@dataclass
class ImageAssistantDeps:
    """Dependencies for the Image Generation Assistant."""
    generation_service: UnifiedImageGenerationService
    enhancement_service: PromptEnhancementService
    storage_service: ImageStorageService
    processing_service: ImageProcessingService


class GenerateImageRequest(BaseModel):
    """Request to generate an image."""
    prompt: str = Field(..., description="The text prompt for image generation")
    style: Optional[str] = Field(None, description="Artistic style preference")
    size: Optional[str] = Field(None, description="Image size (e.g., '1024x1024', 'landscape', 'portrait')")
    quality: Optional[str] = Field(None, description="Image quality ('standard' or 'hd')")
    model: Optional[str] = Field(None, description="Generation model to use")
    negative_prompt: Optional[str] = Field(None, description="What to avoid in the image")
    num_images: Optional[int] = Field(1, description="Number of images to generate (1-10)")
    enhance_prompt: bool = Field(True, description="Whether to enhance the prompt using AI")
    seed: Optional[int] = Field(None, description="Random seed for reproducible results (Fal.ai models)")
    guidance_scale: Optional[float] = Field(None, description="Guidance scale for Fal.ai models (1.0-20.0)")
    num_inference_steps: Optional[int] = Field(None, description="Number of inference steps (1-100)")


class EnhancePromptRequest(BaseModel):
    """Request to enhance a prompt."""
    prompt: str = Field(..., description="The original prompt to enhance")
    style_preference: Optional[str] = Field(None, description="Preferred artistic style")
    additional_context: Optional[str] = Field(None, description="Additional context or requirements")
    target_provider: Optional[str] = Field(None, description="Target provider (openai or fal)")


class ViewHistoryRequest(BaseModel):
    """Request to view generation history."""
    limit: Optional[int] = Field(10, description="Number of recent generations to show")
    search_term: Optional[str] = Field(None, description="Search term to filter history")
    provider: Optional[str] = Field(None, description="Filter by provider (openai or fal)")


class UpscaleImageRequest(BaseModel):
    """Request to upscale an image."""
    image_path: str = Field(..., description="Path to the image to upscale")
    scale_factor: int = Field(2, description="Scaling factor (2, 3, or 4)")
    enhance_quality: bool = Field(True, description="Whether to apply quality enhancement")


class CreateVariationsRequest(BaseModel):
    """Request to create image variations."""
    image_path: str = Field(..., description="Path to the base image")
    num_variations: int = Field(3, description="Number of variations to create")
    prompt_variation: Optional[str] = Field(None, description="Variation in the prompt")


# Define output types for different operations
ImageGenerationOutput = Union[GenerateImageRequest, EnhancePromptRequest, ViewHistoryRequest, 
                             UpscaleImageRequest, CreateVariationsRequest]

# Create the main Image Generation Assistant agent
image_assistant = Agent[ImageAssistantDeps, AgentResponse](
    'openai:gpt-4o-mini',
    deps_type=ImageAssistantDeps,
    output_type=AgentResponse,
    system_prompt="""You are an AI Image Generation Assistant supporting both OpenAI DALL-E and Fal.ai models. You help users create, enhance, and manage AI-generated images.

Your capabilities include:
1. Generating images from text descriptions using multiple providers:
   - OpenAI: DALL-E 3, DALL-E 2
   - Fal.ai: fast-sdxl, flux/schnell, flux/dev, stable-diffusion-v3-medium, aura-flow
2. Enhancing user prompts to create better, more detailed descriptions
3. Managing image generation parameters (size, style, quality, advanced Fal.ai parameters)
4. Viewing and searching generation history (filterable by provider)
5. Upscaling existing images
6. Creating variations of existing images

Key guidelines:
- Always be helpful and creative
- Ask clarifying questions if the user's request is unclear
- Suggest improvements to prompts when appropriate
- Explain the differences between providers and models when needed
- Provide information about different styles, sizes, and options available
- Be encouraging and supportive of creative endeavors

Provider-specific information:
**OpenAI DALL-E:**
- DALL-E 3: Latest model, best quality, 1 image per request
- DALL-E 2: Faster, up to 10 images per request
- Sizes: 1024x1024, 1792x1024, 1024x1792
- Styles: vivid, natural

**Fal.ai Models:**
- fast-sdxl: Fast SDXL, supports negative prompts, many styles
- flux/schnell: Fast Flux model, high quality
- flux/dev: Development Flux model (premium)
- stable-diffusion-v3-medium: Latest Stable Diffusion
- aura-flow: Creative flow model
- Sizes: square, portrait, landscape, square_hd
- Advanced parameters: seed, guidance_scale, num_inference_steps

Available styles: photorealistic, artistic, cartoon, oil_painting, watercolor, digital_art, vintage, minimalist, cyberpunk, fantasy, anime, photographic, comic_book, line_art, neon_punk

Always respond with structured data that includes your response message and any relevant suggestions."""
)


@image_assistant.tool
async def generate_image(ctx: RunContext[ImageAssistantDeps], request: GenerateImageRequest) -> AgentResponse:
    """Generate images based on user specifications."""
    try:
        # Parse and validate parameters
        params = _parse_generation_params(request)
        
        # Determine target provider for prompt enhancement
        target_provider = params.get_provider()
        
        # Enhance prompt if requested
        enhanced_prompt = params.prompt
        if request.enhance_prompt:
            enhancement_request = PromptEnhancementRequest(
                original_prompt=params.prompt,
                style_preference=request.style,
                enhance_creativity=True,
                target_provider=target_provider
            )
            enhancement_result = await ctx.deps.enhancement_service.enhance_prompt(enhancement_request)
            enhanced_prompt = enhancement_result.enhanced_prompt
            params.prompt = enhanced_prompt
        
        # Generate images using unified service
        generation_result = await ctx.deps.generation_service.generate_images(params)
        
        if not generation_result.success:
            return AgentResponse(
                success=False,
                message=f"Failed to generate images: {generation_result.error_message}",
                suggestions=[
                    "Try simplifying your prompt", 
                    "Check your parameters", 
                    "Try a different model",
                    "Ensure API keys are configured"
                ]
            )
        
        # Save images locally
        saved_result = await ctx.deps.storage_service.save_images(generation_result)
        
        # Prepare response
        image_paths = [img.local_path for img in saved_result.images if img.local_path]
        
        provider_name = generation_result.provider.value if generation_result.provider else "unknown"
        message = f"Successfully generated {len(saved_result.images)} image(s) using {provider_name.upper()} ({params.model.value})"
        message += f"\n\nPrompt: '{request.prompt}'"
        
        if request.enhance_prompt and enhanced_prompt != request.prompt:
            message += f"\n\nEnhanced prompt: '{enhanced_prompt}'"
        
        # Add queue information for Fal.ai
        if generation_result.provider == ProviderType.FAL and generation_result.queue_position:
            message += f"\n\nQueue position was: {generation_result.queue_position}"
        
        response_data = {
            "generation_id": saved_result.request_id,
            "original_prompt": request.prompt,
            "enhanced_prompt": enhanced_prompt if request.enhance_prompt else None,
            "parameters": params.dict(),
            "generation_time": saved_result.generation_time_seconds,
            "provider": provider_name,
            "model": params.model.value
        }
        
        # Add Fal.ai specific data
        if generation_result.provider == ProviderType.FAL:
            response_data["queue_position"] = generation_result.queue_position
            if saved_result.images and saved_result.images[0].seed:
                response_data["seed"] = saved_result.images[0].seed
        
        suggestions = [
            "Try creating variations of this image",
            "Upscale the image for higher resolution"
        ]
        
        # Add provider-specific suggestions
        if generation_result.provider == ProviderType.OPENAI:
            suggestions.append("Try the same prompt with Fal.ai models for different styles")
        elif generation_result.provider == ProviderType.FAL:
            suggestions.extend([
                "Try adjusting guidance_scale or num_inference_steps",
                "Use the seed to reproduce similar results"
            ])
        
        return AgentResponse(
            success=True,
            message=message,
            data=response_data,
            images=image_paths,
            suggestions=suggestions
        )
        
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Error during image generation: {str(e)}",
            suggestions=["Check your prompt and parameters", "Try again with simpler requirements"]
        )


@image_assistant.tool
async def enhance_prompt(ctx: RunContext[ImageAssistantDeps], request: EnhancePromptRequest) -> AgentResponse:
    """Enhance a user's prompt for better image generation."""
    try:
        # Parse target provider
        target_provider = None
        if request.target_provider:
            if request.target_provider.lower() == "openai":
                target_provider = ProviderType.OPENAI
            elif request.target_provider.lower() == "fal":
                target_provider = ProviderType.FAL
        
        enhancement_request = PromptEnhancementRequest(
            original_prompt=request.prompt,
            style_preference=request.style_preference,
            additional_context=request.additional_context,
            enhance_creativity=True,
            target_provider=target_provider
        )
        
        result = await ctx.deps.enhancement_service.enhance_prompt(enhancement_request)
        
        message = f"Enhanced your prompt"
        if target_provider:
            message += f" (optimized for {target_provider.value.upper()})"
        message += f":\n\nOriginal: '{result.original_prompt}'\nEnhanced: '{result.enhanced_prompt}'\n\nReason: {result.enhancement_reason}"
        
        response_data = {
            "original_prompt": result.original_prompt,
            "enhanced_prompt": result.enhanced_prompt,
            "enhancement_reason": result.enhancement_reason,
            "target_provider": target_provider.value if target_provider else None
        }
        
        if result.suggested_params:
            response_data["suggested_params"] = result.suggested_params
            message += f"\n\nSuggested parameters: {json.dumps(result.suggested_params, indent=2)}"
        
        suggestions = [
            "Use this enhanced prompt to generate images",
            "Try the prompt with different models",
            "Further customize the suggested parameters"
        ]
        
        if not target_provider:
            suggestions.append("Specify a target provider (openai or fal) for optimized enhancement")
        
        return AgentResponse(
            success=True,
            message=message,
            data=response_data,
            suggestions=suggestions
        )
        
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Failed to enhance prompt: {str(e)}",
            suggestions=["Try a simpler prompt", "Provide more specific style preferences"]
        )


@image_assistant.tool
async def view_history(ctx: RunContext[ImageAssistantDeps], request: ViewHistoryRequest) -> AgentResponse:
    """View or search generation history."""
    try:
        # Parse provider filter
        provider_filter = None
        if request.provider:
            if request.provider.lower() == "openai":
                provider_filter = ProviderType.OPENAI
            elif request.provider.lower() == "fal":
                provider_filter = ProviderType.FAL
        
        if request.search_term:
            generations = ctx.deps.storage_service.search_history(request.search_term, provider_filter)
            filter_desc = f"matching '{request.search_term}'"
            if provider_filter:
                filter_desc += f" from {provider_filter.value.upper()}"
            message = f"Found {len(generations)} generations {filter_desc}:"
        else:
            generations = ctx.deps.storage_service.get_history(request.limit, provider_filter)
            filter_desc = ""
            if provider_filter:
                filter_desc = f" from {provider_filter.value.upper()}"
            message = f"Your {len(generations)} most recent generations{filter_desc}:"
        
        if not generations:
            return AgentResponse(
                success=True,
                message="No generations found matching your criteria.",
                suggestions=[
                    "Generate some images first", 
                    "Try a different search term",
                    "Remove provider filter to see all generations"
                ]
            )
        
        history_data = []
        for gen in generations:
            history_data.append({
                "id": gen.request_id,
                "prompt": gen.original_prompt,
                "timestamp": gen.timestamp.isoformat(),
                "num_images": len(gen.images),
                "success": gen.success,
                "provider": gen.provider.value if gen.provider else "unknown",
                "model": gen.parameters.model.value if gen.parameters else "unknown"
            })
        
        # Build detailed message
        details = []
        for i, gen in enumerate(generations[:5], 1):  # Show details for first 5
            status = "✓" if gen.success else "✗"
            provider = gen.provider.value if gen.provider else "?"
            model = gen.parameters.model.value if gen.parameters else "unknown"
            details.append(f"{i}. {status} [{provider.upper()}:{model}] \"{gen.original_prompt[:40]}{'...' if len(gen.original_prompt) > 40 else ''}\" ({gen.timestamp.strftime('%Y-%m-%d %H:%M')})")
        
        message += "\n\n" + "\n".join(details)
        if len(generations) > 5:
            message += f"\n... and {len(generations) - 5} more"
        
        suggestions = [
            "Generate variations of previous images",
            "Upscale your favorite images",
            "Search for specific themes"
        ]
        
        if not provider_filter:
            suggestions.extend([
                "Filter by provider: add 'provider: openai' or 'provider: fal'",
                "Compare results between different providers"
            ])
        
        return AgentResponse(
            success=True,
            message=message,
            data={
                "history": history_data,
                "provider_filter": provider_filter.value if provider_filter else None
            },
            suggestions=suggestions
        )
        
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Failed to retrieve history: {str(e)}",
            suggestions=["Try again later", "Check if any images have been generated"]
        )


@image_assistant.tool
async def upscale_image(ctx: RunContext[ImageAssistantDeps], request: UpscaleImageRequest) -> AgentResponse:
    """Upscale an existing image."""
    try:
        image_path = Path(request.image_path)
        if not image_path.exists():
            return AgentResponse(
                success=False,
                message=f"Image not found at path: {request.image_path}",
                suggestions=["Check the file path", "Use view_history to find correct paths"]
            )
        
        upscale_request = ImageUpscaleRequest(
            image_path=image_path,
            scale_factor=request.scale_factor,
            enhance_quality=request.enhance_quality
        )
        
        upscaled_path = await ctx.deps.processing_service.upscale_image(upscale_request)
        
        return AgentResponse(
            success=True,
            message=f"Successfully upscaled image by {request.scale_factor}x. Original: {image_path.name}, Upscaled: {upscaled_path.name}",
            data={
                "original_path": str(image_path),
                "upscaled_path": str(upscaled_path),
                "scale_factor": request.scale_factor
            },
            images=[upscaled_path],
            suggestions=[
                "Compare with the original image",
                "Use the upscaled image for further processing",
                "Create variations of the upscaled image"
            ]
        )
        
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Failed to upscale image: {str(e)}",
            suggestions=["Check if the image file is valid", "Try a lower scale factor"]
        )


@image_assistant.tool
async def create_variations(ctx: RunContext[ImageAssistantDeps], request: CreateVariationsRequest) -> AgentResponse:
    """Create variations of an existing image."""
    try:
        image_path = Path(request.image_path)
        if not image_path.exists():
            return AgentResponse(
                success=False,
                message=f"Image not found at path: {request.image_path}",
                suggestions=["Check the file path", "Use view_history to find correct paths"]
            )
        
        variation_request = ImageVariationRequest(
            base_image_path=image_path,
            num_variations=request.num_variations,
            prompt_variation=request.prompt_variation
        )
        
        variation_paths = await ctx.deps.processing_service.create_variations(variation_request)
        
        return AgentResponse(
            success=True,
            message=f"Successfully created {len(variation_paths)} variations of {image_path.name}",
            data={
                "base_image": str(image_path),
                "variations": [str(p) for p in variation_paths],
                "num_variations": len(variation_paths)
            },
            images=variation_paths,
            suggestions=[
                "Compare the variations with the original",
                "Generate more variations with different prompts",
                "Upscale your favorite variations"
            ]
        )
        
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Failed to create variations: {str(e)}",
            suggestions=["Check if the image file is valid", "Try with a different base image"]
        )


def _parse_generation_params(request: GenerateImageRequest) -> ImageGenerationParams:
    """Parse and validate generation parameters from request."""
    # Parse model
    model = GenerationModel.DALL_E_3  # default
    if request.model:
        # Try to match model name
        for model_enum in GenerationModel:
            if request.model.lower() in model_enum.value.lower() or model_enum.value == request.model:
                model = model_enum
                break
    
    # Parse size based on model provider
    provider = ProviderType.OPENAI if not model.value.startswith("fal-ai/") else ProviderType.FAL
    size = "1024x1024"  # default
    
    if request.size:
        if provider == ProviderType.FAL:
            # Fal.ai size mappings
            fal_size_map = {
                "square": "square",
                "portrait": "portrait", 
                "landscape": "landscape",
                "square_hd": "square_hd",
                "1024x1024": "square",
                "1024x1792": "portrait",
                "1792x1024": "landscape"
            }
            size = fal_size_map.get(request.size.lower(), request.size)
        else:
            # OpenAI size mappings
            openai_size_map = {
                "square": "1024x1024",
                "landscape": "1792x1024",
                "portrait": "1024x1792",
                "wide": "1792x1024",
                "tall": "1024x1792"
            }
            size = openai_size_map.get(request.size.lower(), request.size)
    
    # Parse quality
    quality = ImageQuality.STANDARD
    if request.quality and request.quality.lower() in [q.value for q in ImageQuality]:
        quality = ImageQuality(request.quality.lower())
    
    # Parse style based on provider
    style = "vivid"  # default
    if request.style:
        if provider == ProviderType.FAL:
            # Map to Fal.ai styles
            fal_style_map = {
                "photorealistic": "photographic",
                "realistic": "photographic", 
                "photo": "photographic",
                "cartoon": "anime",
                "digital": "digital-art",
                "comic": "comic-book",
                "fantasy": "fantasy-art",
                "line": "line-art",
                "neon": "neon-punk",
                "cyberpunk": "neon-punk"
            }
            style = fal_style_map.get(request.style.lower(), request.style.lower())
        else:
            # Map to OpenAI styles
            openai_style_map = {
                "realistic": "natural",
                "photorealistic": "natural",
                "photo": "natural",
                "creative": "vivid",
                "artistic": "vivid"
            }
            style = openai_style_map.get(request.style.lower(), request.style.lower())
            if style not in ["vivid", "natural"]:
                style = "vivid"  # fallback
    
    return ImageGenerationParams(
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        model=model,
        size=size,
        quality=quality,
        style=style,
        num_images=min(max(request.num_images or 1, 1), 10),
        seed=request.seed,
        guidance_scale=request.guidance_scale,
        num_inference_steps=request.num_inference_steps
    )


# Helper functions for agent interaction
async def run_image_assistant(user_input: str) -> AgentResponse:
    """Run the image assistant with user input."""
    # Initialize services
    deps = ImageAssistantDeps(
        generation_service=UnifiedImageGenerationService(),
        enhancement_service=PromptEnhancementService(),
        storage_service=ImageStorageService(),
        processing_service=ImageProcessingService()
    )
    
    try:
        # Run the agent
        result = await image_assistant.run(user_input, deps=deps)
        return result.output
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Assistant error: {str(e)}",
            suggestions=["Try rephrasing your request", "Check your input format"]
        )


def run_image_assistant_sync(user_input: str) -> AgentResponse:
    """Run the image assistant synchronously."""
    # Initialize services
    deps = ImageAssistantDeps(
        generation_service=UnifiedImageGenerationService(),
        enhancement_service=PromptEnhancementService(),
        storage_service=ImageStorageService(),
        processing_service=ImageProcessingService()
    )
    
    try:
        # Run the agent synchronously
        result = image_assistant.run_sync(user_input, deps=deps)
        return result.output
    except Exception as e:
        return AgentResponse(
            success=False,
            message=f"Assistant error: {str(e)}",
            suggestions=["Try rephrasing your request", "Check your input format"]
        ) 