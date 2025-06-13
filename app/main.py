# app/main.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv # Used to load environment variables from a .env file

# Import the agent classes Davin created
from agents.curious_agent import CuriousAgent
# We will need a science_agent.py file soon, but we can use CuriousAgent as a placeholder
# from agents.science_agent import ScienceAgent 

# --- App Initialization ---
app = Flask(__name__)
CORS(app) # Allows your Streamlit frontend (on a different port) to call this API

# --- AI and Agent Initialization ---

# Load environment variables from a .env file in the same directory
# This is a best practice for managing secrets like API keys locally
load_dotenv() 

# Securely configure the API key from an environment variable
# This is much safer than hardcoding the key in the script.
API_KEY = os.getenv("GOOGLE_API_KEY")
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
else:
    print("WARNING: GOOGLE_API_KEY environment variable not found.")
    print("Please create a .env file in the 'app/' directory and add GOOGLE_API_KEY='your_key_here'")


# Initialize Agents
# For the hackathon, we can point to placeholder data files.
# Let's create these files so the app doesn't crash.
creative_agent = CuriousAgent(model, data_path="creative_data.json")
science_agent = CuriousAgent(model, data_path="science_data.json") # Using CuriousAgent as a placeholder for now

# --- API Routes (The Endpoints Your Frontend Calls) ---

@app.route('/chat', methods=['POST'])
def chat():
    if not model:
        return jsonify({'error': 'AI model not initialized. Is the API key missing?'}), 500

    data = request.get_json()
    if not data or 'message' not in data or 'mood' not in data:
        return jsonify({'error': 'Invalid request. "message" and "mood" are required.'}), 400

    user_message = data['message']
    mood = data['mood']
    
    reply = ""
    # This is the core Orchestrator logic
    if mood == 'science':
        prompt = f"You are a science communicator. Explain the core concept of '{user_message}' simply and accurately."
        reply = science_agent.call_llm(prompt)
    elif mood == 'creative':
        prompt = f"You are a creative muse. Generate a short, inspiring, one-sentence idea related to '{user_message}'."
        reply = creative_agent.call_llm(prompt)
    else:
        reply = "I'm in a general mood. Let's talk about anything!"

    return jsonify({'reply': reply})


@app.route('/spark', methods=['POST'])
def spark():
    if not model:
        return jsonify({'error': 'AI model not initialized. Is the API key missing?'}), 500

    prompt = "Generate a single, surprising, cross-disciplinary idea in one sentence that connects two unlikely fields (e.g., marine biology and architecture)."
    reply = creative_agent.call_llm(prompt)
    
    return jsonify({'reply': reply})


# This block runs when you execute 'python main.py'
if __name__ == '__main__':
    # The 'debug=True' flag automatically reloads the server when you save changes.
    app.run(host='0.0.0.0', port=5000, debug=True)