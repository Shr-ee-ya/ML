import cohere
import streamlit as st

# Initialize Cohere API
cohere_api_key = "4aAFEygkX0gZur4BLIxUfKux6QKIno3c5EnKXRQi"  # Replace with your actual Cohere API key
co = cohere.Client(cohere_api_key)

## Function to load Cohere model and get responses
def get_cohere_response(question):
    response = co.generate(
        model='command-xlarge-nightly',  # Use an appropriate Cohere model
        prompt=question,
        max_tokens=150,  # Adjust max tokens as per your requirement
        temperature=0.5
    )
    return response.generations[0].text.strip()

# Initialize Streamlit app
st.set_page_config(page_title="Q&A Demo")

st.header("Langchain Application")

input = st.text_input("Input: ", key="input")
submit = st.button("Ask the question")

# If ask button is clicked
if submit:
    if input.strip():
        response = get_cohere_response(input)
        st.subheader("The Response is:")
        st.write(response)
    else:
        st.write("Please enter a question to get a response.")