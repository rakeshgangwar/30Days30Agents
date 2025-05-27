import requests
import json
import time
import logging
from typing import Dict, List, Optional, Union, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("musicbrainz.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("musicbrainz_tools")

# Base URL for the MusicBrainz API
BASE_URL = "https://musicbrainz.org/ws/2"

# User agent for API requests (required by MusicBrainz API)
USER_AGENT = "MusicAssistant/0.1 (ursrakesh2006@gmail.com)"

# Headers for API requests
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "application/json"
}

# Rate limiting to respect MusicBrainz API guidelines (1 request per second)
def rate_limit_request(func):
    """Decorator to rate limit requests to the MusicBrainz API"""
    last_request_time = 0
    
    def wrapper(*args, **kwargs):
        nonlocal last_request_time
        current_time = time.time()
        time_since_last_request = current_time - last_request_time
        
        # If less than 1 second has passed since the last request, wait
        if time_since_last_request < 1:
            wait_time = 1 - time_since_last_request
            logger.debug(f"Rate limiting: Waiting {wait_time:.2f} seconds before next request")
            time.sleep(wait_time)
        
        result = func(*args, **kwargs)
        last_request_time = time.time()
        return result
    
    return wrapper

@rate_limit_request
def make_request(endpoint: str, params: Dict = None) -> Dict:
    """
    Make a request to the MusicBrainz API
    
    Args:
        endpoint: API endpoint to request
        params: Query parameters for the request
        
    Returns:
        JSON response from the API
    """
    url = f"{BASE_URL}/{endpoint}"
    logger.info(f"Making request to: {url} with params: {params}")
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        logger.info(f"Request successful: {response.status_code}")
        logger.debug(f"Response content: {response.text[:200]}..." if len(response.text) > 200 else response.text)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return {"error": f"API request failed: {str(e)}"}

def search_artist(query: str, limit: int = 10) -> List[Dict]:
    """
    Search for artists by name using the MusicBrainz API
    
    Args:
        query: The artist name to search for
        limit: Maximum number of results to return (default: 5)
        
    Returns:
        List of artists matching the query
    """
    logger.info(f"Searching for artist: {query} with limit: {limit}")
    params = {
        "query": query,
        "limit": limit,
        "fmt": "json"
    }
    
    result = make_request("artist", params)
    
    if "error" in result:
        logger.error(f"Error searching for artist: {result['error']}")
        return result
    
    artists = result.get("artists", [])
    logger.info(f"Found {len(artists)} artists matching query: {query}")
    
    # Format the results for better readability
    formatted_artists = []
    for artist in artists:
        formatted_artist = {
            'id': artist.get('id'),
            'name': artist.get('name'),
            'type': artist.get('type', 'Unknown'),
            'country': artist.get('country', 'Unknown'),
            'disambiguation': artist.get('disambiguation', '')
        }
        formatted_artists.append(formatted_artist)
        
    return formatted_artists

def get_artist_info(artist_id: str) -> Dict:
    """
    Get detailed information about an artist by their MusicBrainz ID
    
    Args:
        artist_id: The MusicBrainz ID of the artist
        
    Returns:
        Detailed information about the artist
    """
    logger.info(f"Getting info for artist ID: {artist_id}")
    params = {
        "inc": "url-rels+aliases",
        "fmt": "json"
    }
    
    result = make_request(f"artist/{artist_id}", params)
    
    if "error" in result:
        logger.error(f"Error getting artist info: {result['error']}")
        return result
    
    logger.info(f"Successfully retrieved info for artist: {result.get('name', 'Unknown')}")
    
    # Format the results for better readability
    formatted_artist = {
        'id': result.get('id'),
        'name': result.get('name'),
        'type': result.get('type', 'Unknown'),
        'country': result.get('country', 'Unknown'),
        'gender': result.get('gender', 'Unknown'),
        'disambiguation': result.get('disambiguation', ''),
        'life-span': result.get('life-span', {})
    }
    
    # Extract aliases if available
    if 'aliases' in result:
        formatted_artist['aliases'] = [alias.get('name') for alias in result.get('aliases', [])]
        logger.debug(f"Found {len(formatted_artist['aliases'])} aliases for artist")
    
    # Extract URLs if available
    if 'relations' in result:
        formatted_artist['urls'] = {}
        for relation in result.get('relations', []):
            if relation.get('type') == 'url':
                formatted_artist['urls'][relation.get('type-id')] = relation.get('url', {}).get('resource')
        logger.debug(f"Found {len(formatted_artist.get('urls', {}))} URLs for artist")
    
    return formatted_artist

def search_release(query: str, limit: int = 50) -> List[Dict]:
    """
    Search for releases (albums, singles, etc.) by title using the MusicBrainz API
    
    Args:
        query: The release title to search for
        limit: Maximum number of results to return (default: 5)
        
    Returns:
        List of releases matching the query
    """
    logger.info(f"Searching for release: {query} with limit: {limit}")
    params = {
        "query": query,
        "limit": limit,
        "fmt": "json"
    }
    
    result = make_request("release", params)
    
    if "error" in result:
        logger.error(f"Error searching for release: {result['error']}")
        return result
    
    releases = result.get("releases", [])
    logger.info(f"Found {len(releases)} releases matching query: {query}")
    
    # Format the results for better readability
    formatted_releases = []
    for release in releases:
        formatted_release = {
            'id': release.get('id'),
            'title': release.get('title'),
            'status': release.get('status', 'Unknown'),
            'date': release.get('date', 'Unknown'),
            'country': release.get('country', 'Unknown')
        }
        
        # Extract artist credit information
        if 'artist-credit' in release:
            formatted_release['artist-credit'] = []
            for credit in release.get('artist-credit', []):
                if 'artist' in credit:
                    formatted_release['artist-credit'].append({
                        'name': credit.get('artist', {}).get('name')
                    })
        
        formatted_releases.append(formatted_release)
        
    return formatted_releases

