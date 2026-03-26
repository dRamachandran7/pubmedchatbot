import logging
from typing import List, Dict
from ..config.settings import settings
from .tools import RAGTools
from .retrieval_router import RetrievalRouterAgent
from .query_analyzer import QueryAnalyzerAgent
from .response_generator import ResponseGeneratorAgent

logger = logging.getLogger(__name__)

class RAGAgent:
    def __init__(self):
        self.tools = RAGTools(settings.PUBMED_EMAIL)
        self.conversation_history: List[Dict] = []
        
        # Initialize sub-agents
        self.retrieval_router = RetrievalRouterAgent()
        self.query_analyzer = QueryAnalyzerAgent()
        self.response_generator = ResponseGeneratorAgent()
    
    def process_query(self, query: str, session_id: str = None) -> Dict:
        """Process user query through agent pipeline"""
        logger.info(f"Processing query: {query}")
        
        try:
            # Step 1: Analyze query
            analysis = self.query_analyzer.analyze(query)
            
            # Step 2: Route to determine if retrieval needed
            routing_decision = self.retrieval_router.should_retrieve(analysis)
            
            context_results = []
            search_results = []
            
            # Step 3: Conditionally retrieve
            if routing_decision.get("should_retrieve"):
                search_results = self.tools.search_pubmed(query, max_results=5)
                context_results = self.tools.retrieve_context(query, k=3)
            
            # Step 4: Generate response
            response_data = self.response_generator.generate(query, context_results)
            
            return {
                "message": response_data.get("message"),
                "sources": self._format_sources(search_results),
                "conversationId": session_id or "default",
                "metadata": {
                    "analysis": analysis,
                    "retrieved": routing_decision.get("should_retrieve")
                }
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "message": "An error occurred processing your query",
                "sources": [],
                "conversationId": session_id or "default"
            }
    
    def _format_sources(self, articles: List[Dict]) -> List[Dict]:
        """Format articles as sources"""
        sources = []
        for article in articles:
            sources.append({
                "title": article.get("title", ""),
                "pmid": article.get("pmid", ""),
                "relevance": 0.95,
                "excerpt": article.get("abstract", "")[:200]
            })
        return sources
