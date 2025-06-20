# ==============================================================================
# --- New main.py (Copy and Paste This Entire Block) ---
# ==============================================================================

#import streamlit as st
#import time
#import plotly.io as pio
#from dotenv import load_dotenv

# --- NEW: REAL AGENT IMPORTS ---
#from agents.VibeDetector import detect_vibe
#from agents.SparkGenerator import get_spark
#from agents.WiseBot import WiseBot

# In main.py
import streamlit as st
import time
import plotly.io as pio
from dotenv import load_dotenv
import os # <-- Add os import
import google.generativeai as genai # <-- Add genai import

# --- NEW: REAL AGENT IMPORTS ---
from agents.VibeDetector import detect_vibe
from agents.SparkGenerator import get_spark
from agents.WiseBot import WiseBot

# --- CENTRALIZED API KEY CONFIGURATION ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("FATAL ERROR: GOOGLE_API_KEY not found in .env file!")
    st.stop() # This will halt the app if the key is missing

genai.configure(api_key=GOOGLE_API_KEY)
print("✅ Gemini AI Model Initialized Successfully from main.py.")
# ----------------------------------------

# --- NEW: LOAD API KEYS ---
# Make sure you have a .env file in this directory with your GOOGLE_API_KEY
#load_dotenv()

# --- SINGLE, UNIFIED PAGE CONFIGURATION ---
st.set_page_config(page_title="Wise", page_icon="🦉", layout="wide")

# --- PERSONA CONFIGURATION ---
PERSONA_CONFIG = {
    "scientific": {"label": "Analytical 🔬", "color": "#2196F3", "avatar": "🔬", "prompt": "Analytical Vibe engaged. Ready for facts and analysis."},
    "creative": {"label": "Imaginative 🎨", "color": "#FFC107", "avatar": "🎨", "prompt": "Imaginative Vibe engaged. Ready to brainstorm and explore ideas!"}
}

# --- STATE INITIALIZATION ---
if "stage" not in st.session_state:
    st.session_state.stage = "onboarding"
    st.session_state.messages = []
    st.session_state.current_vibe = "scientific" # Default to scientific
    st.session_state.user_profile = {"name": "Dave", "status": "new_user"}

