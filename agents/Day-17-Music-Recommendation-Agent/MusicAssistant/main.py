import asyncio
import os

from pydantic_ai import Agent
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.mcp import MCPServerStdio
from dotenv import load_dotenv

# Import the MusicBrainz tools
from musicbrainz_tools import (
    search_artist,
    get_artist_info,
    search_release,
    get_release_info,
    search_track,
    get_cover_art
)

load_dotenv()

openrouter = OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY"))
model = OpenAIModel(
    provider=openrouter,
    model_name='qwen/qwen3-14b')

server = MCPServerStdio(  
    'uv',
    args=[
        '--directory',
        '/Users/rakeshgangwar/PycharmProjects/MusicAssistant/spotify-mcp',
        'run',
        'spotify-mcp',
    ],
    env={
        "SPOTIFY_CLIENT_ID": os.getenv("SPOTIFY_CLIENT_ID"),
        "SPOTIFY_CLIENT_SECRET": os.getenv("SPOTIFY_CLIENT_SECRET"),
        "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8080/callback"
    },
)


# Register the MusicBrainz tools with the agent
def mb_search_artist(query: str, limit: int = 10) -> list:
    """Search for artists by name in MusicBrainz database.

    Args:
        query: The artist name to search for
        limit: Maximum number of results to return (default: 5)
    """
    return search_artist(query, limit)

def mb_get_artist_info(artist_id: str) -> dict:
    """Get detailed information about an artist by their MusicBrainz ID.

    Args:
        artist_id: The MusicBrainz ID of the artist
    """
    return get_artist_info(artist_id)

def mb_search_release(query: str, limit: int = 50) -> list:
    """Search for releases (albums, singles, etc.) by title in MusicBrainz database.

    Args:
        query: The release title to search for
        limit: Maximum number of results to return (default: 5)
    """
    return search_release(query, limit)

def mb_get_release_info(release_id: str) -> dict:
    """Get detailed information about a release by its MusicBrainz ID.

    Args:
        release_id: The MusicBrainz ID of the release
    """
    return get_release_info(release_id)

def mb_search_track(query: str, limit: int = 50) -> list:
    """Search for tracks (recordings) by title in MusicBrainz database.

    Args:
        query: The track title to search for
        limit: Maximum number of results to return (default: 5)
    """
    return search_track(query, limit)

def mb_get_cover_art(release_id: str) -> dict:
    """Get cover art for a release by its MusicBrainz ID.

    Args:
        release_id: The MusicBrainz ID of the release
    """
    return get_cover_art(release_id)

musicbrainz_tools = [
    mb_search_artist,
    mb_get_artist_info,
    mb_search_release,
    mb_get_release_info,
    mb_search_track,
    mb_get_cover_art
]

agent = Agent(
    model=model, 
    mcp_servers=[server],  # Uncommented to enable Spotify integration
    tools=musicbrainz_tools,
    system_prompt="I'm a music assistant that can help you find information about artists, albums, and tracks using MusicBrainz data (when searching MusizBrainz data use limits of 50 for searching songs), and can play music through Spotify."
)

async def conversational_agent():
    message_history = []
    print("Music Assistant is ready! Type '/exit' to quit.")
    
    async with agent.run_mcp_servers():
        while True:
            user_input = input("\nYou: ")
            
            if user_input.lower() == "/exit":
                print("Goodbye!")
                break
                
            if user_input.lower() == "/clear":
                message_history = []
                print("Conversation history cleared.")
                continue
                
            # Run the agent with the user input and message history
            result = await agent.run(user_input, message_history=message_history)
            
            # Store the messages from this interaction for the next run
            message_history = result.all_messages()
            
            # Print the agent's response
            print(f"\nMusic Assistant: {result.output}")


if __name__ == '__main__':
    # Run the conversational agent by default
    asyncio.run(conversational_agent())
    # print(search_artist("Arijit Singh", 5))