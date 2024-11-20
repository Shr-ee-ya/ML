import streamlit as st
import cohere

# Initialize the Cohere API client with your API key
API_KEY = 'VBEt0sphxQ4QTaCwCrY5Q8TBKBcxBIoeyeT8I78F'  # Replace with your actual Cohere API key
co = cohere.Client(API_KEY)

def summarize_text(input_text):
    """
    Summarize the given text using the Cohere API.
    """
    try:
        response = co.generate(
            model='command-xlarge-nightly',  # Use an appropriate model
            prompt=f"Summarize the following text:\n\n{input_text}\n\nSummary:",
            max_tokens=100,  # Adjust based on the desired summary length
            temperature=0.5,  # Lower temperature for more focused responses
        )
        return response.generations[0].text.strip()
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.set_page_config(page_title="Text Summarization", page_icon="✂")

st.title("Text Summarization with Cohere")
st.write("Enter a block of text below, and get a concise summary!")

input_text = st.text_area("Input Text", height=200)

if st.button("Summarize"):
    if input_text.strip():
        with st.spinner("Generating summary..."):
            summary = summarize_text(input_text)
            st.subheader("Summary:")
            st.write(summary)
    else:
        st.error("Please enter some text to summarize.")