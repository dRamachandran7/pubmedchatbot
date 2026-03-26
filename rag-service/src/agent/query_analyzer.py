import logging
from typing import Dict
import json
import requests
from ..config.prompts import QUERY_ANALYZER_PROMPT

logger = logging.getLogger(__name__)

class QueryAnalyzerAgent:
    """Analyzes queries to determine type, intent, and complexity"""
    #Change url as necessary, llama2 is cheap so good for this simple task
    def __init__(self, model: str = "llama2", ollama_url: str = "http://localhost:11434" ):
        self.model = model
        self.ollama_url = ollama_url
    
    def analyze(self, query: str) -> Dict:
        """
        Analyze the query for characteristics
        
        Returns:
            {
                "query_type": str,  # e.g., "factual", "opinion", "comparison"
                "intent": str,  # e.g., "research", "diagnosis", "treatment"
                "complexity": str,  # e.g., "simple", "moderate", "complex"
                "entities": list
            }
        """
        prompt = f"{QUERY_ANALYZER_PROMPT}\nUser Query: {query}"

        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json = {
                "model" : self.model,
                "prompt" : prompt,
                "stream" : False
            }
        )

        response_text = response.json()["response"]
        json_result = json.loads(response_text)

        return json_result