# --- NEW: REAL AGENT INITIALIZATION ---
if "wise_bot" not in st.session_state:
    # IMPORTANT: Verify this path is correct from your root directory
    st.session_state.wise_bot = WiseBot(data_path="data/wmt_stock_data.csv")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@300;400;500;600&display=swap');
        html, body, [class*="css"]  { font-family: 'Lexend', sans-serif; }
        div[data-testid="stChatMessage"] { background-color: #262730; border-radius: 20px; padding: 16px; border: 1px solid #404040; }
        div[data-testid="stButton"] > button { border-radius: 20px; border: 1px solid #FFC107; background-color: transparent; padding: 10px 20px; transition: background-color 0.3s, color 0.3s; }
        div[data-testid="stButton"] > button:hover { background-color: #FFC107; color: black; }
        div[data-testid="stButton"] > button:disabled { border: 1px solid #4a4a4a; background-color: #222222; color: #4a4a4a; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCTION TO CREATE A CENTERED LAYOUT ---
def centered_container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        return st.container()

# ==============================================================================
# --- STAGE ROUTER: The App's Main Brain ---
# ==============================================================================

if st.session_state.stage in ["onboarding", "welcome", "set_vibe"]:
    with centered_container():
        # Ensure your logo file is named 'wise_logo.png.jpeg' and is in the root folder
        st.image("wise_logo.png.jpeg", width=150)

        if st.session_state.stage == "onboarding":
            st.title("Hello! I'm Wise.")
            st.header("What topics are you curious about?")
            if interests := st.text_input("e.g., AI, philosophy, space...", key="onboarding_input"):
                with st.spinner("Calibrating my curiosity engine..."):
                    time.sleep(1.5)
                    st.session_state.user_profile["status"] = "existing_user"
                    st.session_state.stage = "welcome"
                    st.rerun()

        elif st.session_state.stage == "welcome":
            st.header(f"Welcome back, {st.session_state.user_profile['name']}.")
            # --- REPLACED LOGIC: REAL SPARK GENERATION ---
            with st.spinner("Finding a new spark of inspiration..."):
                spark_idea = get_spark(data_path="data/wmt_stock_data.csv")
            st.info(f"💡 **A thought I had:** {spark_idea}")
            btn_col1, btn_col2 = st.columns(2)
            if btn_col1.button("Explore this Idea", use_container_width=True):
                st.session_state.current_vibe = "creative"
                st.session_state.messages = [{"role": "user", "content": "Let's explore that idea you had."}]
                st.session_state.stage = "chat"
                st.toast("Switched to Creative Vibe!", icon="🎨")
                st.rerun()
            if btn_col2.button("Start a New Topic", use_container_width=True):
                st.session_state.stage = "set_vibe"
                st.rerun()

        elif st.session_state.stage == "set_vibe":
            st.header("Of course. What's on your mind?")
            if vibe_prompt := st.text_input("Type your first message here...", key="vibe_input"):
                with st.spinner("Tuning into the vibe..."):
                    # --- REPLACED LOGIC: REAL VIBE DETECTION ---
                    detected_vibe = detect_vibe(vibe_prompt)
                    if detected_vibe == 'none': # Handle simple greetings
                        detected_vibe = 'scientific' # Default to a safe vibe
                    st.session_state.current_vibe = detected_vibe
                    st.session_state.messages = [{"role": "user", "content": vibe_prompt}]
                    st.session_state.stage = "chat"
                    st.toast(f"Switched to {detected_vibe.capitalize()} Vibe!", icon=PERSONA_CONFIG[detected_vibe]['avatar'])
                    st.rerun()

elif st.session_state.stage == "chat":
    current_persona = PERSONA_CONFIG[st.session_state.current_vibe]

    # --- SIDEBAR ---
    with st.sidebar:
        st.image("wise_logo.png.jpeg", width=80)
        if st.button("➕ New Conversation", use_container_width=True):
            st.session_state.stage = "welcome"
            st.session_state.messages = []
            st.rerun()
        st.header("Change Vibe")
        for vibe_key, vibe_info in PERSONA_CONFIG.items():
            if st.button(vibe_info["label"], key=vibe_key, use_container_width=True):
                if st.session_state.current_vibe != vibe_key:
                    st.session_state.current_vibe = vibe_key
                    st.session_state.messages.append({"role": "assistant", "content": vibe_info["prompt"], "avatar": vibe_info["avatar"]})
                    st.toast(f"Switched to {vibe_info['label']} Vibe!", icon=vibe_info['avatar'])
                    st.rerun()

    # --- HEADER & CHAT ---
    main_col1, main_col2, main_col3 = st.columns([1, 3, 1])
    with main_col2:
        st.markdown(f"### Current Vibe: <span style='color: {current_persona['color']};'>{current_persona['label']}</span>", unsafe_allow_html=True)
        st.divider()

        # Display chat history
        for message in st.session_state.messages:
            avatar = current_persona.get('avatar') if message["role"] == "assistant" else "🧑‍💻"
            if "avatar" in message:
                avatar = message["avatar"]
            with st.chat_message(message["role"], avatar=avatar):
                # This is a bit of a hack to re-render plotly charts from history
                if "{" in message["content"] and '"type": "plotly"' in message["content"]:
                     try:
                        chart_data = json.loads(message["content"])
                        fig = pio.from_json(chart_data["content"])
                        st.plotly_chart(fig, use_container_width=True)
                     except:
                        st.markdown("Could not render chart from history.")
                else:
                    st.markdown(message["content"])

        # --- REPLACED LOGIC: REAL CHAT INPUT AND RESPONSE ---
        if prompt := st.chat_input("Continue the conversation..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        user_message = st.session_state.messages[-1]["content"]
        with main_col2:
            with st.chat_message("assistant", avatar=current_persona["avatar"]):
                with st.spinner(f"Wise is thinking with a '{st.session_state.current_vibe}' lense..."):
                    st.session_state.wise_bot.lens = st.session_state.current_vibe
                    response = st.session_state.wise_bot.chat(user_message)
                    
                    ai_content_for_history = ""
                    if response["type"] == "plotly":
                        fig = pio.from_json(response["content"])
                        st.plotly_chart(fig, use_container_width=True)
                        # We store the JSON in history to attempt re-rendering
                        ai_content_for_history = f'{{"type": "plotly", "content": {response["content"]}}}'
                    elif response["type"] == "error":
                        st.error(response["content"])
                        ai_content_for_history = response["content"]
                    else: # 'text'
                        st.markdown(response["content"])
                        ai_content_for_history = response["content"]
                    
                    st.session_state.messages.append({"role": "assistant", "content": ai_content_for_history, "avatar": current_persona["avatar"]})
            st.rerun()