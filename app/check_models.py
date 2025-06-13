# app/check_models.py

import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv() 

# Configure the API key
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
    print("API Key configured successfully.")
else:
    print("ERROR: GOOGLE_API_KEY environment variable not found.")
    exit() # Exit the script if no key is found

print("\n--- Available Models ---")
print("Fetching list of available models from Google AI...\n")

# Iterate through all available models
for m in genai.list_models():
    # The 'generateContent' method is what we need for our chatbot
    if 'generateContent' in m.supported_generation_methods:
        print(f"Model Name: {m.name}")
        # print(f"  - Supported Methods: {m.supported_generation_methods}")
        # print(f"  - Description: {m.description}\n")

print("\n--- End of List ---")
print("\nLook for a model name like 'models/gemini-1.0-pro' or 'models/gemini-pro' in the list above.")
print("Copy that exact name into your main.py file.")