def get_release_info(release_id: str) -> Dict:
    """
    Get detailed information about a release by its MusicBrainz ID
    
    Args:
        release_id: The MusicBrainz ID of the release
        
    Returns:
        Detailed information about the release including tracks
    """
    logger.info(f"Getting info for release ID: {release_id}")
    params = {
        "inc": "recordings+artists+labels+url-rels",
        "fmt": "json"
    }
    
    result = make_request(f"release/{release_id}", params)
    
    if "error" in result:
        logger.error(f"Error getting release info: {result['error']}")
        return result
    
    logger.info(f"Successfully retrieved info for release: {result.get('title', 'Unknown')}")
    
    # Format the results for better readability
    formatted_release = {
        'id': result.get('id'),
        'title': result.get('title'),
        'status': result.get('status', 'Unknown'),
        'date': result.get('date', 'Unknown'),
        'country': result.get('country', 'Unknown'),
        'barcode': result.get('barcode', 'Unknown')
    }
    
    # Extract artist credit information
    if 'artist-credit' in result:
        formatted_release['artist-credit'] = []
        for credit in result.get('artist-credit', []):
            if 'artist' in credit:
                formatted_release['artist-credit'].append({
                    'name': credit.get('artist', {}).get('name'),
                    'id': credit.get('artist', {}).get('id')
                })
    
    # Extract label information
    if 'label-info' in result:
        formatted_release['label-info'] = []
        for info in result.get('label-info', []):
            label_info = {
                'catalog-number': info.get('catalog-number', 'Unknown')
            }
            if 'label' in info:
                label_info['label'] = info.get('label', {}).get('name', 'Unknown')
            formatted_release['label-info'].append(label_info)
    
    # Extract track information
    if 'media' in result:
        formatted_release['tracks'] = []
        for medium in result.get('media', []):
            for track in medium.get('tracks', []):
                formatted_track = {
                    'position': track.get('position'),
                    'title': track.get('title'),
                    'length': track.get('length')
                }
                if 'recording' in track:
                    formatted_track['recording-id'] = track.get('recording', {}).get('id')
                formatted_release['tracks'].append(formatted_track)
        
        logger.debug(f"Found {len(formatted_release.get('tracks', []))} tracks for release")
    
    return formatted_release

def search_track(query: str, limit: int = 50) -> List[Dict]:
    """
    Search for tracks (recordings) by title using the MusicBrainz API
    
    Args:
        query: The track title to search for
        limit: Maximum number of results to return (default: 5)
        
    Returns:
        List of tracks matching the query
    """
    logger.info(f"Searching for track: {query} with limit: {limit}")
    params = {
        "query": query,
        "limit": limit,
        "fmt": "json"
    }
    
    result = make_request("recording", params)
    
    if "error" in result:
        logger.error(f"Error searching for track: {result['error']}")
        return result
    
    recordings = result.get("recordings", [])
    logger.info(f"Found {len(recordings)} tracks matching query: {query}")
    
    # Format the results for better readability
    formatted_recordings = []
    for recording in recordings:
        formatted_recording = {
            'id': recording.get('id'),
            'title': recording.get('title'),
            'length': recording.get('length')
        }
        
        # Extract artist credit information
        if 'artist-credit' in recording:
            formatted_recording['artist-credit'] = []
            for credit in recording.get('artist-credit', []):
                if 'artist' in credit:
                    formatted_recording['artist-credit'].append({
                        'name': credit.get('artist', {}).get('name')
                    })
        
        # Extract release information
        if 'releases' in recording:
            formatted_recording['releases'] = []
            for release in recording.get('releases', []):
                formatted_recording['releases'].append({
                    'title': release.get('title'),
                    'id': release.get('id')
                })
        
        formatted_recordings.append(formatted_recording)
        
    return formatted_recordings

def get_cover_art(release_id: str) -> Dict:
    """
    Get cover art for a release by its MusicBrainz ID using the Cover Art Archive API
    
    Args:
        release_id: The MusicBrainz ID of the release
        
    Returns:
        Information about available cover art including URLs
    """
    logger.info(f"Getting cover art for release ID: {release_id}")
    # Cover Art Archive API is separate from MusicBrainz API
    url = f"http://coverartarchive.org/release/{release_id}"
    
    try:
        logger.debug(f"Making request to Cover Art Archive: {url}")
        response = requests.get(url, headers={"User-Agent": USER_AGENT})
        response.raise_for_status()
        result = response.json()
        
        # Format the results to include thumbnail URLs
        formatted_images = []
        for image in result.get('images', []):
            formatted_image = {
                'types': image.get('types', []),
                'front': 'Front' in image.get('types', []),
                'back': 'Back' in image.get('types', []),
                'approved': image.get('approved', False),
                'thumbnails': {
                    'small': image.get('thumbnails', {}).get('small', ''),
                    'large': image.get('thumbnails', {}).get('large', '')
                },
                'image': image.get('image', '')
            }
            formatted_images.append(formatted_image)
        
        logger.info(f"Successfully retrieved {len(formatted_images)} cover art images")
        return formatted_images
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None and e.response.status_code == 404:
            logger.warning(f"No cover art found for release ID: {release_id}")
            return "No cover art found for this release"
        logger.error(f"Error getting cover art: {str(e)}")
        return f"Error getting cover art: {str(e)}"
