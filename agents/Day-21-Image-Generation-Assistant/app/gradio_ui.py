"""Gradio Web UI for Image Generation Assistant."""

import gradio as gr
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
import os

from agent import run_image_assistant_sync, run_image_assistant
from models import AgentResponse
from config import SUPPORTED_MODELS, STYLE_KEYWORDS

# Global state for managing UI updates
current_generation = None

def get_available_models():
    """Get list of available models categorized by provider."""
    openai_models = []
    fal_models = []
    
    for model_name, config in SUPPORTED_MODELS.items():
        if config["provider"] == "openai":
            openai_models.append(model_name)
        elif config["provider"] == "fal":
            fal_models.append(model_name)
    
    return openai_models, fal_models

def get_model_info(model_name: str) -> str:
    """Get detailed information about a model."""
    if not model_name or model_name not in SUPPORTED_MODELS:
        return "Select a model to see details"
    
    config = SUPPORTED_MODELS[model_name]
    provider = config["provider"].upper()
    
    info = f"**{model_name}** ({provider})\n\n"
    info += f"• **Max Images**: {config.get('max_images', 1)}\n"
    info += f"• **Sizes**: {', '.join(config['sizes'])}\n"
    info += f"• **Styles**: {', '.join(config['styles'])}\n"
    
    if config.get("supports_negative_prompt"):
        info += "• **Negative Prompts**: ✅ Supported\n"
    
    if config.get("requires_premium"):
        info += "• **Premium**: ⭐ Premium subscription required\n"
    
    return info

def get_available_styles():
    """Get list of available styles."""
    return list(STYLE_KEYWORDS.keys())

def get_available_sizes(model_name: str) -> List[str]:
    """Get available sizes for a specific model."""
    if not model_name or model_name not in SUPPORTED_MODELS:
        return ["1024x1024"]
    
    return SUPPORTED_MODELS[model_name]["sizes"]

def update_model_dependent_ui(model_name: str):
    """Update UI elements based on selected model."""
    if not model_name:
        return (
            gr.update(choices=["1024x1024"], value="1024x1024"),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(value=get_model_info(model_name))
        )
    
    config = SUPPORTED_MODELS.get(model_name, {})
    is_fal = config.get("provider") == "fal"
    supports_negative = config.get("supports_negative_prompt", False)
    
    sizes = get_available_sizes(model_name)
    
    return (
        gr.update(choices=sizes, value=sizes[0] if sizes else "square"),
        gr.update(visible=is_fal),  # Advanced parameters section
        gr.update(visible=supports_negative),  # Negative prompt
        gr.update(visible=is_fal),  # Fal.ai note
        gr.update(value=get_model_info(model_name))
    )

