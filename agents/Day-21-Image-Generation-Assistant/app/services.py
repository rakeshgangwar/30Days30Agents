"""Service classes for Image Generation Assistant."""

import asyncio
import hashlib
import time
import uuid
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

import httpx
from PIL import Image
from openai import AsyncOpenAI

try:
    import fal_client
except ImportError:
    fal_client = None

from config import get_config, STYLE_KEYWORDS
from models import (
    ImageGenerationParams, ImageGenerationResult, GeneratedImage,
    PromptEnhancementRequest, PromptEnhancementResult,
    ImageHistory, ImageUpscaleRequest, ImageVariationRequest,
    ProviderType, FalQueueStatus
)


class ImageGenerationService:
    """Service for generating images using OpenAI's DALL-E models."""
    
    def __init__(self):
        self.config = get_config()
        if self.config.api.openai_api_key:
            self.client = AsyncOpenAI(api_key=self.config.api.openai_api_key)
        else:
            self.client = None
        self.rate_limiter = RateLimiter(self.config.api.rate_limit_requests_per_minute)
    
    async def generate_images(self, params: ImageGenerationParams) -> ImageGenerationResult:
        """Generate images using the specified parameters."""
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Check if OpenAI client is available
            if not self.client:
                return ImageGenerationResult(
                    request_id=request_id,
                    images=[],
                    original_prompt=params.prompt,
                    parameters=params,
                    success=False,
                    error_message="OpenAI API key not configured",
                    provider=ProviderType.OPENAI
                )
            
            # Validate parameters
            if not params.validate_params():
                return ImageGenerationResult(
                    request_id=request_id,
                    images=[],
                    original_prompt=params.prompt,
                    parameters=params,
                    success=False,
                    error_message="Invalid parameter combination for the selected model",
                    provider=ProviderType.OPENAI
                )
            
            # Apply rate limiting
            await self.rate_limiter.acquire()
            
            # Convert parameters to OpenAI format
            openai_params = params.to_openai_params()
            
            # Prepare the prompt (combine main prompt with negative prompt if provided)
            final_prompt = params.prompt
            if params.negative_prompt:
                final_prompt += f" (avoid: {params.negative_prompt})"
            openai_params["prompt"] = final_prompt
            
            # Call OpenAI API
            response = await self.client.images.generate(**openai_params)
            
            # Process response
            images = []
            for img_data in response.data:
                generated_image = GeneratedImage(
                    url=img_data.url,
                    revised_prompt=getattr(img_data, 'revised_prompt', None)
                )
                images.append(generated_image)
            
            generation_time = time.time() - start_time
            
            return ImageGenerationResult(
                request_id=request_id,
                images=images,
                original_prompt=params.prompt,
                parameters=params,
                success=True,
                generation_time_seconds=generation_time,
                provider=ProviderType.OPENAI
            )
            
        except Exception as e:
            generation_time = time.time() - start_time
            return ImageGenerationResult(
                request_id=request_id,
                images=[],
                original_prompt=params.prompt,
                parameters=params,
                success=False,
                error_message=str(e),
                generation_time_seconds=generation_time,
                provider=ProviderType.OPENAI
            )


