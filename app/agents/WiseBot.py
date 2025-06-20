import os
import pandas as pd
import google.generativeai as genai
from google.generativeai import types
import plotly.express as px

# --- Configuration ---
if 'GOOGLE_API_KEY' in os.environ:
    genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
else:
    print("WARNING: GOOGLE_API_KEY environment variable not set.")

class WiseBot:
    """
    The main Conversational Agent for Wise. It thinks with the user,
    adapting its responses based on the selected 'Cognitive Lens'.
    """
    def __init__(self, lens: str = 'scientific', data_path: str = "../data/data/WMT_1970-10-01_2025-01-31.csv"):
        """
        Initializes the agent with a specific cognitive lens.

        Args:
            lens (str): The active lens ('scientific' or 'creative').
            data_path (str): Path to the data file for analysis.
        """
        self.lens = lens
        self.data_path = data_path
        self.df = None
        if os.path.exists(self.data_path):
            self.df = pd.read_csv(self.data_path)
        
        print(f"🤖 WiseBot initialized with '{self.lens}' lens.")

    def chat(self, user_message: str) -> dict:
        """
        Main chat function. Routes the user's message to the correct
        internal thinking process based on the lens and message content.
        """
        # --- Explicit Tool/Function Calling Logic ---
        # Check if the user is asking for a graph. This overrides the lens.
        if any(keyword in user_message.lower() for keyword in ['plot', 'graph', 'chart', 'visualize']):
            print("📈 Detected plotting request. Routing to graph generator.")
            return self._generate_plotly_chart(user_message)

        # --- Lens-based Routing ---
        if self.lens == 'creative':
            return self._get_creative_response(user_message)
        else: # Default to scientific
            return self._get_scientific_response(user_message)

    def _get_scientific_response(self, user_message: str) -> dict:
        """Generates a factual, analytical response."""
        print("🔬 Generating scientific response...")
        prompt = f"""You are a scientific assistant. Your goal is to explain the user's question in a way that is analytical, fact-based, and clear.
        Question: {user_message}"""
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return {"type": "text", "content": response.text.strip()}

    def _get_creative_response(self, user_message: str) -> dict:
        """Generates an imaginative, metaphorical response."""
        print("🎨 Generating creative response...")
        prompt = f"""You are a creative muse. Your task is to answer the user's prompt in a way that is artistic, poetic, or metaphorical.
        Prompt: {user_message}"""

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return {"type": "text", "content": response.text.strip()}

    def _generate_plotly_chart(self, user_message: str) -> dict:
        """Uses Gemini to write and execute Python code to generate a Plotly chart."""
        print("📊 Generating Plotly chart code...")
        if self.df is None:
            return {"type": "error", "content": "I can't generate a chart because the data file was not found."}

        # Let Gemini write the plotting code for us
        prompt = f"""You are a data visualization expert. You write Python code using the pandas and plotly.express libraries.
        A user wants to create a plot from a pandas DataFrame named 'df'. The DataFrame has the following columns: {list(self.df.columns)}.
        The user's request is: '{user_message}'

        Your task is to write Python code to generate a Plotly figure object named 'fig'.
        - Use the provided DataFrame 'df'.
        - The final line of your code MUST be `fig = ...`
        - Do NOT include any explanations or markdown, only the raw Python code.

        Example Request: "Plot the closing price over time."
        Example Code Output:
        import plotly.express as px
        fig = px.line(df, x='Date', y='Close', title='WMT Closing Price Over Time')

        Now, write the Python code for the user's request.
        """
        
        model = genai.GenerativeModel('gemini-1.5-pro') # Use Pro for better code generation
        code_response = model.generate_content(prompt)
        
        generated_code = code_response.text.strip().replace("```python", "").replace("```", "")
        print(f"Generated Code:\n---\n{generated_code}\n---")

        try:
            # IMPORTANT: exec() is powerful but risky in production. Perfect for a hackathon.
            # We create a local scope to execute the code in.
            local_scope = {'df': self.df, 'px': px}
            exec(generated_code, globals(), local_scope)
            fig = local_scope.get('fig')

            if fig:
                # Convert the figure to JSON so the frontend can render it
                chart_json = fig.to_json()
                return {"type": "plotly", "content": chart_json}
            else:
                return {"type": "error", "content": "I couldn't generate a chart from your request. Could you try rephrasing it?"}

        except Exception as e:
            print(f"🚨 Error executing generated code: {e}")
            return {"type": "error", "content": f"I ran into an error trying to create that chart: {e}"}


# --- A simple test block so you can run this file directly to test it ---
if __name__ == "__main__":
    print("\n--- Testing WiseBot ---")
    
    # Test 1: Scientific Lens
    bot_sci = WiseBot(lens='scientific')
    response_sci = bot_sci.chat("Explain the concept of 'market capitalization'.")
    print("\n[Scientific Response]:", response_sci['type'], "\n", response_sci['content'][:100] + "...")
    
    # Test 2: Creative Lens
    bot_creative = WiseBot(lens='creative')
    response_creative = bot_creative.chat("What is the stock market?")
    print("\n[Creative Response]:", response_creative['type'], "\n", response_creative['content'][:100] + "...")

    # Test 3: Plotly Chart Generation
    bot_plot = WiseBot(lens='scientific') # Lens doesn't matter for plotting
    response_plot = bot_plot.chat("Can you plot the trading volume for WMT over the years?")
    print("\n[Plotly Response]:", response_plot['type'])
    # print(response_plot['content']) # This will be a long JSON string
    assert response_plot['type'] == 'plotly' # Auto-check if it worked
    print("--- Test Complete ---")