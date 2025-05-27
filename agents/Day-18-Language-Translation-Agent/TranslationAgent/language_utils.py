"""
Utility functions and constants for language handling.
"""

# Supported languages mapping
SUPPORTED_LANGUAGES = {
    'English': 'English',
    'Spanish': 'Spanish',
    'French': 'French',
    'German': 'German',
    'Italian': 'Italian',
    'Portuguese': 'Portuguese',
    'Chinese': 'Chinese',
    'Japanese': 'Japanese',
    'Korean': 'Korean',
    'Arabic': 'Arabic',
    'Hindi': 'Hindi'
}

# Language code to name mapping for detection
LANGUAGE_CODE_MAP = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'zh': 'Chinese',
    'zh-cn': 'Chinese',
    'zh-tw': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'ru': 'Russian',
    'nl': 'Dutch',
    'sv': 'Swedish',
    'da': 'Danish',
    'no': 'Norwegian',
    'fi': 'Finnish',
    'pl': 'Polish',
    'tr': 'Turkish',
    'hi': 'Hindi',
    'th': 'Thai',
    'vi': 'Vietnamese'
}

def get_language_name(language_code):
    """
    Get the full language name from a language code.
    
    Args:
        language_code (str): Language code (e.g., 'en', 'es')
        
    Returns:
        str: Full language name
    """
    return LANGUAGE_CODE_MAP.get(language_code, 'Unknown')

def chunk_text(text, max_length=1500):
    """
    Split text into chunks that fit within the model's context window.
    
    Args:
        text (str): Text to chunk
        max_length (int): Maximum length per chunk
        
    Returns:
        list: List of text chunks
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by sentences first
    sentences = text.split('. ')
    
    for i, sentence in enumerate(sentences):
        # Add period back except for last sentence
        if i < len(sentences) - 1:
            sentence += '. '
        
        # If adding this sentence would exceed the limit
        if len(current_chunk) + len(sentence) > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                # If single sentence is too long, split by words
                words = sentence.split()
                temp_chunk = ""
                for word in words:
                    if len(temp_chunk) + len(word) + 1 > max_length:
                        if temp_chunk:
                            chunks.append(temp_chunk.strip())
                            temp_chunk = word
                        else:
                            # Single word is too long, just add it
                            chunks.append(word)
                    else:
                        temp_chunk += " " + word if temp_chunk else word
                
                if temp_chunk:
                    current_chunk = temp_chunk
        else:
            current_chunk += sentence
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks

def validate_language(language):
    """
    Validate if a language is supported.
    
    Args:
        language (str): Language name to validate
        
    Returns:
        bool: True if language is supported
    """
    return language in SUPPORTED_LANGUAGES

def get_language_pairs():
    """
    Get all possible language pairs for translation.
    
    Returns:
        list: List of tuples (source, target) for all valid pairs
    """
    languages = list(SUPPORTED_LANGUAGES.keys())
    pairs = []
    
    for source in languages:
        for target in languages:
            if source != target:
                pairs.append((source, target))
    
    return pairs