def generate_image(
    prompt: str,
    model: str,
    style: str,
    size: str,
    quality: str,
    num_images: int,
    enhance_prompt: bool,
    negative_prompt: str,
    seed: Optional[int],
    guidance_scale: Optional[float],
    inference_steps: Optional[int],
    progress=gr.Progress()
) -> Tuple[List[str], str, str]:
    """Generate images using the selected parameters."""
    
    if not prompt.strip():
        return [], "❌ Please enter a prompt", ""
    
    if not model:
        return [], "❌ Please select a model", ""
    
    # Build request string
    request_parts = [f'Generate an image with prompt: "{prompt}"']
    
    if model:
        request_parts.append(f"model: {model}")
    if style and style != "auto":
        request_parts.append(f"style: {style}")
    if size:
        request_parts.append(f"size: {size}")
    if quality != "standard":
        request_parts.append(f"quality: {quality}")
    if num_images > 1:
        request_parts.append(f"number of images: {num_images}")
    if negative_prompt and negative_prompt.strip():
        request_parts.append(f"avoid: {negative_prompt}")
    if seed is not None:
        request_parts.append(f"seed: {seed}")
    if guidance_scale is not None:
        request_parts.append(f"guidance scale: {guidance_scale}")
    if inference_steps is not None:
        request_parts.append(f"inference steps: {inference_steps}")
    if not enhance_prompt:
        request_parts.append("do not enhance the prompt")
    
    user_input = ", ".join(request_parts)
    
    try:
        progress(0.1, desc="Initializing...")
        
        # Run the generation
        progress(0.3, desc="Processing request...")
        response = run_image_assistant_sync(user_input)
        
        progress(0.8, desc="Finalizing...")
        
        if response.success:
            image_paths = response.images if response.images else []
            
            # Convert paths to strings for Gradio
            image_paths_str = [str(path) for path in image_paths]
            
            # Build success message
            message = f"✅ {response.message}"
            
            # Build details
            details = ""
            if response.data:
                details += "**Generation Details:**\n"
                for key, value in response.data.items():
                    if key == "provider":
                        details += f"• **Provider**: {value.upper()}\n"
                    elif key == "model":
                        details += f"• **Model**: {value}\n"
                    elif key == "generation_time":
                        details += f"• **Time**: {value:.2f}s\n"
                    elif key == "seed" and value is not None:
                        details += f"• **Seed**: {value} (use for reproducible results)\n"
                    elif key == "enhanced_prompt" and value:
                        details += f"• **Enhanced Prompt**: {value}\n"
            
            if response.suggestions:
                details += "\n**Suggestions:**\n"
                for suggestion in response.suggestions:
                    details += f"• {suggestion}\n"
            
            progress(1.0, desc="Complete!")
            return image_paths_str, message, details
        else:
            error_msg = f"❌ {response.message}"
            if response.suggestions:
                error_msg += "\n\n**Suggestions:**\n"
                for suggestion in response.suggestions:
                    error_msg += f"• {suggestion}\n"
            return [], error_msg, ""
            
    except Exception as e:
        return [], f"❌ Error: {str(e)}", ""

def enhance_prompt_func(
    prompt: str,
    style: str,
    provider: str,
    context: str
) -> Tuple[str, str]:
    """Enhance a prompt using AI."""
    
    if not prompt.strip():
        return "", "❌ Please enter a prompt to enhance"
    
    try:
        # Import required modules
        import asyncio
        from agent import enhance_prompt, ImageAssistantDeps, EnhancePromptRequest
        from services import (
            UnifiedImageGenerationService, PromptEnhancementService,
            ImageStorageService, ImageProcessingService
        )
        
        # Create dependencies
        deps = ImageAssistantDeps(
            generation_service=UnifiedImageGenerationService(),
            enhancement_service=PromptEnhancementService(),
            storage_service=ImageStorageService(),
            processing_service=ImageProcessingService()
        )
        
        # Create structured request
        enhance_request = EnhancePromptRequest(
            prompt=prompt,
            style_preference=style if style != "auto" else None,
            target_provider=provider if provider != "auto" else None,
            additional_context=context if context.strip() else None
        )
        
        # Create a mock context for the tool call
        class MockContext:
            def __init__(self, deps):
                self.deps = deps
        
        # Run the tool function directly
        response = asyncio.run(enhance_prompt(MockContext(deps), enhance_request))
        
        if response.success:
            enhanced_prompt = ""
            details = response.message
            
            # Extract enhanced prompt from response data
            if response.data and "enhanced_prompt" in response.data:
                enhanced_prompt = response.data["enhanced_prompt"]
            
            return enhanced_prompt, details
        else:
            return "", f"❌ {response.message}"
            
    except ImportError as e:
        return "", f"❌ Import Error: {str(e)}"
    except Exception as e:
        return "", f"❌ Error: {str(e)}"