class FalImageGenerationService:
    """Service for generating images using Fal.ai models."""
    
    def __init__(self):
        self.config = get_config()
        # Set up fal_client environment if API key is available
        if fal_client and self.config.api.fal_api_key:
            # Set the FAL_KEY environment variable for fal_client
            os.environ["FAL_KEY"] = self.config.api.fal_api_key
        self.rate_limiter = RateLimiter(self.config.api.rate_limit_requests_per_minute)
    
    async def generate_images(self, params: ImageGenerationParams) -> ImageGenerationResult:
        """Generate images using Fal.ai models."""
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Check if Fal client is available
            if not fal_client:
                return ImageGenerationResult(
                    request_id=request_id,
                    images=[],
                    original_prompt=params.prompt,
                    parameters=params,
                    success=False,
                    error_message="fal-client not installed. Run: pip install fal-client",
                    provider=ProviderType.FAL
                )
            
            if not self.config.api.fal_api_key:
                return ImageGenerationResult(
                    request_id=request_id,
                    images=[],
                    original_prompt=params.prompt,
                    parameters=params,
                    success=False,
                    error_message="FAL_KEY environment variable not configured",
                    provider=ProviderType.FAL
                )
            
            # Validate parameters
            if not params.validate_params():
                return ImageGenerationResult(
                    request_id=request_id,
                    images=[],
                    original_prompt=params.prompt,
                    parameters=params,
                    success=False,
                    error_message="Invalid parameter combination for the selected model",
                    provider=ProviderType.FAL
                )
            
            # Apply rate limiting
            await self.rate_limiter.acquire()
            
            # Convert parameters to Fal.ai format
            fal_params = params.to_fal_params()
            
            # Use queue monitoring for longer operations
            if self.config.fal.enable_queue_monitoring:
                result = await self._generate_with_queue_monitoring(params.model.value, fal_params, request_id)
            else:
                # Direct synchronous call
                response = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: fal_client.run(params.model.value, arguments=fal_params)
                )
                result = await self._process_fal_response(response, params, request_id, start_time)
            
            return result
            
        except Exception as e:
            generation_time = time.time() - start_time
            return ImageGenerationResult(
                request_id=request_id,
                images=[],
                original_prompt=params.prompt,
                parameters=params,
                success=False,
                error_message=str(e),
                generation_time_seconds=generation_time,
                provider=ProviderType.FAL
            )
    
    async def _generate_with_queue_monitoring(self, model_id: str, params: Dict[str, Any], request_id: str) -> ImageGenerationResult:
        """Generate images with queue monitoring for better user experience."""
        start_time = time.time()
        
        try:
            # Submit to queue
            request = await asyncio.get_event_loop().run_in_executor(
                None, lambda: fal_client.submit(model_id, arguments=params)
            )
            
            # Monitor queue status
            queue_position = None
            logs_index = 0
            
            async for event in self._iter_events_async(request):
                if hasattr(event, 'position') and event.position is not None:
                    queue_position = event.position
                
                # Log progress if available
                if hasattr(event, 'logs'):
                    new_logs = event.logs[logs_index:]
                    for log in new_logs:
                        print(f"[Fal.ai] {log.get('message', '')}")
                    logs_index = len(event.logs)
            
            # Get final result
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: request.get()
            )
            
            # Process the response
            result = await self._process_fal_response(response, params, request_id, start_time)
            result.queue_position = queue_position
            
            return result
            
        except Exception as e:
            generation_time = time.time() - start_time
            return ImageGenerationResult(
                request_id=request_id,
                images=[],
                original_prompt=params.get("prompt", ""),
                parameters=ImageGenerationParams(prompt=params.get("prompt", "")),
                success=False,
                error_message=str(e),
                generation_time_seconds=generation_time,
                provider=ProviderType.FAL
            )
    
    async def _iter_events_async(self, request):
        """Convert synchronous event iteration to async."""
        loop = asyncio.get_event_loop()
        
        def get_events():
            try:
                return list(request.iter_events(with_logs=True))
            except Exception:
                return []
        
        events = await loop.run_in_executor(None, get_events)
        for event in events:
            yield event
    
    async def _process_fal_response(self, response: Dict[str, Any], original_params: Dict[str, Any], request_id: str, start_time: float) -> ImageGenerationResult:
        """Process Fal.ai API response into our standard format."""
        generation_time = time.time() - start_time
        
        # Extract images from response
        images = []
        image_data = response.get("images", [])
        
        for i, img_data in enumerate(image_data):
            # Handle different response formats
            image_url = None
            seed = None
            
            if isinstance(img_data, dict):
                image_url = img_data.get("url")
                seed = img_data.get("seed")
            elif isinstance(img_data, str):
                image_url = img_data
            
            if image_url:
                generated_image = GeneratedImage(
                    url=image_url,
                    seed=seed
                )
                images.append(generated_image)
        
        # Create parameters object for the result
        params = ImageGenerationParams(
            prompt=original_params.get("prompt", ""),
            negative_prompt=original_params.get("negative_prompt"),
            num_images=original_params.get("num_images", 1),
            seed=original_params.get("seed")
        )
        
        return ImageGenerationResult(
            request_id=request_id,
            images=images,
            original_prompt=original_params.get("prompt", ""),
            parameters=params,
            success=True,
            generation_time_seconds=generation_time,
            provider=ProviderType.FAL
        )


