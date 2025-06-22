import os
import pandas as pd
import google.generativeai as genai
import plotly.express as px

class ConversationalAgent:
    def __init__(self, lens: str = 'scientific', data_path: str = "data/wmt_stock_data.csv"):
        self.lens = lens
        self.data_path = data_path
        self.df = None
        if os.path.exists(self.data_path):
            self.df = pd.read_csv(self.data_path)
        print(f"🤖 ConversationalAgent initialized with '{self.lens}' lens.")

    def chat(self, user_message: str, history: list) -> dict:
        if any(keyword in user_message.lower() for keyword in ['plot', 'graph', 'chart', 'visualize']):
            print("📈 Detected plotting request. Routing to graph generator.")
            return self._generate_plotly_chart(user_message)
        if self.lens == 'creative':
            return self._get_creative_response(user_message, history)
        else:
            return self._get_scientific_response(user_message, history)

    def _format_history_for_prompt(self, history: list) -> str:
        if not history: return "This is the beginning of the conversation."
        formatted_history = ""
        for msg in history:
            role = "User" if msg["role"] == "user" else "AI"
            content = msg.get("content", "")
            if not content.startswith('{"type": "plotly"'):
                formatted_history += f"{role}: {content}\n"
        return formatted_history

    def _get_scientific_response(self, user_message: str, history: list) -> dict:
        print("🔬 Generating scientific response with context...")
        conversation_history = self._format_history_for_prompt(history)
        prompt = f"""You are a brilliant, context-aware AI assistant.
        CONVERSATION HISTORY:\n---\n{conversation_history}\n---\n
        Based on the complete history, provide a clear, factual, and analytical response to the LATEST user message.
        User: {user_message}\nAI:"""
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return {"type": "text", "content": response.text.strip()}

    def _get_creative_response(self, user_message: str, history: list) -> dict:
        print("🎨 Generating creative response with context...")
        conversation_history = self._format_history_for_prompt(history)
        prompt = f"""You are a clever, context-aware AI muse.
        CONVERSATION HISTORY:\n---\n{conversation_history}\n---\n
        Based on the complete history, provide an artistic, poetic, or metaphorical response to the LATEST user message.
        User: {user_message}\nAI:"""
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return {"type": "text", "content": response.text.strip()}

    def _generate_plotly_chart(self, user_message: str) -> dict:
        print("📊 Generating Plotly chart code...")
        if self.df is None: return {"type": "error", "content": "Data file not found."}
        prompt = f"""You are a Python data visualization expert specializing in Plotly Express. Your ONLY task is to write a single line of Python code that generates a Plotly figure object and assigns it to a variable named 'fig'. You will be working with a pre-existing pandas DataFrame named `df`. DO NOT create your own DataFrame. The `df` is already loaded.
        The `df` DataFrame has the following columns: {list(self.df.columns)}.
        The user's request is: '{user_message}'
        RULES:
        1. Assume `import plotly.express as px` and `import pandas as pd` are already done.
        2. Your output MUST be a single line of code starting with `fig = px...`.
        3. If the 'Date' column is used, it is a string. Convert it to datetime within your single line of code using `pd.to_datetime(df['Date'])`.
        4. DO NOT output the word "python", markdown backticks ```, or any explanations.
        Example Request: "Plot the closing price over time."
        Example Output: fig = px.line(df, x=pd.to_datetime(df['Date']), y='Close', title='WMT Closing Price Over Time')"""
        model = genai.GenerativeModel('gemini-1.5-pro')
        code_response = model.generate_content(prompt)
        generated_code = code_response.text.strip()
        print(f"Generated Code:\n---\n{generated_code}\n---")
        try:
            local_scope = {'df': self.df, 'px': px, 'pd': pd}
            exec(generated_code, globals(), local_scope)
            fig = local_scope.get('fig')
            if fig: return {"type": "plotly", "content": fig.to_json()}
            else: return {"type": "error", "content": "Could not generate a chart. Please rephrase."}
        except Exception as e:
            print(f"🚨 Error executing generated code: {e}")
            return {"type": "error", "content": f"I ran into an error: {e}"}