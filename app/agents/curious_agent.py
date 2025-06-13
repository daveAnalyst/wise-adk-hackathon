from agents.base_agent import BaseAgent
from pathlib import Path
import json

class CuriousAgent(BaseAgent): 
    def __init__(self, llm, data_path): 
        super().__init__(llm)
        self.data_path = Path(__file__).parent.parent / "data" / data_path
        self.data = self._load_data()
    
    def _load_data(self): 
        with open(self.data_path, "r") as f: 
            data = json.load(f)
        return data

    def analyze_data(self): 
        prompt = f"You're a science analyst. Analyze this data: \n{self.data}"
        return self.call_llm(prompt)