class UnifiedImageGenerationService:
    """Unified service that routes requests to appropriate providers."""
    
    def __init__(self):
        self.openai_service = ImageGenerationService()
        self.fal_service = FalImageGenerationService()
    
    async def generate_images(self, params: ImageGenerationParams) -> ImageGenerationResult:
        """Generate images using the appropriate provider based on the model."""
        provider = params.get_provider()
        
        if provider == ProviderType.OPENAI:
            return await self.openai_service.generate_images(params)
        elif provider == ProviderType.FAL:
            return await self.fal_service.generate_images(params)
        else:
            return ImageGenerationResult(
                request_id=str(uuid.uuid4()),
                images=[],
                original_prompt=params.prompt,
                parameters=params,
                success=False,
                error_message=f"Unsupported provider for model: {params.model.value}",
                provider=provider
            )


class PromptEnhancementService:
    """Service for enhancing user prompts using LLM."""
    
    def __init__(self):
        self.config = get_config()
    
    async def enhance_prompt(self, request: PromptEnhancementRequest) -> PromptEnhancementResult:
        """Enhance a user prompt using LLM."""
        try:
            # Build enhancement context
            context = self._build_enhancement_context(request)
            
            # Create system prompt for enhancement
            system_prompt = self._create_enhancement_system_prompt(request.target_provider)
            
            # This would integrate with the Pydantic AI agent
            # For now, we'll create a basic enhancement
            enhanced_prompt = self._enhance_prompt_basic(request)
            
            return PromptEnhancementResult(
                original_prompt=request.original_prompt,
                enhanced_prompt=enhanced_prompt,
                enhancement_reason="Added artistic details, lighting, and composition elements",
                suggested_params=self._suggest_parameters(request)
            )
            
        except Exception as e:
            # Fallback to original prompt if enhancement fails
            return PromptEnhancementResult(
                original_prompt=request.original_prompt,
                enhanced_prompt=request.original_prompt,
                enhancement_reason=f"Enhancement failed: {str(e)}",
                suggested_params=None
            )
    
    def _create_enhancement_system_prompt(self, target_provider: Optional[ProviderType]) -> str:
        """Create provider-specific system prompt for enhancement."""
        base_prompt = """You are an expert at creating detailed, creative prompts for AI image generation.
        Your task is to enhance user prompts while preserving their core intent.
        
        Guidelines:
        - Add specific details about composition, lighting, colors, and style
        - Include artistic techniques and quality descriptors
        - Maintain the original subject and concept
        - Make the prompt more vivid and descriptive
        - Keep it under 500 characters"""
        
        if target_provider == ProviderType.FAL:
            base_prompt += """
        
        Fal.ai specific optimizations:
        - Focus on detailed scene descriptions
        - Include technical photography terms
        - Mention specific art styles and techniques
        - Add quality modifiers like '4K', 'highly detailed', 'masterpiece'"""
        elif target_provider == ProviderType.OPENAI:
            base_prompt += """
        
        DALL-E specific optimizations:
        - Use clear, descriptive language
        - Avoid overly complex compositions
        - Focus on main subject and setting
        - Include mood and atmosphere descriptions"""
        
        return base_prompt
    
    def _build_enhancement_context(self, request: PromptEnhancementRequest) -> str:
        """Build context for prompt enhancement."""
        context = f"Original prompt: {request.original_prompt}\n"
        
        if request.style_preference:
            style_keywords = STYLE_KEYWORDS.get(request.style_preference, "")
            context += f"Style preference: {request.style_preference} ({style_keywords})\n"
        
        if request.additional_context:
            context += f"Additional context: {request.additional_context}\n"
        
        if request.target_provider:
            context += f"Target provider: {request.target_provider.value}\n"
        
        return context
    
    def _enhance_prompt_basic(self, request: PromptEnhancementRequest) -> str:
        """Basic prompt enhancement without LLM."""
        prompt = request.original_prompt
        
        # Add style keywords if specified
        if request.style_preference and request.style_preference in STYLE_KEYWORDS:
            style_addition = STYLE_KEYWORDS[request.style_preference]
            prompt = f"{prompt}, {style_addition}"
        
        # Add quality descriptors if creativity enhancement is requested
        if request.enhance_creativity:
            if request.target_provider == ProviderType.FAL:
                quality_descriptors = [
                    "highly detailed", "4K resolution", "masterpiece quality",
                    "perfect composition", "professional lighting", "ultra-realistic"
                ]
            else:
                quality_descriptors = [
                    "highly detailed", "professional", "masterpiece quality",
                    "perfect composition", "excellent lighting"
                ]
            prompt += f", {', '.join(quality_descriptors[:3])}"
        
        return prompt
    
    def _suggest_parameters(self, request: PromptEnhancementRequest) -> Optional[Dict[str, Any]]:
        """Suggest generation parameters based on the prompt."""
        suggestions = {}
        
        # Suggest style based on prompt content
        prompt_lower = request.original_prompt.lower()
        
        if any(word in prompt_lower for word in ["photo", "realistic", "portrait"]):
            suggestions["style"] = "natural" if request.target_provider == ProviderType.OPENAI else "photographic"
            suggestions["quality"] = "hd"
        elif any(word in prompt_lower for word in ["art", "painting", "creative"]):
            suggestions["style"] = "vivid" if request.target_provider == ProviderType.OPENAI else "base"
        
        # Suggest size based on content
        if any(word in prompt_lower for word in ["landscape", "wide", "panorama"]):
            suggestions["size"] = "1792x1024" if request.target_provider == ProviderType.OPENAI else "landscape"
        elif any(word in prompt_lower for word in ["portrait", "tall", "vertical"]):
            suggestions["size"] = "1024x1792" if request.target_provider == ProviderType.OPENAI else "portrait"
        
        # Fal.ai specific suggestions
        if request.target_provider == ProviderType.FAL:
            if any(word in prompt_lower for word in ["detailed", "complex", "intricate"]):
                suggestions["num_inference_steps"] = 50
                suggestions["guidance_scale"] = 7.5
        
        return suggestions if suggestions else None


