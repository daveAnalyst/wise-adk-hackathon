class BaseAgent: 
    def __init__(self, llm): 
        self.llm = llm

    def call_llm(self, prompt: str): 
        """
        Calls Google Gemini model with a prompt and returns text output.
        """
        try: 
            response = self.llm.generate_content(prompt)
            return response.text
        except Exception as e: 
            return f"LLM Error: {e}"