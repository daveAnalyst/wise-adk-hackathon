#!/usr/bin/env python
# coding: utf-8

# In[2]:


from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.memory import InMemoryMemoryService
from google.generativeai import configure
from google.genai import types
from google import genai
import warnings
from IPython.display import HTML, Markdown, display
from typing import Optional, Dict, Any
from types import SimpleNamespace
import os
import random
import json
import textwrap
import re
import asyncio

#Ignore all warnings 
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

print("All Libraries are imported")


# In[3]:


os.environ['GOOGLE_API_KEY'] = "AIzaSyAEDUokFA2dYLnu4Cogwz9tOrMaxOTWMys"
configure(api_key=os.environ['GOOGLE_API_KEY'])
client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])


# In[4]:


async def call_agent_async(query: str, runner, user_id, session_id): 
    """Sends a query to the agent and prints the final responose. """
    # print(f"\n >>> User Query: {query}")

    #Prepare the user's messages in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response." #Default response

    #run_async executes the agent logic and yields Events.
    #We iterate through events to find the final answer.
    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content): 
        # print(f"[Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        if event.is_final_response(): 
            if event.content and event.content.parts: 
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate: #Handle potential errors
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break
    # print(f"<<< Agent Response: {final_response_text}")
    return final_response_text

def read_memory(memory_path): 
    with open(memory_path, "r") as f: 
        old_memory = json.load(f)
    return old_memory


# In[5]:


def vibe_stateful(tool_context: ToolContext) -> dict: 
    """Classifying the last_message based on session state as vibe"""
    print(f"--- Tool: vibe_stateful called ---")
    last_message = tool_context.state.get("last_message", None) 
    # print(f"🟢 . Checking the last message : {last_message}")
    
    if last_message: 
        print("🟢 Thinking Vibe...............")
        code_prompt = f"""
        You are a vibe Detector. 
        Given Data(str) below. Classify its tone as either 'scientific' or 'creative'. 
        
        Classification Instruction: 
        ---------------------------------
        You are a vibe-detection agent. Given a user's messages, classify its tone as one of the following:
        1. 'scientific' - The user is analytical, precise, logical or technical. They may ask for explanations, data, or structured reasoning.
        2. 'creative' - The user is imaginative, metaphorical, poetic and artistic. They may be expressing abstract ideas, inventing concepts.
        3. None - IF the user's message is greeting/farewell (example: hi, hallo, hey, bye, see you)
        
        Return ONLY one word: 'scientific' or 'creative'. 
        
        
        Examples:
            - "Can you explain how gradient descent works in machine learning?" → scientific
            - "What if the stars were just neutrons in the brain of the universe?" → creative
            - "How do LLMs store and recall information?" → scientific
            - "Let's invent a theory where gravity is made of music." → creative 
        
        ------------------------------------
        Data: {last_message}
        """
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(
                temperature=1,
                top_p=1,
                max_output_tokens=1024,
            ),
            contents=code_prompt)
        
        tool_context.state["vibe"] = Markdown(response.text).data.strip()
        report = f"Based on the last message, the vibe would be {tool_context.state['vibe']}"
        result = {"status": "success", "report": report}

    else: 
        print(f"last_message not found")
        return {"status": "error", "error_message": "last_message not found"}

print("✅ State-aware 'vibe_stateful' tool defined.")


# In[6]:


try: 
    vibe_agent = Agent(
        model="gemini-2.0-flash", 
        name="vibe_agent", 
        description = "Main Agent: Analyzes user last messages to determine their tone as 'scientific' or 'creative'.", 
        instruction = """
                        You are the vibe_agent. Your job is to determine the last_message tone using 'vibe_stateful'. 
                        The tool will determine the tone of the last_message stored IN state. 
                        Handle determination of the last message tone.
                      """, 
        tools = [vibe_stateful]
        #sub_agents=[greeting_agent]
    )


   #2 Configure InMemorySessionService
    session_service_stateful = InMemorySessionService() 
    print("✅ New InMemorySessionService created for state demonstration.")

    #3 Define constants for indentifying the interactio context
    APP_NAME = "vibe_agent_v1"
    USER_ID_STATEFUL = "user_1" #Dummy test user_1
    SESSION_ID_STATEFUL = "session_001"
    initial_state = {"vibe": None, "messages": [], "last_message": None}

    #4 Create specific session where the conversation will happen 
    async def create_session(): 
        session_stateful = await session_service_stateful.create_session(
            app_name=APP_NAME, 
            user_id=USER_ID_STATEFUL, 
            session_id=SESSION_ID_STATEFUL, 
            state=initial_state)
        print(f"✅ Session '{SESSION_ID_STATEFUL}' created for user '{USER_ID_STATEFUL}'.")

        retrieved_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                            user_id=USER_ID_STATEFUL,
                                                            session_id = SESSION_ID_STATEFUL)
        return session_stateful, retrieved_session
    
    session_stateful, retrieved_session = asyncio.run(create_session())
    print("\n--- Initial Session State ---")
    if retrieved_session:
        print(retrieved_session.state)
    else:
        print("Error: Could not retrieve session.")
        
    #5 Create a Runner 
    runner = Runner(
        agent = vibe_agent, 
        app_name = APP_NAME, 
        session_service = session_service_stateful, 
    )
    print(f"Runner created for agent '{runner.agent.name}'. ")

except Exception as e: 
    print(f"Could not create agent. Please check API Key and model name. Error: {e}")
    if not greeting_agent: print("greeting_agent is missing")
    if not farewell_agent: print("farewell_agent is missing")


# In[7]:


#Example on how it runs!

stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
async def interaction_func(query: str): 

    stored_session.state["messages"].append(query)
    stored_session.state["last_message"] = query 
    
    response = await call_agent_async(query=query, 
                      runner = runner, 
                      user_id = USER_ID_STATEFUL, 
                      session_id = SESSION_ID_STATEFUL)
    # print(stored_session.state)
    with open("../data/chat_state.json", "w") as f: 
        json.dump(stored_session.state, f)
    print(stored_session.state)
    return stored_session.state['vibe']


def run_vibe(query: str): 
    
    vibe_response = asyncio.run(interaction_func(query))
    return vibe_response

#Dummy test
#just enter the query
if __name__ == "__main__":
    print(run_vibe("where is the color of flowers from?"))