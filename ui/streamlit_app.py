# ui/streamlit_app.py

import streamlit as st
import time

# --- SINGLE, UNIFIED PAGE CONFIGURATION ---
st.set_page_config(page_title="Wise", page_icon="🦉", layout="wide")

# --- PERSONA CONFIGURATION ---
# I've added the 'avatar' key back in, as the toast notifications can use it.
PERSONA_CONFIG = {
    "analytical": {"label": "Analytical 🔬", "color": "#2196F3", "avatar": "🔬", "prompt": "Analytical Vibe engaged. Ready for facts."},
    "imaginative": {"label": "Imaginative 🎨", "color": "#FFC107", "avatar": "🎨", "prompt": "Imaginative Vibe engaged. Ready to brainstorm!"}
}

# --- STATE INITIALIZATION ---
if "stage" not in st.session_state:
    st.session_state.stage = "onboarding"
    st.session_state.messages = []
    st.session_state.current_vibe = "analytical"
    st.session_state.user_profile = {"name": "Dave", "status": "new_user"}

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        /* Your existing CSS is perfect */
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
        st.image("wise_logo.png.jpeg", width=150) 

        if st.session_state.stage == "onboarding":
            st.title("Hello! I'm Wise.")
            st.header("What topics are you curious about?")
            if interests := st.text_input("e.g., AI, philosophy, space...", key="onboarding_input"):
                with st.spinner("Calibrating my curiosity engine..."): ### <-- UPDATED
                    time.sleep(1.5)
                    st.session_state.user_profile["status"] = "existing_user"
                    st.session_state.stage = "welcome"
                    st.rerun()

        elif st.session_state.stage == "welcome":
            st.header(f"Welcome back, {st.session_state.user_profile['name']}.")
            st.info("💡 **A thought I had:** What if music theory could help us understand dark matter?")
            btn_col1, btn_col2 = st.columns(2)
            if btn_col1.button("Explore this Idea", use_container_width=True):
                st.session_state.current_vibe = "imaginative"
                st.session_state.messages = [{"role": "user", "content": "Let's explore that idea about music and dark matter."}]
                st.session_state.stage = "chat"
                st.toast("Switched to Imaginative Vibe!", icon="🎨") ### <-- NEW
                st.rerun()
            if btn_col2.button("Start a New Topic", use_container_width=True):
                st.session_state.stage = "set_vibe"
                st.rerun()

        elif st.session_state.stage == "set_vibe":
            st.header("Of course. What's on your mind?")
            if vibe_prompt := st.text_input("Type your first message here...", key="vibe_input"):
                with st.spinner("Tuning into the vibe..."): ### <-- UPDATED
                    time.sleep(1)
                    detected_vibe = "analytical" if "data" in vibe_prompt.lower() else "imaginative"
                    st.session_state.current_vibe = detected_vibe
                    st.session_state.messages = [{"role": "user", "content": vibe_prompt}]
                    st.session_state.stage = "chat"
                    st.toast(f"Switched to {detected_vibe.capitalize()} Vibe!", icon=PERSONA_CONFIG[detected_vibe]['avatar']) ### <-- NEW
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
                    st.session_state.messages.append({"role": "assistant", "content": vibe_info["prompt"], "avatar": vibe_info["avatar"]}) ### <-- UPDATED to add avatar
                    st.toast(f"Switched to {vibe_info['label']} Vibe!", icon=vibe_info['avatar']) ### <-- NEW
                    st.rerun()
        
        st.divider()
        if st.button("💡 On-Demand Spark", use_container_width=True):
            with st.spinner("Finding a spark..."): ### <-- UPDATED
                time.sleep(1)
                spark_reply = "Here's a random on-demand spark! What if fungal networks could be used to create biodegradable circuits?"
                st.session_state.messages.append({"role": "assistant", "content": spark_reply, "avatar": "💡"})
                st.rerun()
    
    # --- HEADER & CHAT ---
    main_col1, main_col2, main_col3 = st.columns([1, 3, 1])
    with main_col2:
        header_col_title, header_col_btn1, header_col_btn2 = st.columns([4, 1, 1])
        with header_col_title:
            st.markdown(f"### Current Vibe: <span style='color: {current_persona['color']};'>{current_persona['label']}</span>", unsafe_allow_html=True)
        with header_col_btn1:
            st.button("🧠", key="mind_map_btn", disabled=True, help="Coming Soon: Visualize your second brain!", use_container_width=True)
        with header_col_btn2:
            st.button("🌌", key="wise_verse_btn", disabled=True, help="Coming Soon: Enter the social dreamscape!", use_container_width=True)
        st.divider()

        # Chat History
        for message in st.session_state.messages:
            # We need to define the user avatar here
            avatar = current_persona.get('avatar') if message["role"] == "assistant" else "🧑‍💻"
            if "avatar" in message: # Override if the message has a specific avatar (like the spark)
                avatar = message["avatar"]
            with st.chat_message(message["role"], avatar=avatar):
                 st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("Continue the conversation..."):
            st.session_state.messages.append({"role": "user", "content": prompt, "avatar": "🧑‍💻"})
            
            # Dummy AI Response
            with st.spinner(f"Wise is thinking in an '{st.session_state.current_vibe}' vibe..."): ### <-- UPDATED
                time.sleep(1.5)
                ai_reply = f"Dummy response in '{st.session_state.current_vibe}' vibe to: '{prompt}'"
                st.session_state.messages.append({"role": "assistant", "content": ai_reply, "avatar": current_persona["avatar"]})
            
            st.rerun()