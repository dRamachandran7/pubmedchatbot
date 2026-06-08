import logging
from typing import Dict

logger = logging.getLogger(__name__)

class RetrievalRouterAgent:
    """Determines if a query requires PubMed retrieval or can be answered from context"""
    
    def __init__(self):
        pass
    
    def should_retrieve(self, analysis: Dict) -> Dict:
        """Use query analysis to decide if retrieval is needed"""
        intent = analysis.get("intent", "")
        requires_research = intent in ["research", "diagnosis", "treatment", "evidence"]
        
        return {
            "should_retrieve": requires_research,
            "reasoning": f"Intent '{intent}' requires PubMed retrieval"
        }