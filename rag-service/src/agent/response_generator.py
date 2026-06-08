import logging
from typing import Dict, List, Optional
from ..config.settings import settings
from groq import Groq

logger = logging.getLogger(__name__)

class ResponseGeneratorAgent:
    """Generates responses based on retrieved context"""
    
    def __init__(self):
        self.llm_client = self._init_llm()

    def _init_llm(self):
        """Initialize Groq client for LLM inference."""
        try:
            if not settings.GROQ_API_KEY:
                logger.error("GROQ_API_KEY not set")
                return None
            client = Groq(api_key=settings.GROQ_API_KEY)
            logger.info("Groq client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            return None
    
    def generate(self, query: str, context: Optional[List[Dict]] = None) -> Dict:
        """
        Generate a response using Groq.
        
        Returns:
            {
                "message": str,
                "sources_used": list,
                "confidence": float
            }
        """
        if not self.llm_client:
            logger.warning("LLM client not initialized, returning placeholder response")
            return {
                "message": "This is a placeholder response. LLM client not configured.",
                "sources_used": [],
                "confidence": 0.0
            }
        context = context or []
        sources_used = [c.get("pmid") for c in context if c.get("pmid")]

        prompt = self._build_prompt(query, context)

        try:
            response = self.llm_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a biomedical research assistant. Answer questions based on the provided PubMed articles, being accurate and evidence-based."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=500
            )
            message = (response.choices[0].message.content or "").strip()
            return {
                "message": message if message else "Unable to generate a response",
                "sources_used": sources_used,
                "confidence": 0.9
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
        
        return {
            "message": "An error occurred generating the response.",
            "sources_used": sources_used,
            "confidence": 0.0
        }
    
    def _build_prompt(self, query: str, context: List[Dict]) -> str:
        context_str = ""
        if context:
            context_str += "Based on these relevant articles:\n"
            for c in context:
                context_str += f"- {c.get('title', 'No title')} (PMID: {c.get('pmid', 'N/A')})\n  Summary: {c.get('summary', '')}\n"
            context_str += ("\nProvide a comprehensive answer with citations to the source articles. "
                            "Cite specific articles with their PMID, be accurate and evidence-based, "
                            "mention if information is uncertain, and provide links to relevant sources. "
                            "Format citations as: [Title](https://pubmed.ncbi.nlm.nih.gov/PMID)\n\n")

        return f"{context_str}Question: {query}"