class ImageStorageService:
    """Service for managing image storage and metadata."""
    
    def __init__(self):
        self.config = get_config()
        self.history = ImageHistory()
        self._load_history()
    
    async def save_images(self, result: ImageGenerationResult) -> ImageGenerationResult:
        """Download and save generated images locally."""
        try:
            async with httpx.AsyncClient() as client:
                for i, image in enumerate(result.images):
                    if image.url:
                        # Download image
                        response = await client.get(str(image.url))
                        response.raise_for_status()
                        
                        # Generate filename
                        filename = self._generate_filename(result, i)
                        image_path = self.config.storage.images_dir / filename
                        
                        # Save image
                        with open(image_path, 'wb') as f:
                            f.write(response.content)
                        
                        # Update image with local path
                        image.local_path = image_path
            
            # Save metadata
            result.save_metadata(self.config.storage.metadata_dir)
            
            # Add to history
            self.history.add_generation(result)
            self._save_history()
            
            return result
            
        except Exception as e:
            result.success = False
            result.error_message = f"Failed to save images: {str(e)}"
            return result
    
    def _generate_filename(self, result: ImageGenerationResult, image_index: int) -> str:
        """Generate a unique filename for an image."""
        # Create hash of prompt for uniqueness
        prompt_hash = hashlib.md5(result.original_prompt.encode()).hexdigest()[:8]
        timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
        provider = result.provider.value if result.provider else "unknown"
        return f"{timestamp}_{provider}_{prompt_hash}_{image_index}.png"
    
    def get_history(self, limit: int = 20, provider: Optional[ProviderType] = None) -> List[ImageGenerationResult]:
        """Get recent generation history, optionally filtered by provider."""
        if provider:
            filtered_generations = self.history.get_by_provider(provider)
            return sorted(filtered_generations, key=lambda x: x.timestamp, reverse=True)[:limit]
        else:
            return self.history.get_recent_generations(limit)
    
    def search_history(self, search_term: str, provider: Optional[ProviderType] = None) -> List[ImageGenerationResult]:
        """Search generation history by prompt, optionally filtered by provider."""
        results = self.history.search_by_prompt(search_term)
        if provider:
            results = [r for r in results if r.provider == provider]
        return results
    
    def _load_history(self):
        """Load generation history from disk."""
        try:
            for metadata_file in self.config.storage.metadata_dir.glob("*.json"):
                try:
                    result = ImageGenerationResult.load_metadata(metadata_file)
                    self.history.add_generation(result)
                except Exception as e:
                    print(f"Failed to load metadata from {metadata_file}: {e}")
        except Exception as e:
            print(f"Failed to load history: {e}")
    
    def _save_history(self):
        """Save current history state."""
        # History is automatically saved through individual metadata files
        pass
    
    async def cleanup_old_files(self):
        """Clean up old images and metadata based on configuration."""
        cutoff_date = datetime.now() - timedelta(days=self.config.storage.cleanup_after_days)
        
        cleaned_count = 0
        for metadata_file in self.config.storage.metadata_dir.glob("*.json"):
            try:
                result = ImageGenerationResult.load_metadata(metadata_file)
                if result.timestamp < cutoff_date:
                    # Remove associated images
                    for image in result.images:
                        if image.local_path and image.local_path.exists():
                            image.local_path.unlink()
                    
                    # Remove metadata file
                    metadata_file.unlink()
                    cleaned_count += 1
                    
            except Exception as e:
                print(f"Error during cleanup of {metadata_file}: {e}")
        
        print(f"Cleaned up {cleaned_count} old generation records")


