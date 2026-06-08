import logging
from typing import Dict
import json
from groq import Groq
from ..config.settings import settings
from ..config.prompts import QUERY_ANALYZER_PROMPT

logger = logging.getLogger(__name__)

class QueryAnalyzerAgent:
    """Analyzes queries to determine type, intent, and complexity"""
    
    def __init__(self):
        self.client = self._init_client()
    
    def _init_client(self):
        """Initialize Groq client"""
        try:
            if not settings.GROQ_API_KEY:
                logger.error("GROQ_API_KEY not set")
                return None
            return Groq(api_key=settings.GROQ_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            return None
    
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
        if not self.client:
            logger.error("Groq client not initialized")
            return self._default_analysis()
        
        prompt = f"{QUERY_ANALYZER_PROMPT}\nUser Query: {query}"
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a biomedical query analyzer. Analyze the query and respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            response_text = response.choices[0].message.content
            logger.debug(f"Groq response: {response_text[:200]}")
            
            # Try to parse as JSON
            try:
                json_result = json.loads(response_text)
                return json_result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from Groq: {e}")
                logger.error(f"Response text was: {response_text[:500]}")
                return self._default_analysis()
                
        except Exception as e:
            logger.error(f"Error calling Groq for query analysis: {e}")
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
