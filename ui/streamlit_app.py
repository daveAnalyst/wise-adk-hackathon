# ui/streamlit_app.py

import streamlit as st
import time

# --- SINGLE, UNIFIED PAGE CONFIGURATION (MUST BE THE FIRST AND ONLY STREAMLIT COMMAND) ---
st.set_page_config(page_title="Wise", page_icon="🦉", layout="wide")

# --- PERSONA CONFIGURATION ---
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
        # Using a consistent and correct file name for the logo
        st.image("wise_logo.png.jpeg", width=150) 

        if st.session_state.stage == "onboarding":
            st.title("Hello! I'm Wise.")
            st.header("What topics are you curious about?")
            if interests := st.text_input("e.g., AI, philosophy, space...", key="onboarding_input"):
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
                st.rerun()
            if btn_col2.button("Start a New Topic", use_container_width=True):
                st.session_state.stage = "set_vibe"
                st.rerun()

        elif st.session_state.stage == "set_vibe":
            st.header("Of course. What's on your mind?")
            if vibe_prompt := st.text_input("Type your first message here...", key="vibe_input"):
                detected_vibe = "analytical" if "data" in vibe_prompt.lower() else "imaginative"
                st.session_state.current_vibe = detected_vibe
                st.session_state.messages = [{"role": "user", "content": vibe_prompt}]
                st.session_state.stage = "chat"
                st.rerun()

elif st.session_state.stage == "chat":
    current_persona = PERSONA_CONFIG[st.session_state.current_vibe]

    # --- SIDEBAR ---
    with st.sidebar:
        # Using a consistent and correct file name for the logo
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
                    st.session_state.messages.append({"role": "assistant", "content": vibe_info["prompt"]})
                    st.rerun()
        
        # ADDED BACK: The On-Demand Spark button was missing
        st.divider()
        if st.button("💡 On-Demand Spark", use_container_width=True):
            spark_reply = "Here's a random on-demand spark! What if fungal networks could be used to create biodegradable circuits?"
            st.session_state.messages.append({"role": "assistant", "content": spark_reply, "avatar": "💡"})
            st.rerun()
    
    # --- HEADER & CHAT (in a centered column for aesthetics) ---
    main_col1, main_col2, main_col3 = st.columns([1, 3, 1])
    with main_col2:
        # ==========================================================
        # --- START OF THE FIX ---
        # ==========================================================
        
        # We define all columns at the top level to avoid nesting.
        header_col_title, header_col_btn1, header_col_btn2 = st.columns([4, 1, 1]) # Adjust ratios for alignment

        with header_col_title:
            st.markdown(f"### Current Vibe: <span style='color: {current_persona['color']};'>{current_persona['label']}</span>", unsafe_allow_html=True)
        
        with header_col_btn1:
            # Use icons for a cleaner look
            st.button("🧠", key="mind_map_btn", disabled=True, help="Coming Soon: Visualize your second brain!", use_container_width=True)
            
        with header_col_btn2:
            st.button("🌌", key="wise_verse_btn", disabled=True, help="Coming Soon: Enter the social dreamscape!", use_container_width=True)

        # ==========================================================
        # --- END OF THE FIX ---
        # ==========================================================

        st.divider()

        # Chat History
        for message in st.session_state.messages:
            # Added back avatar display for messages
            with st.chat_message(message["role"], avatar=PERSONA_CONFIG.get(st.session_state.current_vibe, {}).get("avatar") if message["role"] == "assistant" else "🧑‍💻"):
                 st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("Continue the conversation..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Dummy AI Response
            with st.spinner("Wise is thinking..."):
                time.sleep(1)
                ai_reply = f"Dummy response in '{st.session_state.current_vibe}' vibe to: '{prompt}'"
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            
            st.rerun()