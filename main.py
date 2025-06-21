# ==============================================================================
# --- THE DEFINITIVE, READY-TO-SHIP main.py (v1.3) ---
# ==============================================================================
import streamlit as st
import time
import plotly.io as pio
from dotenv import load_dotenv
import os
import google.generativeai as genai

# --- AGENT IMPORTS (RENAMED) ---
from agents.VibeDetectionAgent import detect_vibe
from agents.DaydreamAgent import get_daydream_spark
from agents.ConversationalAgent import ConversationalAgent

# --- CENTRALIZED API KEY CONFIGURATION ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("FATAL ERROR: GOOGLE_API_KEY not found in .env file!")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)

# --- HELPER FUNCTION FOR SMART, ON-DEMAND SPARKS ---
def get_contextual_spark(vibe: str, history: list):
    print(f"✨ Generating a new contextual spark with vibe: {vibe}...")
    conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-4:]])
    if vibe == "scientific":
        vibe_instruction = "Your response must be analytical, data-focused, or scientific. Ask a clarifying question or propose a logical next step."
    else: # 'creative'
        vibe_instruction = "Your response must be imaginative, metaphorical, or creative. Ask a 'what if' question or propose a lateral thinking idea."
    
    prompt = f"""You are an AI assistant. A user is in the middle of a conversation. Your task is to generate a single, thought-provoking question or 'what if' statement that is relevant to the ongoing conversation, in a specific tone.
    CURRENT CONVERSATION CONTEXT:\n---\n{conversation_context}\n---\n
    INSTRUCTIONS:\n- {vibe_instruction}\n- Your response must be related to the conversation context.\n- Do NOT act like you are interrupting. Just provide the question/statement directly.\n- Be concise.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text.strip()

# --- PAGE CONFIG & PERSONA SETUP ---
st.set_page_config(page_title="Wise", page_icon="🦉", layout="wide")
PERSONA_CONFIG = {
    "scientific": {"label": "Analytical 🔬", "color": "#2196F3", "avatar": "🔬", "prompt": "Analytical Vibe engaged. Ready for facts and analysis."},
    "creative": {"label": "Imaginative 🎨", "color": "#FFC107", "avatar": "🎨", "prompt": "Imaginative Vibe engaged. Ready to brainstorm and explore ideas!"}
}

# --- STATE INITIALIZATION ---
if "stage" not in st.session_state:
    st.session_state.stage = "onboarding"
    st.session_state.messages = []
    st.session_state.current_vibe = "scientific"
    st.session_state.user_profile = {"name": "Dave", "status": "new_user"}
    st.session_state.dream_inbox = []
    st.session_state.conversational_agent = ConversationalAgent(data_path="data/wmt_stock_data.csv")

# --- CUSTOM CSS FOR POLISHED LOOK ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        .stApp { background-color: #0E1117; }
        
        /* Default for all chat bubbles (user's bubbles) */
        div[data-testid="stChatMessage"] { 
            background-color: #262730; 
            border-radius: 12px; 
            border: 1px solid #303138; 
        }

        /* --- FINAL FIX: Overrides for the AI's bubbles --- */
        div[data-testid="stChatMessage"]:has(span[title="assistant"]) {
            background-color: #1C2333; /* A distinct, dark blue-grey background */
        }
        div[data-testid="stChatMessage"]:has(span[title="assistant"]) p { 
            color: #FFFFFF; /* Pure white text for maximum contrast */
        }
        
        /* General UI Polish */
        div[data-testid="stButton"] > button { border-radius: 8px; border: 1px solid #4A4A5A; }
        div[data-testid="stButton"] > button:hover { border: 1px solid #FFC107; color: #FFC107; background-color: #262730; }
        .stTextInput input { border-radius: 8px; }
        .st-emotion-cache-1629p8f, .st-emotion-cache-p5msec { border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

def centered_container():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2: return st.container()

# ==============================================================================
# --- STAGE ROUTER ---
# ==============================================================================

if st.session_state.stage in ["onboarding", "welcome", "set_vibe"]:
    with centered_container():
        st.image("wise_logo.png.jpeg", width=150)

        if st.session_state.stage == "onboarding":
            st.title("Hello! I'm Wise.")
            st.header("Your Curious AI Partner.")
            if st.button("Let's Begin", use_container_width=True):
                st.session_state.stage = "welcome"
                st.rerun()

        elif st.session_state.stage == "welcome":
            st.header(f"Welcome back, {st.session_state.user_profile['name']}.")
            if 'current_spark' not in st.session_state:
                with st.spinner("Finding a new spark of inspiration..."):
                    spark_idea = get_daydream_spark(data_path="data/wmt_stock_data.csv")
                    st.session_state.current_spark = spark_idea
                    if spark_idea not in st.session_state.dream_inbox:
                        st.session_state.dream_inbox.append(spark_idea)
            st.info(f"💡 {st.session_state.current_spark}")
            
            btn_col1, btn_col2 = st.columns(2)
            if btn_col1.button("Explore this Idea", use_container_width=True):
                st.session_state.current_vibe = "creative"
                st.session_state.messages = [{"role": "user", "content": f"Let's explore this idea: {st.session_state.current_spark}"}]
                st.session_state.stage = "chat"
                st.rerun()
            if btn_col2.button("Start a New Topic", use_container_width=True):
                st.session_state.stage = "set_vibe"
                st.rerun()

        elif st.session_state.stage == "set_vibe":
            st.header("Of course. What's on your mind?")
            if vibe_prompt := st.text_input("Type your first message here...", key="vibe_input"):
                with st.spinner("Tuning into the vibe..."):
                    detected_vibe = detect_vibe(vibe_prompt)
                    if detected_vibe == 'none': detected_vibe = 'scientific'
                    st.session_state.current_vibe = detected_vibe
                    st.session_state.messages = [{"role": "user", "content": vibe_prompt}]
                    st.session_state.stage = "chat"
                    st.rerun()

elif st.session_state.stage == "chat":
    current_persona = PERSONA_CONFIG[st.session_state.current_vibe]
    with st.sidebar:
        st.image("wise_logo.png.jpeg", width=80)
        if st.button("➕ New Conversation", use_container_width=True):
            if 'current_spark' in st.session_state: del st.session_state.current_spark
            st.session_state.stage = "welcome"; st.session_state.messages = []; st.rerun()
        st.header("Cognitive Lens")
        for vibe_key, vibe_info in PERSONA_CONFIG.items():
            if st.button(vibe_info["label"], key=vibe_key, use_container_width=True):
                if st.session_state.current_vibe != vibe_key:
                    st.session_state.current_vibe = vibe_key
                    st.session_state.messages.append({"role": "assistant", "content": vibe_info["prompt"], "avatar": vibe_info["avatar"]})
                    st.rerun()
        st.divider()
        st.header("On-Demand Spark")
        if st.button("💡 Generate a new idea", use_container_width=True):
            with st.spinner("Finding a relevant spark..."):
                spark_reply = get_contextual_spark(vibe=st.session_state.current_vibe, history=st.session_state.messages)
                st.session_state.messages.append({"role": "assistant", "content": spark_reply, "avatar": "💡"})
                if spark_reply not in st.session_state.dream_inbox:
                    st.session_state.dream_inbox.append(spark_reply)
                st.rerun()
        st.divider()
        st.header("Dream Inbox")
        if not st.session_state.dream_inbox:
            st.caption("Your generated sparks will appear here.")
        else:
            for spark in reversed(st.session_state.dream_inbox):
                st.info(spark, icon="💡")

    main_col1, main_col2, main_col3 = st.columns([1, 4, 1])
    with main_col2:
        st.markdown(f"### Current Vibe: <span style='color: {current_persona['color']};'>{current_persona['label']}</span>", unsafe_allow_html=True)
        st.divider()
        
        for message in st.session_state.messages:
            avatar = current_persona.get('avatar') if message["role"] == "assistant" else "🧑‍💻"
            if "avatar" in message: avatar = message["avatar"]
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        if prompt := st.chat_input("Continue the conversation..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_message = st.session_state.messages[-1]["content"]
        
        detected_vibe_in_chat = detect_vibe(last_message)
        if detected_vibe_in_chat != 'none' and detected_vibe_in_chat != st.session_state.current_vibe:
            other_vibe_label = PERSONA_CONFIG[detected_vibe_in_chat]['label']
            st.toast(f"Your message seems {detected_vibe_in_chat}. Consider switching to the {other_vibe_label} lens!", icon="🤔")

        with main_col2.chat_message("assistant", avatar=current_persona["avatar"]):
            with st.spinner("Wise is thinking..."):
                agent = st.session_state.conversational_agent
                agent.lens = st.session_state.current_vibe
                response = agent.chat(last_message)
                
                if response["type"] == "plotly":
                    fig = pio.from_json(response["content"])
                    st.plotly_chart(fig, use_container_width=True)
                    ai_content_for_history = "As requested, here is the chart:"
                else:
                    st.markdown(response["content"])
                    ai_content_for_history = response["content"]
                
                st.session_state.messages.append({"role": "assistant", "content": ai_content_for_history, "avatar": current_persona["avatar"]})
        st.rerun()