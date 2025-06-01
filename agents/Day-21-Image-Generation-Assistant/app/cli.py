"""Command-line interface for Image Generation Assistant."""

import asyncio
from pathlib import Path
from typing import Optional, List
import json

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

from agent import run_image_assistant_sync, run_image_assistant
from models import AgentResponse

app = typer.Typer(
    name="image-assistant",
    help="AI-powered Image Generation Assistant with OpenAI DALL-E and Fal.ai support",
    rich_markup_mode="rich"
)
console = Console()


@app.command("generate")
def generate_image(
    prompt: str = typer.Argument(..., help="Text description for the image to generate"),
    style: Optional[str] = typer.Option(None, "--style", "-s", help="Artistic style (photorealistic, cartoon, anime, etc.)"),
    size: Optional[str] = typer.Option(None, "--size", help="Image size (1024x1024, landscape, portrait, square_hd)"),
    quality: Optional[str] = typer.Option(None, "--quality", "-q", help="Image quality (standard, hd)"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use (dall-e-3, fal-ai/fast-sdxl, etc.)"),
    num_images: int = typer.Option(1, "--count", "-n", help="Number of images to generate (1-10)"),
    no_enhance: bool = typer.Option(False, "--no-enhance", help="Skip prompt enhancement"),
    negative_prompt: Optional[str] = typer.Option(None, "--negative", help="What to avoid in the image"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed for reproducible results (Fal.ai models)"),
    guidance_scale: Optional[float] = typer.Option(None, "--guidance", help="Guidance scale 1.0-20.0 (Fal.ai models)"),
    inference_steps: Optional[int] = typer.Option(None, "--steps", help="Number of inference steps 1-100 (Fal.ai models)"),
):
    """Generate images from text descriptions using OpenAI DALL-E or Fal.ai models."""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Generating image...", total=None)
        
        # Build the request
        request_parts = [f'Generate an image with prompt: "{prompt}"']
        
        if style:
            request_parts.append(f"style: {style}")
        if size:
            request_parts.append(f"size: {size}")
        if quality:
            request_parts.append(f"quality: {quality}")
        if model:
            request_parts.append(f"model: {model}")
        if num_images > 1:
            request_parts.append(f"number of images: {num_images}")
        if negative_prompt:
            request_parts.append(f"avoid: {negative_prompt}")
        if seed is not None:
            request_parts.append(f"seed: {seed}")
        if guidance_scale is not None:
            request_parts.append(f"guidance scale: {guidance_scale}")
        if inference_steps is not None:
            request_parts.append(f"inference steps: {inference_steps}")
        if no_enhance:
            request_parts.append("do not enhance the prompt")
        
        user_input = ", ".join(request_parts)
        
        try:
            response = run_image_assistant_sync(user_input)
            progress.stop()
            _display_response(response)
            
        except Exception as e:
            progress.stop()
            console.print(f"[red]Error: {str(e)}[/red]")


@app.command("enhance")
def enhance_prompt(
    prompt: str = typer.Argument(..., help="Prompt to enhance"),
    style: Optional[str] = typer.Option(None, "--style", "-s", help="Preferred artistic style"),
    context: Optional[str] = typer.Option(None, "--context", "-c", help="Additional context"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Target provider (openai or fal)"),
):
    """Enhance a prompt for better image generation."""
    
    request_parts = [f'Enhance this prompt: "{prompt}"']
    
    if style:
        request_parts.append(f"style preference: {style}")
    if context:
        request_parts.append(f"additional context: {context}")
    if provider:
        request_parts.append(f"target provider: {provider}")
    
    user_input = ", ".join(request_parts)
    
    with console.status("Enhancing prompt..."):
        response = run_image_assistant_sync(user_input)
    
    _display_response(response)


@app.command("history")
def view_history(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of recent generations to show"),
    search: Optional[str] = typer.Option(None, "--search", "-s", help="Search term to filter history"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Filter by provider (openai or fal)"),
):
    """View or search generation history."""
    
    request_parts = []
    if search:
        request_parts.append(f"Search history for: {search}")
    else:
        request_parts.append(f"Show my last {limit} generations")
    
    if provider:
        request_parts.append(f"provider: {provider}")
    
    user_input = ", ".join(request_parts)
    
    with console.status("Loading history..."):
        response = run_image_assistant_sync(user_input)
    
    _display_response(response)


@app.command("upscale")
def upscale_image(
    image_path: str = typer.Argument(..., help="Path to the image to upscale"),
    scale: int = typer.Option(2, "--scale", "-s", help="Scale factor (2, 3, or 4)"),
    enhance: bool = typer.Option(True, "--enhance/--no-enhance", help="Apply quality enhancement"),
):
    """Upscale an existing image."""
    
    user_input = f"Upscale image at {image_path} by {scale}x"
    if not enhance:
        user_input += " without quality enhancement"
    
    with console.status(f"Upscaling image by {scale}x..."):
        response = run_image_assistant_sync(user_input)
    
    _display_response(response)


@app.command("variations")
def create_variations(
    image_path: str = typer.Argument(..., help="Path to the base image"),
    count: int = typer.Option(3, "--count", "-n", help="Number of variations to create"),
    prompt_variation: Optional[str] = typer.Option(None, "--variation", "-v", help="Prompt variation"),
):
    """Create variations of an existing image."""
    
    user_input = f"Create {count} variations of image at {image_path}"
    if prompt_variation:
        user_input += f" with variation: {prompt_variation}"
    
    with console.status(f"Creating {count} variations..."):
        response = run_image_assistant_sync(user_input)
    
    _display_response(response)


@app.command("chat")
def interactive_chat():
    """Start an interactive chat session with the Image Assistant."""
    
    console.print(Panel.fit(
        "[bold blue]Image Generation Assistant[/bold blue]\n"
        "Supporting OpenAI DALL-E and Fal.ai models\n\n"
        "Type your requests naturally, like:\n"
        "• 'Generate a sunset over mountains'\n"
        "• 'Generate with fal-ai/fast-sdxl model'\n"
        "• 'Enhance this prompt: cat wearing hat'\n"
        "• 'Show my recent fal images'\n"
        "• 'Upscale my last image'\n\n"
        "Type 'quit' to exit.",
        title="Welcome"
    ))
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            if not user_input.strip():
                continue
            
            with console.status("Processing..."):
                response = run_image_assistant_sync(user_input)
            
            _display_response(response)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")


@app.command("info")
def show_info():
    """Show information about available options and capabilities."""
    
    info_content = """
# Image Generation Assistant

## Supported Providers

### OpenAI DALL-E
- **dall-e-3**: Latest model, best quality, 1 image per request
- **dall-e-2**: Faster model, up to 10 images per request

### Fal.ai Models  
- **fal-ai/fast-sdxl**: Fast SDXL, supports negative prompts, many styles
- **fal-ai/flux/schnell**: Fast Flux model, high quality
- **fal-ai/flux/dev**: Development Flux model (premium)
- **fal-ai/stable-diffusion-v3-medium**: Latest Stable Diffusion
- **fal-ai/aura-flow**: Creative flow model

## Available Styles

### Universal Styles
- **photorealistic**: High detail, professional photography
- **artistic**: Creative, expressive
- **cartoon**: Animated, colorful style
- **digital_art**: Modern digital art
- **vintage**: Retro, nostalgic style
- **minimalist**: Simple, clean lines
- **cyberpunk**: Neon, futuristic, dark
- **fantasy**: Magical, ethereal

### Fal.ai Specific Styles
- **anime**: Japanese animation style
- **photographic**: Realistic photography
- **comic_book**: Bold comic book style
- **line_art**: Black and white, sketch
- **neon_punk**: Vibrant neon colors

## Image Sizes

### OpenAI DALL-E
- **1024x1024**: Square format (default)
- **1792x1024**: Landscape/wide format
- **1024x1792**: Portrait/tall format
- **512x512**: Smaller square (DALL-E 2 only)
- **256x256**: Smallest square (DALL-E 2 only)

### Fal.ai Models
- **square**: Standard square format
- **portrait**: Vertical format
- **landscape**: Horizontal format
- **square_hd**: High-definition square

## Quality Options
- **standard**: Standard quality (faster, cheaper)
- **hd**: High definition (better quality, more expensive)

## Advanced Parameters (Fal.ai)
- **seed**: Random seed for reproducible results
- **guidance_scale**: Control adherence to prompt (1.0-20.0)
- **num_inference_steps**: Number of denoising steps (1-100)
- **negative_prompt**: What to avoid in the image

## Example Commands

```bash
# Generate with OpenAI DALL-E
image-assistant generate "A serene mountain landscape" --model dall-e-3

# Generate with Fal.ai model
image-assistant generate "A cyberpunk city" --model fal-ai/fast-sdxl --style photographic

# Use advanced Fal.ai parameters
image-assistant generate "A dragon in a mystical forest" \\
  --model fal-ai/fast-sdxl \\
  --seed 12345 \\
  --guidance 7.5 \\
  --steps 50 \\
  --negative "blurry, low quality"

# Enhance prompt for specific provider
image-assistant enhance "a cat" --style photorealistic --provider fal

# View history filtered by provider
image-assistant history --provider fal --limit 5

# Start interactive mode
image-assistant chat
```

## Configuration

Set up your API keys in a `.env` file:
```
OPENAI_API_KEY=your_openai_key_here
FAL_KEY=your_fal_key_here
```

You can use either or both providers. At least one API key is required.
"""
    
    console.print(Markdown(info_content))


@app.command("models")
def list_models():
    """List all available models and their capabilities."""
    
    models_info = """
# Available Models

## OpenAI DALL-E Models

### DALL-E 3 (`dall-e-3`)
- **Quality**: Highest
- **Speed**: Moderate  
- **Max Images**: 1 per request
- **Sizes**: 1024x1024, 1792x1024, 1024x1792
- **Styles**: vivid, natural
- **Special Features**: Best prompt interpretation, revised prompts

### DALL-E 2 (`dall-e-2`) 
- **Quality**: Good
- **Speed**: Fast
- **Max Images**: 10 per request
- **Sizes**: 256x256, 512x512, 1024x1024
- **Styles**: natural only
- **Special Features**: Multiple images, variations support

## Fal.ai Models

### Fast SDXL (`fal-ai/fast-sdxl`)
- **Quality**: High
- **Speed**: Fast
- **Max Images**: 4 per request
- **Sizes**: square, portrait, landscape, square_hd
- **Styles**: base, photographic, anime, digital-art, comic-book, fantasy-art, line-art, neon-punk
- **Special Features**: Negative prompts, advanced parameters, many styles

### Flux Schnell (`fal-ai/flux/schnell`)
- **Quality**: Very High
- **Speed**: Fast
- **Max Images**: 4 per request
- **Sizes**: square, portrait, landscape, square_hd
- **Styles**: natural
- **Special Features**: Latest Flux model, excellent quality

### Flux Dev (`fal-ai/flux/dev`)
- **Quality**: Highest
- **Speed**: Moderate
- **Max Images**: 4 per request
- **Sizes**: square, portrait, landscape, square_hd
- **Styles**: natural
- **Special Features**: Premium model, best quality, requires subscription

### Stable Diffusion v3 Medium (`fal-ai/stable-diffusion-v3-medium`)
- **Quality**: High
- **Speed**: Moderate
- **Max Images**: 4 per request
- **Sizes**: square, portrait, landscape
- **Styles**: natural
- **Special Features**: Latest SD3, negative prompts

### Aura Flow (`fal-ai/aura-flow`)
- **Quality**: High
- **Speed**: Fast
- **Max Images**: 4 per request
- **Sizes**: square, portrait, landscape
- **Styles**: natural
- **Special Features**: Creative flow model, unique style
"""
    
    console.print(Markdown(models_info))


def _display_response(response: AgentResponse):
    """Display an agent response with rich formatting."""
    
    if response.success:
        # Success message
        console.print(Panel(
            response.message,
            title="[green]✓ Success[/green]",
            border_style="green"
        ))
        
        # Show generated images if any
        if response.images:
            console.print(f"\n[bold]Generated Images:[/bold]")
            for i, image_path in enumerate(response.images, 1):
                console.print(f"  {i}. [cyan]{image_path}[/cyan]")
        
        # Show additional data if present
        if response.data:
            console.print(f"\n[bold]Details:[/bold]")
            if isinstance(response.data, dict):
                for key, value in response.data.items():
                    if key == "generation_time" and isinstance(value, (int, float)):
                        console.print(f"  {key}: {value:.2f}s")
                    elif key == "parameters" and isinstance(value, dict):
                        console.print(f"  {key}:")
                        for param_key, param_value in value.items():
                            console.print(f"    {param_key}: {param_value}")
                    elif key == "provider":
                        console.print(f"  {key}: [bold]{value.upper()}[/bold]")
                    elif key == "model":
                        console.print(f"  {key}: [blue]{value}[/blue]")
                    elif key == "seed" and value is not None:
                        console.print(f"  {key}: [yellow]{value}[/yellow] (use for reproducible results)")
                    else:
                        console.print(f"  {key}: {value}")
        
        # Show suggestions
        if response.suggestions:
            console.print(f"\n[bold yellow]Suggestions:[/bold yellow]")
            for suggestion in response.suggestions:
                console.print(f"  • {suggestion}")
    
    else:
        # Error message
        console.print(Panel(
            response.message,
            title="[red]✗ Error[/red]",
            border_style="red"
        ))
        
        # Show suggestions for fixing the error
        if response.suggestions:
            console.print(f"\n[bold yellow]Try:[/bold yellow]")
            for suggestion in response.suggestions:
                console.print(f"  • {suggestion}")


@app.command("setup")
def setup():
    """Set up the Image Generation Assistant (create .env file)."""
    
    console.print(Panel.fit(
        "[bold blue]Image Generation Assistant Setup[/bold blue]\n"
        "Configure your API keys for OpenAI and/or Fal.ai",
        title="Setup"
    ))
    
    # Check if .env already exists
    env_file = Path(".env")
    if env_file.exists():
        if not Confirm.ask("A .env file already exists. Overwrite it?"):
            console.print("[yellow]Setup cancelled.[/yellow]")
            return
    
    # Get API keys
    console.print("\n[bold]API Key Configuration[/bold]")
    console.print("You need at least one API key. You can add more later.")
    
    openai_key = Prompt.ask(
        "\nEnter your OpenAI API key (press Enter to skip)",
        password=True,
        default=""
    )
    
    fal_key = Prompt.ask(
        "Enter your Fal.ai API key (press Enter to skip)",
        password=True,
        default=""
    )
    
    if not openai_key and not fal_key:
        console.print("[red]At least one API key is required.[/red]")
        return
    
    # Write .env file
    with open(env_file, 'w') as f:
        if openai_key:
            f.write(f"OPENAI_API_KEY={openai_key}\n")
        if fal_key:
            f.write(f"FAL_KEY={fal_key}\n")
    
    # Show status
    providers = []
    if openai_key:
        providers.append("OpenAI DALL-E")
    if fal_key:
        providers.append("Fal.ai")
    
    console.print(Panel(
        f"[green]✓ Setup complete![/green]\n\n"
        f"Configured providers: {', '.join(providers)}\n"
        f"API keys saved to .env\n\n"
        f"Try: [cyan]image-assistant generate \"a beautiful sunset\"[/cyan]",
        title="Success"
    ))


@app.command("web")
def launch_web_ui(
    share: bool = typer.Option(False, "--share", help="Create a public share link"),
    port: int = typer.Option(7860, "--port", "-p", help="Port to run the web UI on"),
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind the web UI to"),
    auth: Optional[str] = typer.Option(None, "--auth", help="Authentication in format 'username:password'"),
):
    """Launch the web UI for the Image Generation Assistant."""
    
    try:
        from gradio_ui import launch_ui
    except ImportError:
        console.print("[red]Error: Gradio not installed. Run: pip install gradio>=4.0.0[/red]")
        return
    
    # Parse authentication if provided
    auth_tuple = None
    if auth:
        if ":" in auth:
            username, password = auth.split(":", 1)
            auth_tuple = (username, password)
        else:
            console.print("[red]Error: Auth must be in format 'username:password'[/red]")
            return
    
    console.print(Panel.fit(
        f"[bold blue]🎨 Image Generation Assistant - Web UI[/bold blue]\n\n"
        f"Starting web interface...\n"
        f"• **Host**: {host}\n"
        f"• **Port**: {port}\n"
        f"• **Share**: {'Yes (public link)' if share else 'No (local only)'}\n"
        f"• **Auth**: {'Enabled' if auth_tuple else 'Disabled'}\n\n"
        f"The web UI will open automatically in your browser.",
        title="Web UI"
    ))
    
    try:
        launch_ui(
            share=share,
            server_name=host,
            server_port=port,
            auth=auth_tuple
        )
    except Exception as e:
        console.print(f"[red]Failed to launch web UI: {e}[/red]")


if __name__ == "__main__":
    app() 