# app/main.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv

# --- Placeholder for Agent Imports (Davin will create these files) ---
# from agents.daydream_agent import DaydreamAgent
# from agents.vibe_detection_agent import VibeDetectionAgent
# from agents.conversational_agent import ConversationalAgent

# --- App Initialization ---
app = Flask(__name__)
CORS(app) 

# --- AI Model Initialization ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
model = None

if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
    print("Gemini AI Model Initialized Successfully.")
else:
    print("FATAL ERROR: GOOGLE_API_KEY environment variable not found.")

# --- Agent Initialization (We create one instance of each agent) ---
# Davin will replace these with his real agent classes
# For now, we create placeholder objects so the code can run.
class PlaceholderAgent:
    def __init__(self, name):
        self.name = name
    def get_proactive_spark(self):
        return "What if we could use bioluminescence to create self-powered streetlights?"
    def detect_vibe(self, text):
        return "imaginative" if "idea" in text else "analytical"
    def run(self, message, vibe):
        return f"This is a placeholder response from the {self.name} for your message: '{message}' in '{vibe}' vibe."

daydream_agent = PlaceholderAgent("DaydreamAgent")
vibe_detection_agent = PlaceholderAgent("VibeDetectionAgent")
conversational_agent = PlaceholderAgent("ConversationalAgent")

# ==============================================================================
# --- API ENDPOINTS ---
# ==============================================================================

# This endpoint powers the "Intelligent Welcome" for existing users.
@app.route('/welcome_back', methods=['POST'])
def welcome_back():
    print("Received request for /welcome_back")
    # TODO: Replace with real agent call
    # spark = daydream_agent.get_proactive_spark()
    spark = daydream_agent.get_proactive_spark()
    
    greeting = "Welcome back, Dave!" # We can add more logic here later
    return jsonify({
        "greeting": greeting,
        "spark_idea": spark
    })

# This endpoint handles the initial message from a user to set the vibe.
@app.route('/set_vibe_from_text', methods=['POST'])
def set_vibe_from_text():
    print("Received request for /set_vibe_from_text")
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Missing message field'}), 400
    
    user_message = data['message']
    
    # TODO: Replace with real agent call
    # detected_vibe = vibe_detection_agent.detect_vibe(user_message)
    detected_vibe = vibe_detection_agent.detect_vibe(user_message)

    return jsonify({'detected_vibe': detected_vibe})

# This is the main conversational endpoint.
@app.route('/chat', methods=['POST'])
def chat():
    print("Received request for /chat")
    if not model:
        return jsonify({'error': 'AI model not initialized.'}), 500

    data = request.get_json()
    if not data or 'message' not in data or 'vibe' not in data:
        return jsonify({'error': 'Invalid request. "message" and "vibe" are required.'}), 400

    user_message = data['message']
    vibe = data['vibe']
    
    # TODO: Replace with real agent call
    # reply = conversational_agent.run(message=user_message, vibe=vibe)
    reply = conversational_agent.run(user_message, vibe)

    return jsonify({'reply': reply})

# This is for the manual "On-Demand Spark" button.
@app.route('/spark', methods=['POST'])
def spark():
    print("Received request for /spark")
    if not model:
        return jsonify({'error': 'AI model not initialized.'}), 500

    # This can call the DaydreamAgent or a simpler creative prompt directly.
    # TODO: Replace with real agent call
    # spark_reply = daydream_agent.get_proactive_spark() 
    spark_reply = daydream_agent.get_proactive_spark()
    
    return jsonify({'reply': spark_reply})


# This block runs when you execute 'python main.py'
if __name__ == '__main__':
    print("Starting Wise Backend Server...")
    # Setting host to '0.0.0.0' makes it accessible on your local network
    app.run(host='0.0.0.0', port=5000, debug=True)