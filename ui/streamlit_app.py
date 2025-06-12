# ui/app.py

import streamlit as st
import requests  # This is the library we use to "talk" to the API

# --- Page Configuration ---
# This should be the first Streamlit command in your app
st.set_page_config(
    page_title="Wise",
    page_icon="🧠",
    layout="wide"
)

# --- State Management ---
# Streamlit reruns your script from top to bottom every time a user interacts.
# st.session_state is a special dictionary that persists across these reruns.
# We use it to store the chat history and the current mood.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_mood" not in st.session_state:
    st.session_state.current_mood = "creative" # Set a default mood

# --- Backend API Configuration ---
# This is the address of Davin's "kitchen".
# For now, we point to the local address where he will run his Flask app.
# When we deploy, we will change this to the live Google Cloud Run URL.
BACKEND_URL = "http://127.0.0.1:5000/chat" # Port 5000 is the default for Flask

# --- UI Layout ---

st.title("🧠 Wise")
st.caption("Your mood-adaptive AI friend. Built for the ADK Hackathon.")

# Create a sidebar for mood selection for a cleaner main layout
st.sidebar.header("Select a Mood")

# A dictionary to map user-friendly labels to the mood values the API expects
mood_options = {
    "Creative 🎨": "creative",
    "Science 🔬": "science",
}

# When a button is clicked, this function will be called to update our state
def update_mood(mood_value):
    st.session_state.current_mood = mood_value

# Create a button for each mood in the sidebar
for label, value in mood_options.items():
    st.sidebar.button(label, on_click=update_mood, args=(value,), use_container_width=True)

# Display the current mode to the user
st.sidebar.info(f"Current Mode: **{st.session_state.current_mood.capitalize()}**")

# --- Chat History Display ---
# Loop through the messages stored in our session state and display them
for message in st.session_state.messages:
    # Use the 'with' syntax to create a chat message container
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Main Chat Interaction ---
# st.chat_input creates the input box at the bottom of the screen.
# The 'if prompt:' block runs only when the user presses Enter.
if prompt := st.chat_input("What do you want to explore?"):
    # 1. Add the user's message to our state and display it immediately
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Prepare for the AI's response
    with st.chat_message("assistant"):
        # Create a placeholder to show a "thinking" message while we wait
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("Wise is thinking...")

        # 3. THE API CALL
        try:
            # This is the "order" we send to the "waiter" (requests)
            # It's a Python dictionary that we will convert to JSON.
            payload = {
                "message": prompt,
                "mood": st.session_state.current_mood
            }

            # This is the line that actually sends the request to Davin's backend
            response = requests.post(BACKEND_URL, json=payload)
            response.raise_for_status()  # This will raise an error if the server returns a bad status (like 404 or 500)

            # Get the "plate" back from the "kitchen"
            ai_reply = response.json()["reply"]

            # Update the placeholder with the real response
            thinking_placeholder.markdown(ai_reply)

            # Add the AI's full response to our chat history
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

        except requests.exceptions.RequestException as e:
            # This 'except' block catches errors if we can't connect to the backend
            error_message = f"Could not connect to Wise's brain. Is the backend server running? (Error: {e})"
            thinking_placeholder.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})