import streamlit as st
import time
from translator import LanguageTranslator
from language_utils import SUPPORTED_LANGUAGES, get_language_name


# Initialize the translator and voice processor
@st.cache_resource
def get_translator():
    return LanguageTranslator()



def main():
    st.set_page_config(
        page_title="Language Translation Tool",
        page_icon="🌐",
        layout="wide"
    )
    
    st.title("🌐 Language Translation Tool")
    st.markdown("Translate text between multiple languages with automatic language detection powered by OpenAI")
    
    translator = get_translator()
    

    
    # Create two columns for better layout
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Input Text")
        
        # Text input area
        input_text = st.text_area(
            "Enter text to translate:",
            height=200,
            placeholder="Type or paste your text here..."
        )
        
        # Language detection option
        auto_detect = st.checkbox("🔍 Auto-detect source language", value=True)
        
        source_language = None
        if not auto_detect:
            source_language = st.selectbox(
                "Source Language:",
                options=list(SUPPORTED_LANGUAGES.keys()),
                index=0
            )
    
    with col2:
        st.subheader("🎯 Translation Settings")
        
        # Target language selection
        target_language = st.selectbox(
            "Target Language:",
            options=list(SUPPORTED_LANGUAGES.keys()),
            index=1  # Default to Spanish
        )
        
        # Translation button
        translate_button = st.button("🔄 Translate", type="primary", use_container_width=True)
    
    # Translation results section
    st.markdown("---")
    
    if translate_button:
        if not input_text.strip():
            st.error("⚠️ Please enter some text to translate.")
            return
        
        if not auto_detect and source_language == target_language:
            st.error("⚠️ Source and target languages cannot be the same.")
            return
        
        # Show loading spinner
        with st.spinner("🔄 Translating..."):
            try:
                # Perform translation
                result = translator.translate_text(
                    text=input_text,
                    target_language=SUPPORTED_LANGUAGES[target_language],
                    source_language=SUPPORTED_LANGUAGES[source_language] if not auto_detect and source_language else None
                )
                
                # Display results
                st.subheader("📋 Translation Results")
                
                # Create columns for source and target
                result_col1, result_col2 = st.columns([1, 1])
                
                with result_col1:
                    detected_lang_name = get_language_name(result['detected_language'])
                    st.markdown(f"**Source ({detected_lang_name}):**")
                    st.text_area(
                        "Original text:",
                        value=input_text,
                        height=150,
                        disabled=True,
                        key="source_display"
                    )
                
                with result_col2:
                    st.markdown(f"**Target ({target_language}):**")
                    st.text_area(
                        "Translated text:",
                        value=result['translated_text'],
                        height=150,
                        disabled=True,
                        key="target_display"
                    )
                
                # Additional information
                st.info(f"✅ Translation completed successfully! Detected source language: {detected_lang_name}")
                
                # Copy functionality
                st.info("💡 Use Ctrl+C (or Cmd+C) to copy the translated text from the text area above.")
                
            except Exception as e:
                st.error(f"❌ Translation failed: {str(e)}")
                st.info("💡 Please check your internet connection and try again.")
    
    # Sidebar with information
    with st.sidebar:
        st.markdown("### 🌍 Supported Languages")
        st.markdown("This tool supports translation between:")
        
        for lang in SUPPORTED_LANGUAGES.keys():
            st.markdown(f"• {lang}")
        
        st.markdown("---")
        st.markdown("### 🔧 Features")
        st.markdown("""
        • **Automatic language detection**
        • **High-quality AI translation**
        • **Support for long texts**
        • **Multiple language pairs**
        • **Real-time translation**
        • **11 language support including Hindi**
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This translation tool uses OpenAI's advanced language models
        to provide accurate and contextual translations between multiple languages.
        """)

if __name__ == "__main__":
    main()
