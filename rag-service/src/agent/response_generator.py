import logging
from typing import Dict, List, Optional
from ..config.settings import settings

logger = logging.getLogger(__name__)

class ResponseGeneratorAgent:
    """Generates responses based on retrieved context"""
    
    def __init__(self):
        self.llm_client = self._init_llm()

    def _init_llm(self):
        # Placeholder for LLM client initialization (e.g., OpenAI, Ollama)
        # For example, if using OpenAI:
        # import openai
        # openai.api_key = settings.OPENAI_API_KEY
        # return openai
        pass
    
    def generate(self, query: str, context: Optional[List[Dict]] = None) -> Dict:
        """
        Generate a response
        
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
            response = self.llm_client.ChatCompletion.create (
                model = "gpt-4",  # Example model
                messages = [{"role": "system", "content": "You are a helpful medical assistant."},
                            {"role": "user", "content": prompt}],
                temperature = 0.6, #low temp for more factual responses
                max_tokens = 500
            )

            message = response.choices[0].message.content.strip()

            return {
                "message": message,
                "sources_used": sources_used,
                "confidence": 0.9  # Placeholder confidence, should use semantic scoring later ig
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
