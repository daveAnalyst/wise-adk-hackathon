from flask import Flask, request, jsonify
import google.generativeai as genai
from agents.science_agent import ScienceAgent
from agents.curious_agent import CuriousAgent

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat(): 
    data = request.get_json() 

    if not data or 'message' not in data: 
        return jsonify({'error' : 'Missing message field'})
    
    user_message = data['message']
    reply = f"You said: {user_message}"
    return jsonify({'reply': reply})

def main(): 
    #Set your Gemini API key
    #Insert your api key here.
    genai.configure(api_key="")

    #Initialize the Gemini Model
    model = genai.GenerativeModel("gemini-pro")

    #Initialize Agents
    #Insert datapath in order for it to work
    science_agent = ScienceAgent(model, data_path=None) 
    support_agent = CuriousAgent(model, data_path=None)


if __name__ == '__main__':
    main()
    app.run(debug=True)