def view_history_func(
    limit: int,
    search_term: str,
    provider_filter: str
) -> Tuple[str, str]:
    """View generation history."""
    
    try:
        # Import required modules
        import asyncio
        from agent import view_history, ImageAssistantDeps, ViewHistoryRequest
        from services import (
            UnifiedImageGenerationService, PromptEnhancementService,
            ImageStorageService, ImageProcessingService
        )
        
        # Create dependencies
        deps = ImageAssistantDeps(
            generation_service=UnifiedImageGenerationService(),
            enhancement_service=PromptEnhancementService(),
            storage_service=ImageStorageService(),
            processing_service=ImageProcessingService()
        )
        
        # Create structured request
        history_request = ViewHistoryRequest(
            limit=limit,
            search_term=search_term if search_term.strip() else None,
            provider=provider_filter if provider_filter != "all" else None
        )
        
        # Create a mock context for the tool call
        class MockContext:
            def __init__(self, deps):
                self.deps = deps
        
        # Run the tool function directly
        response = asyncio.run(view_history(MockContext(deps), history_request))
        
        if response.success:
            history_text = response.message
            
            # Add detailed information if available
            details = ""
            if response.data and "history" in response.data:
                history = response.data["history"]
                if history:
                    details = f"Found {len(history)} generations\n\n"
                    for i, gen in enumerate(history[:10], 1):  # Show first 10 in details
                        status = "✅" if gen.get("success") else "❌"
                        provider = gen.get("provider", "unknown").upper()
                        model = gen.get("model", "unknown")
                        timestamp = gen.get("timestamp", "")
                        if timestamp:
                            try:
                                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                timestamp = dt.strftime("%Y-%m-%d %H:%M")
                            except:
                                pass
                        
                        prompt = gen.get("prompt", "")[:60]
                        if len(gen.get("prompt", "")) > 60:
                            prompt += "..."
                        
                        details += f"{i}. {status} [{provider}:{model}] \"{prompt}\" ({timestamp})\n"
            
            return history_text, details
        else:
            return f"❌ {response.message}", ""
            
    except ImportError as e:
        return f"❌ Import Error: {str(e)}", ""
    except Exception as e:
        return f"❌ Error: {str(e)}", ""

def get_setup_status():
    """Check if API keys are configured."""
    openai_key = os.getenv("OPENAI_API_KEY")
    fal_key = os.getenv("FAL_KEY")
    
    status = "**API Key Status:**\n\n"
    
    if openai_key:
        status += "• ✅ **OpenAI API Key**: Configured\n"
    else:
        status += "• ❌ **OpenAI API Key**: Not configured\n"
    
    if fal_key:
        status += "• ✅ **Fal.ai API Key**: Configured\n"
    else:
        status += "• ❌ **Fal.ai API Key**: Not configured\n"
    
    if not openai_key and not fal_key:
        status += "\n⚠️ **No API keys configured!** Please set up at least one API key in your `.env` file."
    elif openai_key and fal_key:
        status += "\n🎉 **All providers available!** You can use both OpenAI and Fal.ai models."
    else:
        available = "OpenAI" if openai_key else "Fal.ai"
        status += f"\n✅ **{available} ready!** You can generate images with {available} models."
    
    return status

