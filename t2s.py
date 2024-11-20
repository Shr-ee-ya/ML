import streamlit as st
import cohere

# Initialize Cohere API
API_KEY = "3qeisnbsUVIPBtO06V6Tk5szXvIZphbgWAcKckQ1"  # Replace with your Cohere API key
co = cohere.Client(API_KEY)

# Function to generate a story
def generate_story(prompt, max_tokens=300, temperature=0.7):
    """
    Generate a story continuation based on the given prompt.

    Args:
        prompt (str): The starting text or idea for the story.
        max_tokens (int): The maximum number of tokens to generate.
        temperature (float): Controls randomness. Higher values = more randomness.

    Returns:
        str: The generated story or an error message.
    """
    try:
        # Adjusted model ID
        response = co.generate(
            model='command-xlarge',  # Use a valid model ID
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            k=0,
            p=0.75,
            stop_sequences=[],
            return_likelihoods='NONE'
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return f"Error: {e}"

# Streamlit app UI
st.title("Text-to-Story Generator")
st.write("Generate creative stories based on your ideas using Cohere's powerful language models!")

# User input
prompt = st.text_area("Enter your story idea or prompt:", placeholder="Once upon a time in a mystical forest...")
max_tokens = st.slider("Story Length (max tokens):", min_value=50, max_value=500, value=300, step=50)
temperature = st.slider("Creativity Level (temperature):", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

# Generate button
if st.button("Generate Story"):
    if prompt.strip() == "":
        st.warning("Please enter a story prompt to continue!")
    else:
        st.write("Generating your story...")
        story = generate_story(prompt, max_tokens=max_tokens, temperature=temperature)
        st.subheader("Your Generated Story:")
        st.write(story)