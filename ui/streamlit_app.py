# ui/streamlit_app.py

import streamlit as st
import requests
import json # To handle plotly graphs

# --- Page Configuration ---
st.set_page_config(
    page_title="Wise",
    page_icon="🧠",
    layout="centered" # Let's start with a centered layout for the welcome screen
)

# --- Backend API Configuration ---
API_BASE_URL = "http://127.0.0.1:5000"
WELCOME_URL = f"{API_BASE_URL}/welcome_back"
SET_MOOD_URL = f"{API_BASE_URL}/set_mood_from_text"
CHAT_URL = f"{API_BASE_URL}/chat"
SPARK_URL = f"{API_BASE_URL}/spark"

# --- Persona Configuration (The Dynamic Personalities) ---
PERSONA_CONFIG = {
    "science": {
        "label": "Science 🔬",
        "color": "#2196F3",
        "avatar": "🔬",
        "welcome_message": "Science mode activated. I'm ready for deep analysis. What's our research topic?"
    },
    "creative": {
        "label": "Creative 🎨",
        "color": "#FFC107",
        "avatar": "🎨",
        "welcome_message": "Creative mode engaged! Let's brainstorm something amazing. What's our starting point?"
    },
    "general": {
        "label": "General 🤔",
        "color": "#9E9E9E",
        "avatar": "🤔",
        "welcome_message": "I'm here to help with anything. What's on your mind?"
    }
}

# --- State Management (The App's "Memory") ---
if "stage" not in st.session_state:
    st.session_state.stage = "welcome"
    st.session_state.messages = []
    st.session_state.current_mood = "general" # Start with a neutral mood
    st.session_state.welcome_data = None


# ==============================================================================
# --- STAGE 1: THE INTELLIGENT WELCOME SCREEN ---
# ==============================================================================
if st.session_state.stage == "welcome":
    st.image("https://em-content.zobj.net/source/apple/391/brain_1f9e0.png", width=120)
    st.title("Welcome to Wise")

    # Fetch the welcome data from the backend once
    if st.session_state.welcome_data is None:
        try:
            with st.spinner("Waking up..."):
                response = requests.post(WELCOME_URL)
                response.raise_for_status()
                st.session_state.welcome_data = response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to Wise's brain. Please ensure the backend is running. Error: {e}")
            st.stop() # Stop the app if we can't get the welcome message

    # Display the welcome messages
    st.markdown(f"### {st.session_state.welcome_data['greeting']}")
    st.info(f"💡 **A thought I had while you were away:** {st.session_state.welcome_data['spark_idea']}")

    # Get the user's mood
    mood_prompt = st.text_input("You can explore that idea, or we can talk about something else. What's on your mind right now?")

    if mood_prompt:
        with st.spinner("Understanding your mood..."):
            try:
                payload = {"message": mood_prompt}
                response = requests.post(SET_MOOD_URL, json=payload)
                response.raise_for_status()
                detected_mood = response.json()["detected_mood"]

                # Update state and transition to the chat stage
                st.session_state.current_mood = detected_mood
                st.session_state.stage = "chat"
                
                # Add the initial user message and the mode-setting confirmation to the chat
                st.session_state.messages.append({"role": "user", "content": mood_prompt, "avatar": "🧑‍💻"})
                persona_info = PERSONA_CONFIG[detected_mood]
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": persona_info["welcome_message"],
                    "avatar": persona_info["avatar"]
                })
                
                # Rerun the script to enter the chat stage
                st.rerun()

            except requests.exceptions.RequestException as e:
                st.error(f"Could not set mood. Please check the backend connection. Error: {e}")

# ==============================================================================
# --- STAGE 2: THE MAIN CHAT INTERFACE ---
# ==============================================================================
elif st.session_state.stage == "chat":
    # Set the layout to wide for the chat interface
    st.set_page_config(page_title="Wise", page_icon="🧠", layout="wide")

    current_persona = PERSONA_CONFIG[st.session_state.current_mood]

    # --- DYNAMIC HEADER ---
    st.markdown(f"### Current Mode: <span style='color: {current_persona['color']};'>{current_persona['label']}</span>", unsafe_allow_html=True)
    st.divider()

    # --- SIDEBAR FOR MANUAL OVERRIDE ---
    st.sidebar.header("Override Mood")
    def update_mood(mood_value):
        if st.session_state.current_mood != mood_value:
            st.session_state.current_mood = mood_value
            persona_info = PERSONA_CONFIG[mood_value]
            st.session_state.messages.append({
                "role": "assistant",
                "content": persona_info["welcome_message"],
                "avatar": persona_info["avatar"]
            })
            st.rerun()

    for value, info in PERSONA_CONFIG.items():
        st.sidebar.button(info["label"], on_click=update_mood, args=(value,), use_container_width=True)

    # --- CURIOSITY SPARK BUTTON ---
    st.sidebar.divider()
    if st.sidebar.button("💡 Curiosity Spark", use_container_width=True):
        with st.chat_message("assistant", avatar="💡"):
            with st.spinner("Searching for a spark..."):
                try:
                    response = requests.post(SPARK_URL)
                    response.raise_for_status()
                    spark_reply = response.json()["reply"]
                    st.markdown(spark_reply)
                    st.session_state.messages.append({"role": "assistant", "content": spark_reply, "avatar": "💡"})
                except requests.exceptions.RequestException as e:
                    st.error(f"Couldn't find a spark right now. Is the backend running? (Error: {e})")
    
    # --- Chat History Display ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=message.get("avatar")):
            # Check if the content is a dictionary (our special graph format)
            if isinstance(message["content"], dict) and 'graph' in message["content"]:
                st.markdown(message["content"]["text"])
                # The graph data from the backend should be JSON, so we load it back
                fig_json = json.loads(message["content"]["graph"])
                st.plotly_chart(fig_json, use_container_width=True)
            else:
                st.markdown(message["content"])

    # --- Main Chat Input ---
    if prompt := st.chat_input("What do you want to explore?"):
        st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "🧑‍💻"})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=current_persona["avatar"]):
            with st.spinner("Wise is thinking..."):
                try:
                    payload = {"message": prompt, "mood": st.session_state.current_mood}
                    response = requests.post(CHAT_URL, json=payload)
                    response.raise_for_status()
                    ai_reply = response.json()["reply"]
                    
                    # Add response to state and display it
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply, "avatar": current_persona["avatar"]})
                    
                    # We need to rerun to make the message show up and then handle the graph if it exists
                    st.rerun()

                except requests.exceptions.RequestException as e:
                    error_message = f"Could not connect to Wise's brain. (Error: {e})"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message, "avatar": "🧠"})