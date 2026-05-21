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
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return self._default_analysis()
            
            response_text = response.json().get("response", "")
            logger.debug(f"Raw Ollama response: {response_text[:200]}")
            
            # Try to parse as JSON
            try:
                json_result = json.loads(response_text)
                return json_result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from Ollama: {e}")
                logger.error(f"Response text was: {response_text[:500]}")
                return self._default_analysis()
                
        except Exception as e:
            logger.error(f"Error calling Ollama for query analysis: {e}")
            return self._default_analysis()
    
    def _default_analysis(self) -> Dict:
        """Return default analysis when parsing fails"""
        return {
            "query_type": "unknown",
            "intent": "research",  # Assume research intent for safety
            "complexity": "moderate",
            "entities": []
        }

        return json_result
