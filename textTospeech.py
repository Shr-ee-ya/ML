import cohere
from gtts import gTTS
import streamlit as st
import os
import tempfile

# Initialize the Cohere client with your API key
co = cohere.Client('3qeisnbsUVIPBtO06V6Tk5szXvIZphbgWAcKckQ1')  # Replace 'your-api-key' with your actual API key

# Streamlit app
st.title('Text-to-Speech with Cohere and Streamlit')

# Input field for the user to type a text
user_input = st.text_area("Enter text or generate summary from Cohere:")

# Option to generate text with Cohere
if st.button('Generate Summary with Cohere'):
    # Example: Long text for summarization (replace with any text of your choice)
    long_text = """
    Artificial Intelligence (AI) has seen incredible growth in recent years. From natural language processing to autonomous vehicles, the potential of AI is vast. However, there are concerns around ethics, privacy, and the impact on jobs and society. Developers and researchers are working on making AI more transparent, ethical, and understandable, ensuring that AI systems benefit humanity as a whole. The future of AI will continue to be shaped by advancements in machine learning and deep learning algorithms.
    """
    
    # Request to summarize the text using Cohere
    response = co.summarize(
        text=long_text,
        length='short',  # You can change to 'medium' or 'long' based on your preference
    )

    # Display the generated summary
    user_input = response.summary
    st.subheader("Generated Summary:")
    st.write(user_input)

# Convert text to speech if there's any input
if user_input:
    if st.button("Convert Text to Speech"):
        # Use gTTS to convert text to speech
        tts = gTTS(text=user_input, lang='en')
        
        # Save the speech to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as fp:
            tts.save(fp.name)
            audio_file = fp.name
        
        # Provide audio player in Streamlit
        st.audio(audio_file, format="audio/mp3")