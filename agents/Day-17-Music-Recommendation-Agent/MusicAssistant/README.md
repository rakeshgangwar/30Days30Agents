# Music Assistant

A powerful music assistant that helps you discover music information and control playback through a conversational interface. Built with Python, MusicBrainz API, and Spotify integration.

## Features

- **Artist Search**: Find detailed information about artists
- **Album/Release Lookup**: Get information about albums and releases
- **Track Search**: Search for specific songs
- **Cover Art**: View album artwork
- **Spotify Integration**: Control music playback (requires Spotify Premium)
- **Conversational Interface**: Natural language interaction

## Prerequisites

- Python 3.8+
- Spotify Premium account (for playback features)
- MusicBrainz API access (no API key required)
- OpenRouter API key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/music-assistant.git
   cd music-assistant
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

4. Copy the example environment file and add your credentials:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your OpenRouter API key and Spotify credentials.

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
# OpenRouter API key
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Spotify API credentials
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8080/callback
```

## Usage

1. Start the Music Assistant:
   ```bash
   python main.py
   ```

2. Interact with the assistant using natural language. For example:
   - "Search for The Beatles"
   - "Find albums by Taylor Swift"
   - "Play Bohemian Rhapsody on Spotify"
   - "Show me information about the album Thriller"

3. Available commands:
   - `/exit` - Exit the application
   - `/clear` - Clear the conversation history

## MusicBrainz Integration

The application uses the MusicBrainz API to search for artists, albums, and tracks. By default, it will return up to 50 results for searches.

### Search Limits
- Artists: 10 results
- Releases/Albums: 50 results
- Tracks: 50 results

## Spotify Integration

To use Spotify features:

1. Create a Spotify Developer account at [Spotify for Developers](https://developer.spotify.com/)
2. Create a new application and get your client ID and secret
3. Add `http://127.0.0.1:8080/callback` as a redirect URI in your Spotify Developer Dashboard
4. Add your credentials to the `.env` file

## Logging

The application logs all API interactions to `musicbrainz.log` in the project root. This can be useful for debugging and monitoring API usage.

## Rate Limiting

The application implements rate limiting to comply with MusicBrainz API guidelines (1 request per second).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [MusicBrainz](https://musicbrainz.org/) for the music metadata
- [Spotify](https://www.spotify.com/) for music playback
- [OpenRouter](https://openrouter.ai/) for language model access