class ImageProcessingService:
    """Service for image processing operations like upscaling and variations."""
    
    def __init__(self):
        self.config = get_config()
    
    async def upscale_image(self, request: ImageUpscaleRequest) -> Path:
        """Upscale an image using PIL (basic implementation)."""
        try:
            # Open original image
            with Image.open(request.image_path) as img:
                # Calculate new size
                new_width = img.width * request.scale_factor
                new_height = img.height * request.scale_factor
                
                # Choose resampling method based on enhancement setting
                if request.enhance_quality:
                    resample = Image.LANCZOS
                else:
                    resample = Image.BICUBIC
                
                # Resize image
                upscaled = img.resize((new_width, new_height), resample)
                
                # Generate output filename
                output_path = request.image_path.parent / f"{request.image_path.stem}_upscaled_{request.scale_factor}x{request.image_path.suffix}"
                
                # Save upscaled image
                upscaled.save(output_path, quality=95 if output_path.suffix.lower() == '.jpg' else None)
                
                return output_path
                
        except Exception as e:
            raise Exception(f"Failed to upscale image: {str(e)}")
    
    async def create_variations(self, request: ImageVariationRequest) -> List[Path]:
        """Create variations of an image (placeholder implementation)."""
        # This would integrate with OpenAI's image variation API or Fal.ai variation models
        # For now, we'll create a placeholder response
        variations = []
        
        try:
            # In a real implementation, this would:
            # 1. Upload the base image to the appropriate service
            # 2. Generate variations using the variations API
            # 3. Download and save the variations
            
            # Placeholder: just copy the original image with different names
            for i in range(request.num_variations):
                variation_path = request.base_image_path.parent / f"{request.base_image_path.stem}_variation_{i+1}{request.base_image_path.suffix}"
                
                # Copy original image (in real implementation, this would be an actual variation)
                with Image.open(request.base_image_path) as img:
                    img.save(variation_path)
                
                variations.append(variation_path)
            
            return variations
            
        except Exception as e:
            raise Exception(f"Failed to create variations: {str(e)}")


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.requests = []
    
    async def acquire(self):
        """Acquire permission to make a request."""
        now = time.time()
        
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        # Check if we can make a request
        if len(self.requests) >= self.requests_per_minute:
            # Calculate how long to wait
            oldest_request = min(self.requests)
            wait_time = 60 - (now - oldest_request)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.requests.append(now) 