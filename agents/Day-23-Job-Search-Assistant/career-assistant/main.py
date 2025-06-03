"""Career Application Assistant - Main Entry Point"""

import asyncio
import os
from dotenv import load_dotenv
from streamlined_cli import main as streamlined_main
from rich.console import Console

# Load environment variables
load_dotenv()
console = Console()

def main():
    """Main entry point for the Career Application Assistant."""
    # Ensure OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        console.print("⚠️  [yellow]Please set your OPENAI_API_KEY environment variable[/yellow]")
        console.print("You can add it to a .env file in this directory:")
        console.print("OPENAI_API_KEY=your_api_key_here")
        console.print("\nCopy from env_example.txt:")
        console.print("cp env_example.txt .env")
        return
    
    console.print("\n[bold cyan]🚀 Career Application Assistant[/bold cyan]")
    console.print("[green]🎯 Starting application package generator...[/green]")
    
    # Run the streamlined CLI
    asyncio.run(streamlined_main())


if __name__ == "__main__":
    main()
