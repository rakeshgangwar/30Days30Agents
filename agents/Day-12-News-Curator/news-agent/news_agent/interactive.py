"""
Interactive web interface for the news curator agent.

This module provides a FastAPI-based web interface for interacting with the news curator agent.
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import fastapi
from fastapi import Depends, Request
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .agent import NewsCuratorAgent
from .config import Config, load_config
from .models import NewsArticle, UserPreferences

# Create the FastAPI app
app = fastapi.FastAPI(title="News Curator Agent")

# Get the directory of this file
THIS_DIR = Path(__file__).parent

# Create a global agent instance
config = load_config()
news_agent = NewsCuratorAgent(config)


class ChatMessage(BaseModel):
    """Format of messages sent to the browser."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str


@app.get("/")
async def index() -> FileResponse:
    """Serve the main HTML page."""
    html_path = THIS_DIR / "static" / "index.html"
    if not html_path.exists():
        # Create a basic HTML file if it doesn't exist
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>News Curator Agent</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 min-h-screen">
            <div class="container mx-auto p-4">
                <h1 class="text-2xl font-bold mb-4">News Curator Agent</h1>

                <div id="conversation" class="bg-white rounded-lg shadow p-4 mb-4 min-h-[400px] max-h-[600px] overflow-y-auto">
                    <!-- Messages will appear here -->
                </div>

                <form id="chat-form" class="flex gap-2">
                    <input
                        id="prompt-input"
                        type="text"
                        name="prompt"
                        placeholder="Ask about news, search for topics, or request a briefing..."
                        class="flex-1 p-2 border rounded"
                        required
                    >
                    <button
                        type="submit"
                        class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                    >
                        Send
                    </button>
                </form>

                <div id="spinner" class="hidden mt-2 text-center">
                    <div class="inline-block animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-blue-500"></div>
                    <span class="ml-2">Processing...</span>
                </div>

                <div id="error" class="hidden mt-2 p-2 bg-red-100 text-red-700 rounded">
                    An error occurred. Please try again.
                </div>
            </div>

            <script>
                const convElement = document.getElementById('conversation');
                const promptInput = document.getElementById('prompt-input');
                const spinner = document.getElementById('spinner');
                const errorElement = document.getElementById('error');
                const chatForm = document.getElementById('chat-form');

                // Function to add a message to the conversation
                function addMessage(message) {
                    const msgDiv = document.createElement('div');
                    msgDiv.classList.add('mb-4', 'p-2', 'rounded');

                    if (message.role === 'user') {
                        msgDiv.classList.add('bg-gray-200', 'ml-12');
                    } else {
                        msgDiv.classList.add('bg-blue-100', 'mr-12');
                    }

                    msgDiv.innerHTML = `<p class="text-sm text-gray-500">${message.role}</p><div>${message.content}</div>`;
                    convElement.appendChild(msgDiv);
                    convElement.scrollTop = convElement.scrollHeight;
                }

                // Function to handle form submission
                async function handleSubmit(e) {
                    e.preventDefault();
                    errorElement.classList.add('hidden');
                    spinner.classList.remove('hidden');

                    const prompt = promptInput.value;
                    promptInput.value = '';
                    promptInput.disabled = true;

                    // Add user message to conversation
                    addMessage({
                        role: 'user',
                        content: prompt,
                        timestamp: new Date().toISOString()
                    });

                    try {
                        const response = await fetch('/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ prompt })
                        });

                        if (!response.ok) {
                            throw new Error('Failed to get response');
                        }

                        const reader = response.body.getReader();
                        const decoder = new TextDecoder();
                        let assistantMessage = '';
                        let assistantDiv = null;

                        while (true) {
                            const { done, value } = await reader.read();
                            if (done) break;

                            const text = decoder.decode(value);
                            assistantMessage += text;

                            if (!assistantDiv) {
                                assistantDiv = document.createElement('div');
                                assistantDiv.classList.add('mb-4', 'p-2', 'rounded', 'bg-blue-100', 'mr-12');
                                assistantDiv.innerHTML = `<p class="text-sm text-gray-500">assistant</p><div>${assistantMessage}</div>`;
                                convElement.appendChild(assistantDiv);
                            } else {
                                assistantDiv.innerHTML = `<p class="text-sm text-gray-500">assistant</p><div>${assistantMessage}</div>`;
                            }

                            convElement.scrollTop = convElement.scrollHeight;
                        }
                    } catch (error) {
                        console.error('Error:', error);
                        errorElement.classList.remove('hidden');
                    } finally {
                        spinner.classList.add('hidden');
                        promptInput.disabled = false;
                        promptInput.focus();
                    }
                }

                chatForm.addEventListener('submit', handleSubmit);
            </script>
        </body>
        </html>
        """
        os.makedirs(THIS_DIR / "static", exist_ok=True)
        with open(html_path, "w") as f:
            f.write(html_content)

    return FileResponse(html_path, media_type="text/html")


@app.post("/chat")
async def chat(request: Request) -> StreamingResponse:
    """Handle chat requests and stream responses."""
    # Parse the request body
    body = await request.json()
    prompt = body.get("prompt", "")

    if not prompt:
        return Response("Prompt is required", status_code=400)

    async def stream_response():
        """Stream the agent's response."""
        try:
            # Process the user's message
            response_text = await process_user_message(prompt)

            # Stream the response
            for chunk in response_text.split(" "):
                yield f"{chunk} "
                await asyncio.sleep(0.01)  # Small delay for streaming effect

        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(stream_response(), media_type="text/plain")


