import asyncio
import streamlit as st
import cohere
import edge_tts
import subprocess
import os
import tempfile

# Initialize Cohere API
COHERE_API_KEY = "3qeisnbsUVIPBtO06V6Tk5szXvIZphbgWAcKckQ1"
cohere_client = cohere.Client(COHERE_API_KEY)

# Function to generate a translated script using Cohere
def generate_translated_script(text, target_language):
    response = cohere_client.generate(
        model="xlarge",
        prompt=f"Translate the following text into {target_language}:\n{text}",
        max_tokens=1000
    )
    return response.generations[0].text.strip()

# Function to convert text to speech using Edge TTS
async def text_to_speech(text, voice, output_path):
    communicator = edge_tts.Communicate(text, voice)
    await communicator.save(output_path)
    return output_path

# Function to merge audio and video using FFmpeg
def merge_audio_video(video_path, audio_path, output_path):
    command = f"ffmpeg -i {video_path} -i {audio_path} -c:v copy -c:a aac -shortest {output_path}"
    subprocess.run(command, shell=True, check=True)

# Streamlit UI
st.title("AI-Powered Auto Dubbing Service")

st.write("""
This app lets you translate and dub a video into another language using AI. 
Upload a video, provide a script, and select the target language!
""")

# File uploader for the video
uploaded_video = st.file_uploader("Upload a video file (MP4 format)", type=["mp4"])

# Text input for the original script
input_script = st.text_area("Enter the script for dubbing", placeholder="Type the original script here...")

# Language selection for translation
target_language = st.selectbox("Select the target language for translation", ["Spanish", "French", "German", "Italian"])

# Button to start processing
if st.button("Generate Dubbed Video"):
    if uploaded_video is None:
        st.error("Please upload a video file.")
    elif not input_script.strip():
        st.error("Please provide a script for dubbing.")
    else:
        with st.spinner("Processing..."):
            try:
                # Save uploaded video to a temporary file
                temp_video_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                temp_video_file.write(uploaded_video.read())
                temp_video_path = temp_video_file.name

                # Translate the script
                translated_script = generate_translated_script(input_script, target_language)

                # Convert text to speech
                audio_output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                asyncio.run(text_to_speech(translated_script, voice="en-US-AriaNeural", output_path=audio_output_path))

                # Merge audio and video
                output_video_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                merge_audio_video(temp_video_path, audio_output_path, output_video_path)

                # Provide download links
                st.success("Dubbed video generated successfully!")
                st.video(output_video_path)
                st.download_button("Download Dubbed Video", open(output_video_path, "rb"), file_name="dubbed_video.mp4")
            except Exception as e:
                st.error(f"An error occurred: {e}")