# Create the Gradio interface
def create_ui():
    """Create the main Gradio interface."""
    
    openai_models, fal_models = get_available_models()
    all_models = openai_models + fal_models
    styles = get_available_styles()
    
    with gr.Blocks(
        theme=gr.themes.Soft(),
        title="Image Generation Assistant",
        css="""
        .model-info { 
            font-size: 14px; 
            padding: 15px; 
            background-color: #000000; 
            color: #ffffff;
            border-radius: 8px; 
            margin: 10px 0; 
            border: 1px solid #e9ecef;
        }
        .status-info {
            font-size: 14px; 
            padding: 15px; 
            background-color: #000000; 
            color: #ffffff;
            border-radius: 8px; 
            margin: 10px 0; 
            border: 1px solid #c3e6c3;
        }
        .generation-details {
            font-size: 14px;
            padding: 15px;
            background-color: #000000;
            color: #ffffff;
            border-radius: 8px;
            margin: 10px 0;
            border: 1px solid #bee5eb;
        }
        .error-message {
            font-size: 14px;
            padding: 15px;
            background-color: #000000;
            color: #ffffff;
            border-radius: 8px;
            margin: 10px 0;
            border: 1px solid #f5c6cb;
        }
        """
    ) as demo:
        
        gr.Markdown("""
        # 🎨 Image Generation Assistant
        
        **Multi-Provider AI Image Generation** powered by OpenAI DALL-E and Fal.ai models
        
        Generate stunning images from text descriptions using state-of-the-art AI models!
        """)
        
        # API Status
        with gr.Row():
            with gr.Column():
                setup_status = gr.Markdown(
                    value=get_setup_status(),
                    elem_classes=["status-info"]
                )
                refresh_status_btn = gr.Button("🔄 Refresh Status", size="sm")
        
        with gr.Tabs() as tabs:
            # Generation Tab
            with gr.Tab("🎨 Generate Images"):
                with gr.Row():
                    with gr.Column(scale=2):
                        prompt_input = gr.Textbox(
                            label="Image Prompt",
                            placeholder="Describe the image you want to generate...",
                            lines=3,
                            value="A serene mountain landscape at sunset with reflections in a crystal-clear lake"
                        )
                        
                        with gr.Row():
                            model_dropdown = gr.Dropdown(
                                label="Model",
                                choices=all_models,
                                value=all_models[0] if all_models else None,
                                info="Choose between OpenAI DALL-E and Fal.ai models"
                            )
                            style_dropdown = gr.Dropdown(
                                label="Style",
                                choices=["auto"] + styles,
                                value="auto",
                                info="Artistic style for the image"
                            )
                        
                        with gr.Row():
                            size_dropdown = gr.Dropdown(
                                label="Size",
                                choices=["1024x1024"],
                                value="1024x1024",
                                info="Image dimensions"
                            )
                            quality_dropdown = gr.Dropdown(
                                label="Quality",
                                choices=["standard", "hd"],
                                value="standard",
                                info="Image quality (HD costs more)"
                            )
                        
                        with gr.Row():
                            num_images_slider = gr.Slider(
                                label="Number of Images",
                                minimum=1,
                                maximum=4,
                                step=1,
                                value=1,
                                info="How many images to generate"
                            )
                            enhance_checkbox = gr.Checkbox(
                                label="✨ Enhance Prompt",
                                value=True,
                                info="Use AI to improve your prompt"
                            )
                        
                        # Negative prompt (for Fal.ai models)
                        negative_prompt_input = gr.Textbox(
                            label="Negative Prompt (Fal.ai only)",
                            placeholder="What to avoid in the image (e.g., blurry, low quality, people)",
                            lines=2,
                            visible=False,
                            info="Specify what you don't want in the image"
                        )
                        
                        # Advanced parameters (for Fal.ai models)
                        with gr.Group(visible=False) as advanced_group:
                            gr.Markdown("### 🔧 Advanced Parameters (Fal.ai)")
                            
                            with gr.Row():
                                seed_input = gr.Number(
                                    label="Seed",
                                    value=None,
                                    precision=0,
                                    info="Random seed for reproducible results"
                                )
                                guidance_scale_slider = gr.Slider(
                                    label="Guidance Scale",
                                    minimum=1.0,
                                    maximum=20.0,
                                    step=0.5,
                                    value=7.5,
                                    info="How closely to follow the prompt"
                                )
                            
                            inference_steps_slider = gr.Slider(
                                label="Inference Steps",
                                minimum=10,
                                maximum=100,
                                step=5,
                                value=50,
                                info="Number of denoising steps (more = better quality)"
                            )
                        
                        fal_note = gr.Markdown(
                            "ℹ️ *Fal.ai models support queue processing - you may need to wait in queue during peak times.*",
                            visible=False
                        )
                        
                        generate_btn = gr.Button(
                            "🎨 Generate Images",
                            variant="primary",
                            size="lg"
                        )
                    
                    with gr.Column(scale=1):
                        model_info = gr.Markdown(
                            value=get_model_info(all_models[0] if all_models else ""),
                            elem_classes=["model-info"]
                        )
                
                # Results section
                with gr.Row():
                    with gr.Column():
                        generation_output = gr.Gallery(
                            label="Generated Images",
                            show_label=True,
                            elem_id="gallery",
                            columns=2,
                            rows=2,
                            height="auto",
                            preview=True
                        )
                        
                        generation_message = gr.Markdown(
                            value="Click 'Generate Images' to start creating!",
                            elem_classes=["generation-details"]
                        )
                        
                        generation_details = gr.Markdown(
                            value="",
                            visible=False
                        )
            
            # Prompt Enhancement Tab
            with gr.Tab("✨ Enhance Prompts"):
                with gr.Row():
                    with gr.Column():
                        enhance_prompt_input = gr.Textbox(
                            label="Original Prompt",
                            placeholder="Enter a basic prompt to enhance...",
                            lines=3,
                            value="a cat"
                        )
                        
                        with gr.Row():
                            enhance_style_dropdown = gr.Dropdown(
                                label="Style Preference",
                                choices=["auto"] + styles,
                                value="auto"
                            )
                            enhance_provider_dropdown = gr.Dropdown(
                                label="Target Provider",
                                choices=["auto", "openai", "fal"],
                                value="auto",
                                info="Optimize for specific provider"
                            )
                        
                        enhance_context_input = gr.Textbox(
                            label="Additional Context",
                            placeholder="Any additional context or requirements...",
                            lines=2
                        )
                        
                        enhance_btn = gr.Button(
                            "✨ Enhance Prompt",
                            variant="primary"
                        )
                    
                    with gr.Column():
                        enhanced_prompt_output = gr.Textbox(
                            label="Enhanced Prompt",
                            lines=4,
                            interactive=True,
                            info="Copy this to use in generation"
                        )
                        
                        enhancement_details = gr.Markdown(
                            value="Enter a prompt and click 'Enhance Prompt' to improve it!",
                            elem_classes=["generation-details"]
                        )
                        
                        copy_to_generate_btn = gr.Button(
                            "📋 Copy to Generate Tab",
                            size="sm"
                        )
            
            # History Tab
            with gr.Tab("📚 History"):
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            history_limit_slider = gr.Slider(
                                label="Number of Records",
                                minimum=5,
                                maximum=50,
                                step=5,
                                value=10
                            )
                            history_provider_dropdown = gr.Dropdown(
                                label="Filter by Provider",
                                choices=["all", "openai", "fal"],
                                value="all"
                            )
                        
                        history_search_input = gr.Textbox(
                            label="Search History",
                            placeholder="Search for specific prompts...",
                            info="Leave empty to see recent generations"
                        )
                        
                        view_history_btn = gr.Button(
                            "📚 View History",
                            variant="primary"
                        )
                        
                        refresh_history_btn = gr.Button(
                            "🔄 Refresh",
                            size="sm"
                        )
                    
                    with gr.Column():
                        history_output = gr.Markdown(
                            value="Click 'View History' to see your generation history!",
                            elem_classes=["generation-details"]
                        )
                        
                        history_details = gr.Markdown(
                            value="",
                            visible=False
                        )
            
            # Help Tab
            with gr.Tab("❓ Help & Info"):
                gr.Markdown("""
                ## 🚀 Getting Started
                
                1. **Set up API Keys**: Configure your OpenAI and/or Fal.ai API keys in a `.env` file
                2. **Choose a Model**: Select from OpenAI DALL-E or Fal.ai models
                3. **Write a Prompt**: Describe the image you want to generate
                4. **Customize Settings**: Adjust style, size, and advanced parameters
                5. **Generate**: Click the generate button and wait for your images!
                
                ## 🎨 Available Models
                
                ### OpenAI DALL-E
                - **DALL-E 3**: Highest quality, 1 image per request
                - **DALL-E 2**: Faster, up to 10 images per request
                
                ### Fal.ai Models
                - **fal-ai/fast-sdxl**: Fast SDXL with many styles
                - **fal-ai/flux/schnell**: High-quality Flux model
                - **fal-ai/flux/dev**: Premium Flux (subscription required)
                - **fal-ai/stable-diffusion-v3-medium**: Latest Stable Diffusion
                - **fal-ai/aura-flow**: Creative flow model
                
                ## 🛠️ Advanced Features
                
                ### Fal.ai Advanced Parameters
                - **Seed**: Use the same seed to reproduce similar results
                - **Guidance Scale**: Higher values follow the prompt more closely (1-20)
                - **Inference Steps**: More steps = better quality but slower (10-100)
                - **Negative Prompt**: Specify what you don't want in the image
                
                ### Prompt Enhancement
                - Uses AI (GPT-4) to improve your prompts automatically
                - Can be optimized for specific providers
                - Adds artistic details, lighting, and composition elements
                
                ### History & Management
                - All generations are automatically saved and tracked
                - Search through your generation history
                - Filter by provider to compare results
                - Track seeds and parameters for reproducible results
                
                ## 💡 Tips for Better Results
                
                1. **Be Descriptive**: Include details about lighting, composition, style
                2. **Use Negative Prompts**: Specify what you want to avoid (Fal.ai only)
                3. **Experiment with Models**: Different models have different strengths
                4. **Try Different Seeds**: Same prompt + different seed = different results
                5. **Use Prompt Enhancement**: Let AI improve your prompts automatically
                
                ## 🔧 Setup Instructions
                
                Create a `.env` file in your project directory:
                ```
                OPENAI_API_KEY=your_openai_api_key_here
                FAL_KEY=your_fal_api_key_here
                ```
                
                You need at least one API key to use the application.
                """)
        
        # Event handlers
        def update_ui_on_model_change(model):
            return update_model_dependent_ui(model)
        
        def copy_enhanced_to_generate(enhanced_prompt):
            return enhanced_prompt
        
        def refresh_status():
            return get_setup_status()
        
        # Connect events
        model_dropdown.change(
            fn=update_ui_on_model_change,
            inputs=[model_dropdown],
            outputs=[size_dropdown, advanced_group, negative_prompt_input, fal_note, model_info]
        )
        
        generate_btn.click(
            fn=generate_image,
            inputs=[
                prompt_input, model_dropdown, style_dropdown, size_dropdown,
                quality_dropdown, num_images_slider, enhance_checkbox,
                negative_prompt_input, seed_input, guidance_scale_slider,
                inference_steps_slider
            ],
            outputs=[generation_output, generation_message, generation_details]
        )
        
        enhance_btn.click(
            fn=enhance_prompt_func,
            inputs=[
                enhance_prompt_input, enhance_style_dropdown,
                enhance_provider_dropdown, enhance_context_input
            ],
            outputs=[enhanced_prompt_output, enhancement_details]
        )
        
        copy_to_generate_btn.click(
            fn=copy_enhanced_to_generate,
            inputs=[enhanced_prompt_output],
            outputs=[prompt_input]
        )
        
        view_history_btn.click(
            fn=view_history_func,
            inputs=[history_limit_slider, history_search_input, history_provider_dropdown],
            outputs=[history_output, history_details]
        )
        
        refresh_history_btn.click(
            fn=view_history_func,
            inputs=[history_limit_slider, history_search_input, history_provider_dropdown],
            outputs=[history_output, history_details]
        )
        
        refresh_status_btn.click(
            fn=refresh_status,
            outputs=[setup_status]
        )
        
        # Initialize the UI with the first model
        demo.load(
            fn=update_ui_on_model_change,
            inputs=[model_dropdown],
            outputs=[size_dropdown, advanced_group, negative_prompt_input, fal_note, model_info]
        )
    
    return demo

def launch_ui(
    share: bool = False,
    server_name: str = "127.0.0.1",
    server_port: int = 7860,
    auth: Optional[Tuple[str, str]] = None
):
    """Launch the Gradio UI."""
    demo = create_ui()
    
    print("🎨 Starting Image Generation Assistant Web UI...")
    print(f"🌐 Server will be available at: http://{server_name}:{server_port}")
    
    if share:
        print("🔗 Public URL will be generated (Gradio share link)")
    
    try:
        demo.launch(
            share=share,
            server_name=server_name,
            server_port=server_port,
            auth=auth,
            show_api=False,
            show_error=True
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error launching UI: {e}")

if __name__ == "__main__":
    launch_ui(share=False) 