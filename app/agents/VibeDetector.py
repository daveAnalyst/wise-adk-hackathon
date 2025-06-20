import os
import google.generativeai as genai
from google.generativeai import types

# --- Configuration ---
# It's better to get this from environment variables in main.py, 
# but for now, this will work.
# IMPORTANT: Make sure the API key is set in your environment before running Flask.
# In your terminal: export GOOGLE_API_KEY="AIzaSy...WMys"
if 'GOOGLE_API_KEY' in os.environ:
    genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
else:
    print("WARNING: GOOGLE_API_KEY environment variable not set.")

# --- The Core Logic, Extracted and Simplified ---

def detect_vibe(user_message: str) -> str:
    """
    Analyzes a user's message and classifies its tone as 'scientific' or 'creative'.

    Args:
        user_message: The text from the user.

    Returns:
        A string, either 'scientific', 'creative', or 'none'.
    """
    if not user_message:
        return "none"

    print(f"🧠 VibeDetector: Analyzing message -> '{user_message[:50]}...'")

    # This is the prompt Davin wrote, it's good.
    prompt = f"""You are a vibe Detector. 
Given Data(str) below. Classify its tone as either 'scientific' or 'creative'. 

Classification Instruction: 
---------------------------------
You are a vibe-detection agent. Given a user's messages, classify its tone as one of ahe following:
1. 'scientific' - The user is analytical, precise, logical or technical. They may ask for explanations, data, or structured reasoning.
2. 'creative' - The user is imaginative, metaphorical, poetic and artistic. They may be expressing abstract ideas, inventing concepts.
3. 'none' - IF the user's message is a simple greeting/farewell (example: hi, hallo, hey, bye, see you)

Return ONLY ONE word: 'scientific', 'creative', or 'none'. 


Examples:
    - "Can you explain how gradient descent works in machine learning?" → scientific
    - "What if the stars were just neutrons in the brain of the universe?" → creative
    - "How do LLMs store and recall information?" → scientific
    - "Let's invent a theory where gravity is made of music." → creative
    - "Hello there" → none

------------------------------------
Data: {user_message}
"""
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config=types.GenerationConfig(
                temperature=0.0, # Set to 0 for classification tasks
                max_output_tokens=10 # We only need one word
            )
        )
        
        # Clean up the response to get just the keyword
        vibe = response.text.strip().lower()
        print(f"✅ VibeDetector: Detected vibe -> {vibe}")

        # Basic validation to make sure the model output is correct
        if vibe in ['scientific', 'creative', 'none']:
            return vibe
        else:
            print(f"⚠️ VibeDetector: Model returned unexpected value '{vibe}'. Defaulting to 'scientific'.")
            return "scientific" # Default to a safe option

    except Exception as e:
        print(f"🚨 VibeDetector: Error calling Gemini API - {e}")
        return "scientific" # If there's an error, default to the safe 'scientific' lens


# --- A simple test block so you can run this file directly to test it ---
if __name__ == "__main__":
    test_message_1 = "Can you explain how gradient descent works in machine learning?"
    test_message_2 = "What if the stars were just neutrons in the brain of the universe?"
    test_message_3 = "Hey, how's it going?"
    
    print("\n--- Testing VibeDetector ---")
    print(f"Message: '{test_message_1}' -> Vibe: {detect_vibe(test_message_1)}")
    print(f"Message: '{test_message_2}' -> Vibe: {detect_vibe(test_message_2)}")
    print(f"Message: '{test_message_3}' -> Vibe: {detect_vibe(test_message_3)}")
    print("--- Test Complete ---")