async def process_user_message(message: str) -> str:
    """Process a user message and generate a response.

    Args:
        message: The user's message

    Returns:
        The agent's response
    """
    # Start MCP servers
    async with news_agent.agent.run_mcp_servers():
        # Use the agent to process the message
        result = await news_agent.agent.run(
            f"""
            You are a helpful news assistant. The user has sent the following message:

            {message}

            Based on this message, determine what the user wants:
            1. If they're asking for news on a specific topic, use search_news to find relevant articles
            2. If they want a briefing, use create_briefing to get recent news
            3. For any other query, respond helpfully

            Respond in a conversational manner.
            """
        )

        # If the message seems like a search query
        if any(keyword in message.lower() for keyword in ["search", "find", "look for", "articles about", "news about"]):
            # Extract the search query
            search_terms = message.lower()
            for prefix in ["search", "find", "look for", "articles about", "news about"]:
                search_terms = search_terms.replace(prefix, "").strip()

            # Determine which source to use
            source = "all"
            if "google" in message.lower():
                source = "google"
            elif "brave" in message.lower():
                source = "brave"
            elif "freshrss" in message.lower() or "feed" in message.lower():
                source = "freshrss"

            # Search for news
            articles = await news_agent.search_news(search_terms, source=source)

            if articles:
                response = f"I found {len(articles)} articles about '{search_terms}'"
                if source != "all":
                    response += f" from {source}"
                response += ":\n\n"

                for i, article in enumerate(articles[:5], 1):
                    response += f"{i}. **{article.title}** ({article.source}, {article.published_date.date()})\n"
                    response += f"   {article.url}\n\n"

                if len(articles) > 5:
                    response += f"\nAnd {len(articles) - 5} more articles."
            else:
                response = f"I couldn't find any articles about '{search_terms}'"
                if source != "all":
                    response += f" from {source}"
                response += ". Would you like to try a different search term or source?"

            return response

        # If the message seems like a briefing request
        elif any(keyword in message.lower() for keyword in ["briefing", "update me", "what's new", "latest news"]):
            # Create a briefing
            briefing = await news_agent.create_briefing()

            if briefing.articles:
                response = f"**News Briefing**\n\nHere are the latest articles:\n\n"

                # Add articles
                for i, article in enumerate(briefing.articles[:5], 1):
                    response += f"{i}. **{article.title}** ({article.source}, {article.published_date.date()})\n"

                if len(briefing.articles) > 5:
                    response += f"\nAnd {len(briefing.articles) - 5} more articles."
            else:
                response = "I couldn't find any recent news articles. Would you like to try a specific search instead?"

            return response

        # For other queries, return the agent's response
        return result.output


def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the FastAPI server.

    Args:
        host: Host to bind to
        port: Port to bind to
    """
    import uvicorn
    uvicorn.run("news_agent.interactive:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    run_server()
