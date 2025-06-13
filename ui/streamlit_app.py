# ui/app.py

import streamlit as st
import requests
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="Wise",
    page_icon="🧠",
    layout="wide"
)

# --- State Management ---
if "messages" not in st.session_state:
    # We'll store a bit more info now: the role, content, and avatar
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm Wise. What's on your mind today?", "avatar": "🧠"}
    ]
if "current_mood" not in st.session_state:
    st.session_state.current_mood = "creative"

# --- Backend API Configuration ---
# Let's define both endpoints now
API_BASE_URL = "http://127.0.0.1:5000"
CHAT_URL = f"{API_BASE_URL}/chat"
SPARK_URL = f"{API_BASE_URL}/spark" # The new endpoint for the Curiosity Spark

# --- UI Components ---

# A dictionary to hold info about each mood
MOOD_CONFIG = {
    "creative": {"label": "Creative 🎨", "color": "#FFC107"}, # Amber
    "science": {"label": "Science 🔬", "color": "#2196F3"},   # Blue
}

current_mood_info = MOOD_CONFIG[st.session_state.current_mood]

# --- DYNAMIC HEADER ---
# Use columns to create a nice header layout
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://em-content.zobj.net/source/apple/391/brain_1f9e0.png", width=100) # Simple brain emoji image
with col2:
    st.title("Wise")
    # The header color changes with the mood!
    st.markdown(f"<h3 style='color: {current_mood_info['color']};'>Current Mode: {current_mood_info['label']}</h3>", unsafe_allow_html=True)


# --- SIDEBAR ---
st.sidebar.header("Select a Mood")
def update_mood(mood_value):
    st.session_state.current_mood = mood_value
    # Add a message to show the mode has changed
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"I'm now in {mood_value.capitalize()} mode. Let's explore!",
        "avatar": "🧠"
    })
    # Rerun the app to reflect the change immediately
    st.rerun()

for value, info in MOOD_CONFIG.items():
    st.sidebar.button(info["label"], on_click=update_mood, args=(value,), use_container_width=True)


# --- CURIOSITY SPARK BUTTON ---
st.sidebar.divider()
if st.sidebar.button("💡 Curiosity Spark", use_container_width=True):
    with st.chat_message("assistant", avatar="💡"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("Searching for a spark...")
        try:
            # Call the new /spark endpoint. It doesn't need a message or mood.
            response = requests.post(SPARK_URL)
            response.raise_for_status()
            spark_reply = response.json()["reply"]
            thinking_placeholder.markdown(spark_reply)
            st.session_state.messages.append({"role": "assistant", "content": spark_reply, "avatar": "💡"})
        except requests.exceptions.RequestException as e:
            error_message = f"Couldn't find a spark right now. Is the backend running? (Error: {e})"
            thinking_placeholder.error(error_message)


# --- Chat History Display ---
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get("avatar")):
        st.markdown(message["content"])

# --- Main Chat Interaction ---
if prompt := st.chat_input("What do you want to explore?"):
    # Add and display user message
    st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "🧑‍💻"})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # Prepare and call the API for the AI's response
    with st.chat_message("assistant", avatar="🧠"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("Wise is thinking...")
        try:
            payload = {"message": prompt, "mood": st.session_state.current_mood}
            response = requests.post(CHAT_URL, json=payload)
            response.raise_for_status()
            ai_reply = response.json()["reply"]

            # This part is for handling potential Plotly graphs from the Science agent
            if st.session_state.current_mood == 'science' and isinstance(ai_reply, dict) and 'graph' in ai_reply:
                thinking_placeholder.markdown(ai_reply['text'])
                st.plotly_chart(ai_reply['graph'], use_container_width=True)
                # Store both text and graph info
                st.session_state.messages.append({"role": "assistant", "content": ai_reply, "avatar": "🧠"})
            else:
                thinking_placeholder.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply, "avatar": "🧠"})

        except requests.exceptions.RequestException as e:
            error_message = f"Could not connect to Wise's brain. (Error: {e})"
            thinking_placeholder.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message, "avatar": "🧠"})