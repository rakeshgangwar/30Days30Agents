import os
from openai import OpenAI
from langdetect import detect, LangDetectException
from language_utils import LANGUAGE_CODE_MAP, chunk_text

class LanguageTranslator:
    def __init__(self):
        """Initialize the translator with OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
    
    def detect_language(self, text):
        """
        Detect the language of the input text.
        
        Args:
            text (str): Text to detect language for
            
        Returns:
            str: Language code (e.g., 'en', 'es', 'fr')
        """
        try:
            # Clean text for better detection
            cleaned_text = text.strip()
            if len(cleaned_text) < 3:
                return 'en'  # Default to English for very short texts
            
            # Use OpenAI for more accurate language detection
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a language detection expert. Identify the language of the given text and respond with only the 2-letter ISO language code (e.g., 'en', 'fr', 'es', 'de', etc.). Do not provide any explanation."
                    },
                    {
                        "role": "user",
                        "content": f"Detect the language of this text: {cleaned_text}"
                    }
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            detected_code = response.choices[0].message.content
            if detected_code is not None:
                detected_code = detected_code.strip().lower()
                # Validate the response is a proper language code
                if detected_code and len(detected_code) == 2 and detected_code.isalpha():
                    return detected_code
            
            # Fallback to langdetect
            return detect(cleaned_text)
        except Exception:
            # Final fallback to English if all detection fails
            return 'en'
    
    def translate_with_openai(self, text, target_language, source_language=None):
        """
        Translate text using OpenAI's GPT model.
        
        Args:
            text (str): Text to translate
            target_language (str): Target language name
            source_language (str, optional): Source language name
            
        Returns:
            str: Translated text
        """
        try:
            # Construct the prompt
            if source_language:
                prompt = f"""
                Translate the following text from {source_language} to {target_language}.
                Provide only the translation without any explanations or additional text.
                
                Text to translate:
                {text}
                """
            else:
                prompt = f"""
                Translate the following text to {target_language}.
                Provide only the translation without any explanations or additional text.
                
                Text to translate:
                {text}
                """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate the text accurately and naturally. "
                                 "Return ONLY the translated text with no explanations, notes, or additional commentary."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent translations
                max_tokens=2000
            )
            
            translated_text = response.choices[0].message.content
            if translated_text is not None:
                translated_text = translated_text.strip()
            return translated_text or ""
            
        except Exception as e:
            raise Exception(f"OpenAI translation failed: {str(e)}")
    
    def translate_text(self, text, target_language, source_language=None):
        """
        Main translation function that handles the complete translation process.
        
        Args:
            text (str): Text to translate
            target_language (str): Target language name
            source_language (str, optional): Source language name
            
        Returns:
            dict: Translation result with detected language and translated text
        """
        if not text or not text.strip():
            raise ValueError("Input text cannot be empty")
        
        # Detect source language if not provided
        if not source_language:
            detected_code = self.detect_language(text)
            detected_language = LANGUAGE_CODE_MAP.get(detected_code or 'en', 'English')
        else:
            detected_language = source_language
            detected_code = None
            # Find the language code for the provided source language
            for code, lang in LANGUAGE_CODE_MAP.items():
                if lang.lower() == source_language.lower():
                    detected_code = code
                    break
        
        # Check if source and target are the same (but still translate to ensure proper output)
        # This ensures we always get a clean translation even if languages seem similar
        
        # Handle long texts by chunking
        chunks = chunk_text(text, max_length=1500)
        translated_chunks = []
        
        for chunk in chunks:
            if chunk.strip():  # Only translate non-empty chunks
                translated_chunk = self.translate_with_openai(
                    chunk, 
                    target_language, 
                    detected_language
                )
                translated_chunks.append(translated_chunk)
        
        # Combine translated chunks
        final_translation = ' '.join(translated_chunks)
        
        return {
            'translated_text': final_translation,
            'detected_language': detected_code or 'en',
            'source_language': detected_language,
            'target_language': target_language
        }
