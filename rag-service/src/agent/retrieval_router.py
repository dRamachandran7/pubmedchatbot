import logging
from typing import Dict
import json
import requests
from ..config.prompts import QUERY_ANALYZER_PROMPT

logger = logging.getLogger(__name__)

class RetrievalRouterAgent:
    """Determines if a query requires PubMed retrieval or can be answered from context"""
    
    def __init__(self, model: str = "llama2", ollama_url: str = "http://localhost:11434" ):
        self.model = model
        self.ollama_url = ollama_url
    
    def should_retrieve(self, analysis: Dict) -> Dict:
        """Use query analysis to decide if retrieval is needed"""
        intent = analysis.get("intent", "")
        requires_research = intent in ["research", "diagnosis", "treatment", "evidence"]
        
        return {
            "should_retrieve": requires_research,
            "reasoning": f"Intent '{intent}' requires PubMed retrieval"
        }