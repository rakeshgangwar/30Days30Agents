"""Main entry point for the Image Generation Assistant."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

try:
    from cli import app as cli_app
    from agent import run_image_assistant, run_image_assistant_sync
    from config import get_config
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Main entry point with interface selection."""
    if len(sys.argv) > 1:
        # If arguments provided, use CLI
        from cli import app
        app()
    else:
        # No arguments, show interface selection
        import typer
        from rich.console import Console
        from rich.panel import Panel
        from rich.prompt import Prompt
        
        console = Console()
        
        console.print(Panel.fit(
            "[bold blue]🎨 Image Generation Assistant[/bold blue]\n\n"
            "Choose your interface:\n"
            "1. **Web UI** - Beautiful web interface (recommended)\n"
            "2. **CLI** - Command-line interface\n"
            "3. **Chat** - Interactive chat mode\n"
            "4. **Help** - Show available commands",
            title="Welcome"
        ))
        
        choice = Prompt.ask(
            "\n[bold cyan]Select interface[/bold cyan]",
            choices=["1", "2", "3", "4", "web", "cli", "chat", "help"],
            default="1"
        )
        
        if choice in ["1", "web"]:
            try:
                from gradio_ui import launch_ui
                console.print("\n🌐 [bold green]Starting Web UI...[/bold green]")
                launch_ui(share=False)
            except ImportError:
                console.print("\n[red]❌ Gradio not installed. Install with: pip install gradio>=4.0.0[/red]")
                console.print("Falling back to CLI...")
                from cli import app
                app()
        elif choice in ["2", "cli"]:
            from cli import app
            # Show CLI help
            sys.argv = ["main.py", "--help"]
            app()
        elif choice in ["3", "chat"]:
            from cli import interactive_chat
            interactive_chat()
        elif choice in ["4", "help"]:
            from cli import app
            sys.argv = ["main.py", "--help"]
            app()


def demo():
    """Run a simple demo of the Image Generation Assistant."""
    print("🎨 Image Generation Assistant Demo")
    print("=" * 40)
    
    # Test prompts
    test_prompts = [
        "Generate a beautiful sunset over mountains",
        "Enhance this prompt: cat wearing hat",
        "Show my recent images",
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{i}. Testing: {prompt}")
        print("-" * 30)
        
        try:
            response = run_image_assistant_sync(prompt)
            print(f"Success: {response.success}")
            print(f"Message: {response.message}")
            
            if response.images:
                print(f"Generated images: {len(response.images)}")
                for img_path in response.images:
                    print(f"  - {img_path}")
            
            if response.suggestions:
                print("Suggestions:")
                for suggestion in response.suggestions:
                    print(f"  • {suggestion}")
                    
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main() 