#!/usr/bin/env python
# coding: utf-8

# In[7]:


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
import asyncio
import re

#Ignore all warnings 
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

# print("All Libraries are imported")


# In[28]:


os.environ['GOOGLE_API_KEY'] = "AIzaSyAEDUokFA2dYLnu4Cogwz9tOrMaxOTWMys"
configure(api_key=os.environ['GOOGLE_API_KEY'])
client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])


# In[30]:


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



def science_stateful(query: str, tool_context: ToolContext) -> str: 
    """
    Responds to user queries in a scientific and analytical manner.

    This agent is activated when the conversation tone is classified as 'scientific'.
    It provides fact-based, logical, and structured responses, often referencing
    scientific concepts, definitions, or explanations.

    Parameters:
        query (str): The user’s input message.
        tool_context (ToolContext): Context object that includes vibe, messages, last_message.

    Returns:
        str: A scientifically reasoned response to the user query.
    """

    science_prompt = f"""
                    You are a scientific assistant. 

                    Your goal is to explain scientific questions in a way that is:
                    - Analytical and based on facts
                    - Logically reasoned
                    - Easy to understand, even for someone with a high school science background
                    - Structured and clear, using bullet points or paragraphs if appropriate

                    Avoid overly complex jargon unless it's essential, and define technical terms when used.
    
                    Question: 
                        {query}
                     """
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        config=types.GenerateContentConfig(
            temperature=1, 
            top_p=1, 
            max_output_tokens=2048
        ), 
        contents=science_prompt
    )
    result = Markdown(response.text).data
    return result
    
def creative_stateful(query: str, tool_context: ToolContext) -> str: 
    """
    Responds to user queries in a creative, imaginative, and expressive manner.

    This agent is activated when the conversation tone is classified as 'creative'.
    It generates responses that are metaphorical, artistic, poetic, or abstract in nature,
    aiming to inspire, provoke thought, or entertain.

    Parameters:
        query (str): The user’s input message.
        tool_context (ToolContext): Context object that may include session state, tools, and memory.

    Returns:
        str: A creatively inspired response based on the user's message.
    """
    creative_prompt = f"""
            You are a creative assistant who responds with imagination, beauty, and expression.
            
            Your task is to answer the user's message in a way that is:
            - Artistic, poetic, or metaphorical
            - Emotionally evocative or thought-provoking
            - Abstract, whimsical, or story-driven if suitable
            - Original and free-form, like a piece of creative writing
            
            Avoid sounding robotic or overly technical. Feel free to use poetic devices, analogies, or even short stories.
            
            Here is the user's prompt:
            {query}
        """

    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        config=types.GenerateContentConfig(
            temperature=1, 
            top_p=1, 
            max_output_tokens=2048
        ), 
        contents=creative_prompt
    )
    result = Markdown(response.text).data
    return result
    
def read_memory(memory_path): 
    with open(memory_path, "r") as f: 
        old_memory = json.load(f)
    return old_memory


# In[31]:


#1. Creating the science Agent
try: 
    science_agent = Agent(
        name="science_agent", 
        model="gemini-2.0-flash", 
        description = "Analyze the user's question and gives an explanation using 'science_stateful'. ", 
        instruction = "You are science_agent. Your job is to give an analytical explanation using 'science_stateful' tool"
                    "Handle only the explanation part. ", 
        tools = [science_stateful]
    )

except Exception as e: 
    print(f"Could not define creative_agent. Please Check Model and API Key. Error: {e}")

#2. Creating the creative agent
try: 
    creative_agent = Agent(
        name="creative_agent", 
        model="gemini-2.0-flash", 
        description="Analyze the user's ", 
        instruction="", 
        tools = [creative_stateful]
    )

except Exception as e: 
    print(f"Could not define science_agent. Please Check Model and API Key. Error: {e}")


# In[32]:


class conversational_agent: 
    def __init__(self, science_agent, creative_agent): 
        self.creative_agent = creative_agent
        self.science_agent = science_agent
        
    async def run(self, query, vibe): 
        #The logic runs here, depends on which vibe is chosen. 

        session_service_stateful = InMemorySessionService()
        USER_ID_STATEFUL = "user_1"
        APP_NAME_science = "science_agent_v1"
        APP_NAME_creative = "creative_agent_v1"
        SESSION_ID_STATEFUL = "session_001"

        chat_state = {"vibe": None, "messages": [], "last_message": None}
        memory_path = "../data/chat_state.json"

        if vibe == "scientific": 
            APP_NAME = APP_NAME_science
            if(os.path.exists(memory_path)):  
                print(f"🟢Loading previous state..")
                session_stateful = await session_service_stateful.create_session(
                    app_name=APP_NAME_science, 
                    user_id=USER_ID_STATEFUL, 
                    session_id=SESSION_ID_STATEFUL, 
                    state=read_memory(memory_path)
                )
            
            else: 
                session_stateful = await session_service_stateful.create_session(
                    app_name=APP_NAME_science, 
                    user_id=USER_ID_STATEFUL, 
                    session_id=SESSION_ID_STATEFUL, 
                    state=chat_state
                )
            retrieved_session = await session_service_stateful.get_session(app_name=APP_NAME_science, 
                                                                   user_id = USER_ID_STATEFUL, 
                                                                   session_id = SESSION_ID_STATEFUL)
                    
            runner = Runner(
                agent = self.science_agent, 
                app_name = APP_NAME_science, 
                session_service = session_service_stateful
            )
            print(f"Runner created for agent '{runner.agent.name}'. ")

        elif vibe == "creative": 
            APP_NAME = APP_NAME_creative
            if(os.path.exists(memory_path)):  
                print(f"🟢Loading previous state..")
                session_stateful = await session_service_stateful.create_session(
                    app_name=APP_NAME_creative, 
                    user_id=USER_ID_STATEFUL, 
                    session_id=SESSION_ID_STATEFUL, 
                    state=read_memory(memory_path)
                )
            else: 
                session_stateful = await session_service_stateful.create_session(
                    app_name=APP_NAME_creative, 
                    user_id=USER_ID_STATEFUL, 
                    session_id=SESSION_ID_STATEFUL, 
                    state=chat_state
                )
                
            retrieved_session = await session_service_stateful.get_session(app_name=APP_NAME_creative, 
                                                                   user_id = USER_ID_STATEFUL, 
                                                                   session_id = SESSION_ID_STATEFUL)
            runner = Runner(
                agent = self.creative_agent, 
                app_name = APP_NAME_creative, 
                session_service = session_service_stateful
            )
            print(f"Runner created for agent '{runner.agent.name}'. ")
        stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]
        stored_session.state["messages"].append(query)
        stored_session.state["last_message"] = query
        response = await call_agent_async(query=query, 
                        runner=runner, 
                        user_id = USER_ID_STATEFUL, 
                        session_id=SESSION_ID_STATEFUL)
        return response
#Dummy test to see whether it runs

def run_conversation(query: str, vibe: str): 
    agent = conversational_agent(science_agent, creative_agent)
    file_path = "../data/chat_state.json"
    with open(file_path, "r") as f:
        data = json.load(f)
    data['vibe'] = vibe
    data["messages"].append(query)     # Append to a list
    data["last_message"] = query
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2) 
    agent_response = asyncio.run(agent.run(query, vibe))
    return agent_response

#Dummy test
#just enter the query and vibe
if __name__ == "__main__":
    print(run_conversation("What do u think of first world country?", "scientific"))
