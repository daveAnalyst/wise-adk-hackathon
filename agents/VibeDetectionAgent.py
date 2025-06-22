# agents/VibeDetectionAgent.py (UPGRADED AND FINAL VERSION)

import google.generativeai as genai
from google.generativeai import types

# --- Configuration block REMOVED ---
# This is now handled centrally in main.py to avoid conflicts.

def detect_vibe(user_message: str) -> str:
    """
    Analyzes a user's message and classifies its INTENT as 'scientific' or 'creative'.
    """
    if not user_message:
        return "none"

    print(f"🧠 VibeDetector: Analyzing message -> '{user_message[:50]}...'")

    # --- UPDATED, MORE NUANCED PROMPT ---
    prompt = f"""You are a Vibe Detection AI. Your task is to classify the user's INTENT based on their message. The output must be one of three words: 'scientific', 'creative', or 'none'.

Classification Instructions:
1.  **'scientific'**: The user is asking for facts, explanations, data, analysis, or logical reasoning. They want to understand something concretely.
    Examples: "Explain market capitalization.", "How does photosynthesis work?", "What are the stats for this player?"

2.  **'creative'**: The user is asking to generate something artistic, to brainstorm, to imagine, or to explore a concept metaphorically. Look for verbs like 'write', 'create', 'imagine', 'what if'.
    Examples: "What if stars were memories?", "Write a poem about the ocean.", "Let's brainstorm ideas for a new company."

3.  **'none'**: The message is a simple greeting, a short, contextless follow-up, or a statement without a clear analytical or creative intent.
    Examples: "Hello there", "do that", "tell me more", "LeBron James"

Return ONLY ONE word: 'scientific', 'creative', or 'none'.
---
User Message: "{user_message}"
Classification:"""
    
    try:
        # Note: The 'genai' library is configured in main.py, so this call will work.
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config=types.GenerationConfig(temperature=0.0, max_output_tokens=10)
        )
        vibe = response.text.strip().lower()
        print(f"✅ VibeDetector: Detected vibe -> {vibe}")

        if vibe in ['scientific', 'creative', 'none']:
            return vibe
        else:
            # Safer to default to 'none' to avoid unwanted mode switches
            print(f"⚠️ VibeDetector: Model returned unexpected value '{vibe}'. Defaulting to 'none'.")
            return "none"

    except Exception as e:
        print(f"🚨 VibeDetector: Error calling Gemini API - {e}")
        return "none" # Safer to default to 'none' on error

# --- A simple test block so you can run this file directly to test it ---
if __name__ == "__main__":
    # This requires you to have your .env file in the root and run this from the root
    # using 'python -m agents.VibeDetectionAgent'
    from dotenv import load_dotenv
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if GOOGLE_API_KEY:
        genai.configure(api_key=GOOGLE_API_KEY)
        print("\n--- Testing VibeDetector ---")
        test_message_1 = "Can you explain how gradient descent works?"
        test_message_2 = "What if the stars were just neutrons in the brain of the universe?"
        test_message_3 = "Hey, how's it going?"
        test_message_4 = "write a poem about him" # <-- The key new test
        
        print(f"Message: '{test_message_1}' -> Vibe: {detect_vibe(test_message_1)}")
        print(f"Message: '{test_message_2}' -> Vibe: {detect_vibe(test_message_2)}")
        print(f"Message: '{test_message_3}' -> Vibe: {detect_vibe(test_message_3)}")
        print(f"Message: '{test_message_4}' -> Vibe: {detect_vibe(test_message_4)}")
        print("--- Test Complete ---")
    else:
        print("Please set your GOOGLE_API_KEY in a .env file to run tests.")