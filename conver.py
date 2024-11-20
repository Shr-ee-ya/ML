import streamlit as st
from dotenv import load_dotenv
import os
import cohere

# Load environment variables
load_dotenv()
COHERE_API_KEY = "VBEt0sphxQ4QTaCwCrY5Q8TBKBcxBIoeyeT8I78F"  # Ensure the API key is loaded from the .env file

# Initialize Cohere client
if not COHERE_API_KEY:
    st.error("COHERE_API_KEY is missing or incorrect.")
else:
    co = cohere.Client(COHERE_API_KEY)

    # Streamlit UI
    st.set_page_config(page_title="Conversational Q&A Chatbot")
    st.header("Hey, Let's Chat!")

    # Initialize session state for conversation history
    if "flowmessages" not in st.session_state:
        st.session_state["flowmessages"] = [
            {"role": "system", "content": "You are a comedian AI assistant."}
        ]

    # Function to load Cohere model and get response
    def get_chatmodel_response(question):
        # Add the user's question to conversation history
        st.session_state["flowmessages"].append({"role": "user", "content": question})

        # Prepare conversation history as a prompt
        prompt = (
            "You are a comedian AI assistant. The following is a conversation:\n\n"
            + "\n".join(
                f"{msg['role'].capitalize()}: {msg['content']}" 
                for msg in st.session_state["flowmessages"]
            )
            + "\nAssistant:"
        )

        # Generate a response from Cohere
        response = co.generate(
            model="command-xlarge-nightly",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
        )

        # Extract and clean up the AI-generated response
        answer = response.generations[0].text.strip()

        # Add the AI response to conversation history
        st.session_state["flowmessages"].append({"role": "assistant", "content": answer})
        return answer

    # Input field for user query
    input = st.text_input("Input: ", key="input")
    response = None

    # Button to trigger the question
    submit = st.button("Ask the Question")

    # If the "Ask the Question" button is clicked
    if submit and input:
        response = get_chatmodel_response(input)
        st.subheader("The Response is:")
        st.write(response)

    # Display conversation history
    if st.session_state["flowmessages"]:
        st.subheader("Conversation History")
        for msg in st.session_state["flowmessages"]:
            role = "You" if msg["role"] == "user" else "AI"
            st.write(f"**{role}:** {msg['content']}")
