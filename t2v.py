import gradio as gr
import edge_tts
import asyncio
import tempfile
import os
from moviepy.editor import AudioFileClip
from moviepy.editor import VideoFileClip, TextClip


# Get all available voices
async def get_voices():
    voices = await edge_tts.list_voices()
    return {f"{v['ShortName']} ({v['Locale']}, {v['Gender']})": v['ShortName'] for v in voices}

# Text to speech functionality
async def text_to_speech(text, voice, rate, pitch, output_path):
    if not text.strip():
        return None, gr.Warning("Please enter the text to convert into voice")
    if not voice:
        return None, gr.Warning("Please select a voice.")
    
    voice_short_name = voice.split(" (")[0]
    rate_str = f"{rate:+d}%"
    pitch_str = f"{pitch:+d}Hz"
    communicate = edge_tts.Communicate(text, voice_short_name, rate=rate_str, pitch=pitch_str)
    
    # Save to the specified output path
    await communicate.save(output_path)
    return output_path, None

# async def text_to_speech(text, voice, rate, pitch):
#     if not text.strip():
#         return None, gr.Warning("Please enter the text to convert.")
#     if not voice:
#         return None, gr.Warning("Please select a voice.")
    
#     voice_short_name = voice.split(" (")[0]
#     rate_str = f"{rate:+d}%"
#     pitch_str = f"{pitch:+d}Hz"
#     communicate = edge_tts.Communicate(text, voice_short_name, rate=rate_str, pitch=pitch_str)
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
#         tmp_path = tmp_file.name
#         await communicate.save(tmp_path)
#     return tmp_path, None

# Generate SRT file with specified lines of subtitles
def generate_srt(words, audio_duration, srt_path, num_lines):
    with open(srt_path, 'w', encoding='utf-8') as srt_file:
        total_segments = max(len(words) // (5 * num_lines), 1)  # Ensure at least one segment
        segment_duration = audio_duration / total_segments
        
        current_time = 0
        for i in range(0, len(words), 5 * num_lines):
            lines = []
            for j in range(num_lines):
                line_start = i + j * 5
                line_end = line_start + 5
                line = ' '.join(words[line_start:line_end])
                if line:
                    lines.append(line)

            start_time = current_time
            end_time = start_time + segment_duration
            
            start_time_str = format_srt_time(start_time)
            end_time_str = format_srt_time(end_time)
            srt_file.write(f"{i // (5 * num_lines) + 1}\n{start_time_str} --> {end_time_str}\n" + "\n".join(lines) + "\n\n")
            
            current_time += segment_duration

    return srt_path

# def generate_srt(words, audio_duration, srt_path, num_lines):
#     with open(srt_path, 'w', encoding='utf-8') as srt_file:
#         divisor = len(words) // (5 * num_lines)
#         if divisor == 0:
#             segment_duration = audio_duration  # Use full duration as fallback
#         else:
#             segment_duration = audio_duration / divisor  # Calculate duration per segment
        
#         current_time = 0
#         for i in range(0, len(words), 5 * num_lines):
#             lines = []
#             for j in range(num_lines):
#                 line = ' '.join(words[i + j * 5:i + (j + 1) * 5])
#                 if line:
#                     lines.append(line)
            
#             start_time = current_time
#             end_time = start_time + segment_duration
#             start_time_str = format_srt_time(start_time)
#             end_time_str = format_srt_time(end_time)
#             srt_file.write(f"{i // (5 * num_lines) + 1}\n{start_time_str} --> {end_time_str}\n" + "\n".join(lines) + "\n\n")
#             current_time += segment_duration

#     return srt_path


def format_srt_time(seconds):
    millis = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    minutes = seconds // 60
    hours = minutes // 60
    minutes %= 60
    seconds %= 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

# Text to audio and SRT functionality

async def text_to_audio_and_srt(text, voice, rate, pitch, num_lines, output_audio_path, output_srt_path):
    audio_path, warning = await text_to_speech(text, voice, rate, pitch, output_audio_path)
    if warning:
        return None, None, warning

    audio_clip = AudioFileClip(audio_path)
    audio_duration = audio_clip.duration
    
    # Generate SRT file based on the entire text
    words = text.split()
    generate_srt(words, audio_duration, output_srt_path, num_lines)

    return audio_path, output_srt_path, None
# async def text_to_audio_and_srt(text, voice, rate, pitch, num_lines):
#     audio_path, warning = await text_to_speech(text, voice, rate, pitch)
#     if warning:
#         return None, None, warning

#     audio_clip = AudioFileClip(audio_path)
#     audio_duration = audio_clip.duration
    
#     # Generate SRT file based on the entire text
#     base_name = os.path.splitext(audio_path)[0]
#     srt_path = f"{base_name}_subtitle.srt"
#     words = text.split()
#     generate_srt(words, audio_duration, srt_path, num_lines)

#     return audio_path, srt_path, None

# Gradio interface function
def tts_interface(text, voice, rate, pitch, num_lines, output_audio_path="output_audio.mp3", output_srt_path="output_subtitle.srt"):
    if not text.strip():
        return None, None, gr.Warning("Text input cannot be empty.")
    if num_lines <= 0:
        return None, None, gr.Warning("Number of SRT lines must be greater than zero.")
    
    try:
        audio_path, srt_path, warning = asyncio.run(
            text_to_audio_and_srt(text, voice, rate, pitch, num_lines, output_audio_path, output_srt_path)
        )
        return audio_path, srt_path, warning
    except Exception as e:
        return None, None, gr.Warning(f"An error occurred: {e}")

# def tts_interface(text, voice, rate, pitch, num_lines):
#     audio_path, srt_path, warning = asyncio.run(text_to_audio_and_srt(text, voice, rate, pitch, num_lines))
#     return audio_path, srt_path, warning

# Create Gradio app
async def create_demo():
    voices = await get_voices()
    
    with gr.Blocks() as demo:
        gr.Markdown(
            """
            <h1 style="text-align: center; color: #333;">Text to Speech with Subtitles</h1>
            <p style="text-align: center; color: #555;">Convert your text to natural-sounding speech and generate subtitles (SRT) for your audio.</p>
            """, 
            elem_id="header"
        )

        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(label="Input Text", lines=5, placeholder="Enter text here...")
                voice_dropdown = gr.Dropdown(choices=[""] + list(voices.keys()), label="Select Voice", value="")
                rate_slider = gr.Slider(minimum=-50, maximum=50, value=0, label="Rate Adjustment (%)", step=1)
                pitch_slider = gr.Slider(minimum=-20, maximum=20, value=0, label="Pitch Adjustment (Hz)", step=1)
                
                num_lines_slider = gr.Slider(minimum=1, maximum=5, value=2, label="Number of SRT Lines", step=1)
                
                generate_button = gr.Button("Generate Audio and Subtitles", variant="primary")

            with gr.Column():
                output_audio = gr.Audio(label="Generated Audio", type="filepath")
                output_srt = gr.File(label="Generated SRT", file_count="single")
                warning_msg = gr.Markdown(label="Warning", visible=False)

        generate_button.click(
            fn=tts_interface,
            inputs=[text_input, voice_dropdown, rate_slider, pitch_slider, num_lines_slider],
            outputs=[output_audio, output_srt, warning_msg]
        )

    return demo

# Run the app
if __name__ == "__main__":
    demo = asyncio.run(create_demo())
    demo.launch(show_error=True)

