#!/usr/bin/env python
# coding: utf-8

# In[62]:


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
import asyncio

#Ignore all warnings 
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

# print("All Libraries are imported")


# In[63]:


os.environ['GOOGLE_API_KEY'] = "AIzaSyAEDUokFA2dYLnu4Cogwz9tOrMaxOTWMys"
configure(api_key=os.environ['GOOGLE_API_KEY'])
client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])


# In[64]:


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

# In[77]:


def intelligent_hello(name: Optional[str] = None) -> str: 
    """
    Provides a warm welcome. If a name is provided, it will be used. 

    Args: 
        name(str, optional): The name of the person to greet. Defaults to a generic greeting if not provided. 

    Returns: 
        str: A friendly, varied greeting message and ask what the user is interested in.
    """
    greetings_with_name = [
        "Hi {name}, I’m Wise. What topics spark your curiosity lately?",
        "Welcome {name}! I’m Wise. What’s something you’ve been wanting to explore?",
        "Hey {name}, I’m Wise. What are a few things you're passionate about?",
        "Hello {name}, ready to dive into new ideas? What excites you these days?",
    ]

    greetings_generic = [
        "Hello, I’m Wise. What are a few topics that excite you?",
        "Hey there, I’m Wise. What have you been curious about lately?",
        "Welcome! I’m Wise. What would you love to explore today?",
        "Hi, I’m Wise. Tell me something that’s been on your mind recently.",
    ]
    if name: 
        greeting = random.choice(greetings_with_name).format(name=name)
    else: 
        greeting = random.choice(greetings_generic)
    return greeting

    
def daydream_stateful(tool_context: ToolContext) -> dict: 
    """
    Delivering an intelligent welcome message based on the user's conversation history (messages) in the session state. 
    """
    print("--- daydream_stateful called ---")

    #Retrieve memory from state 
    history = tool_context.state.get("messages", [])

    if history: 
        print(f"🟢 Thinking...............")
        prompt = f"""
        You are an intelligent welcome bot.
        
        Your goal is to craft a short, curious, and insightful welcome message based on the user's recent message(s). 
        Start the message with a spark — something that makes the user go "Hmm, that's interesting!" 
        It can be a surprising fact, a playful observation, or a thoughtful twist related to the user's message.
        
        Guidelines:
        - Start with phrases like: "Did you know...", "Here's something curious...", or "Imagine this..."
        - Make it engaging, thoughtful, or fun — like a friendly AI trying to start a meaningful conversation.
        - Use the user's message to stay on-topic, but add a fresh perspective.
        
        Example:
        User message: "Why is a leaf green?"
        → Response: "Did you know that leaves don't just reflect green — they’re busy converting light into food using chlorophyll? It’s like nature’s solar panel!"
        
        User message: "Do LLMs actually understand language?"
        → Response: "Here's something curious: LLMs don't 'understand' like we do — they just predict what comes next. Yet they can still write poetry. Weird, right?"
        
        User message: "Hi"
        → Response: "Hello there! 🌟 Ready to dive into something interesting today?"
        
        -------------------------------------
        User Message History: {random.choice(history)}
        """

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(
                temperature=1,
                top_p=1,
                max_output_tokens=1024,
            ),
            contents=prompt)
        
        result = Markdown(response.text).data.strip()
        return result
    else: 
        return intelligent_hello()
    
#--- Intelligent Greeting Agent--- 
try: 
    greeting_agent = Agent(
        name="intel_hello_agent", 
        model="gemini-2.0-flash", 
        description="Handles greetings and hellos using the 'intelligent_hello' tool. ", 
        instruction = ("You are the greeting Agent. Your ONLY task is to provide a friendly greeting. Do nothing else."
                      "Use the 'intelligent_hello' tool to generate the greeting. "
                      "If the user provides their name, make sure to pass it to the tool. "
                      "Do not engage in any other conversation or tasks"), 
        tools=[intelligent_hello]
    )
    print(f"{greeting_agent.name} is successfully created using the model {greeting_agent.model}")
except Exception as e: 
    print(f"Could not create the {greeting_agent.name}. Check API key and the Model. Error: {e}")


# In[78]:


try: 
    #1 Configure the Agent
    daydream_agent = Agent(
        name="daydream_agent", 
        model = "gemini-2.0-flash", 
        description = "Main Agent: Analyzes user messages and delivers intelligent, engaging welcomes that spark meaningful conversations.", 
        instruction = """
                        You are daydream_agent. Your job is to analyze user messages and delivers intelligent welcome using 'daydream_stateful' tool. 
                        The tool will deliver an intelligent welcome (str) stored IN state.  
                        Handle only intelligent welcome on the messages based on state.
                      """,
        tools = [daydream_stateful], 
        #sub_agents=[greeting_agent]
    )

    #2 Configure InMemorySessionService
    session_service_stateful = InMemorySessionService() 

    #3 Define constants for indentifying the interactio context
    APP_NAME = "daydream_agent_v1"
    USER_ID_STATEFUL = "user_1" #Dummy test user_1
    SESSION_ID_STATEFUL = "session_001"
    chat_state = {"vibe": None, "messages": [], "last_message": None}

    #4 Create specific session where the conversation will happen 
    async def create_session():
        memory_path = "../data/chat_state.json"
        if(os.path.exists(memory_path)):  
            session_stateful = await session_service_stateful.create_session(
                app_name=APP_NAME, 
                user_id=USER_ID_STATEFUL, 
                session_id=SESSION_ID_STATEFUL, 
                state=read_memory(memory_path)
            )
        else: 
            session_stateful = await session_service_stateful.create_session(
                app_name=APP_NAME, 
                user_id=USER_ID_STATEFUL, 
                session_id=SESSION_ID_STATEFUL, 
                state=chat_state
            )

        retrieved_session = await session_service_stateful.get_session(app_name=APP_NAME,
                                                         user_id=USER_ID_STATEFUL,
                                                         session_id = SESSION_ID_STATEFUL)
        return retrieved_session, session_stateful
    
    retrieved_session, session_stateful = asyncio.run(create_session())
    # print("\n--- Initial Session State ---")
    # if retrieved_session:
    #     print(retrieved_session.state)
    # else:
    #     print("Error: Could not retrieve session.")
        
    #5 Create a Runner 
    runner = Runner(
        agent = daydream_agent, 
        app_name = APP_NAME, 
        session_service = session_service_stateful
    )
    
    print(f"Runner created for agent '{runner.agent.name}'. ")

except Exception as e: 
    print(f"Could not create agent. Please check API Key and model name. Error: {e}")


# In[79]:


stored_session = session_service_stateful.sessions[APP_NAME][USER_ID_STATEFUL][SESSION_ID_STATEFUL]

async def interaction_func(query: str): 
    #retrieved_session, session_stateful = await create_session()
    response = await call_agent_async(query=query, 
                      runner = runner, 
                      user_id = USER_ID_STATEFUL, 
                      session_id = SESSION_ID_STATEFUL)
    # print(stored_session.state)
    return response

def run_daydream(query: str) -> str: 
    agent_response = asyncio.run(interaction_func("hello"))
    return agent_response


#Dummy test
#just enter the query
if __name__ == "__main__":
    print(run_daydream("Hi, there"))