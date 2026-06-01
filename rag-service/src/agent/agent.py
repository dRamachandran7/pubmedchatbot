import logging
from typing import List, Dict, Optional
from ..config.settings import settings
from .tools import RAGTools
from .retrieval_router import RetrievalRouterAgent
from .query_analyzer import QueryAnalyzerAgent
from .query_builder import QueryBuilderAgent
from .response_generator import ResponseGeneratorAgent

logger = logging.getLogger(__name__)

class RAGAgent:
    def __init__(self):
        self.tools = RAGTools(settings.PUBMED_EMAIL)
        self.conversation_history: List[Dict] = []
        
        # Initialize sub-agents
        self.retrieval_router = RetrievalRouterAgent()
        self.query_analyzer = QueryAnalyzerAgent()
        self.query_builder = QueryBuilderAgent()
        self.response_generator = ResponseGeneratorAgent()
    
    def process_query(self, query: str, session_id: Optional[str] = None) -> Dict:
        """Process user query through agent pipeline"""
        logger.info(f"Processing query: {query}")
        
        try:
            # Step 1: Analyze query using QueryAnalyzerAgent
            logger.info("Step 1: QueryAnalyzerAgent - Analyzing query intent and complexity")
            analysis = self.query_analyzer.analyze(query)
            logger.info(f"  Query analysis result: {analysis}")
            
            # Step 2: Build optimized search query using QueryBuilderAgent
            logger.info("Step 2: QueryBuilderAgent - Building optimized search query")
            query_build_result = self.query_builder.build_query(query)
            optimized_query = query_build_result.get("primary_query", query)
            logger.info(f"  Optimized query: {optimized_query}")
            logger.info(f"  Alternative queries: {query_build_result.get('alternative_queries')}")
            logger.info(f"  Search strategy: {query_build_result.get('search_strategy')}")
            
            # Step 3: Route to determine if retrieval needed using RetrievalRouterAgent
            logger.info("Step 3: RetrievalRouterAgent - Determining if retrieval is needed")
            routing_decision = self.retrieval_router.should_retrieve(analysis)
            logger.info(f"  Routing decision: {routing_decision}")
            
            context_results = []
            search_results = []
            
            # Step 4: Conditionally retrieve using optimized query with RAGTools
            if routing_decision.get("should_retrieve"):
                logger.info("Step 4: RAGTools - Retrieving relevant PubMed articles")
                search_results = self.tools.search_pubmed(optimized_query, max_results=5)
                context_results = self.tools.retrieve_context(optimized_query, k=3)
                logger.info(f"  Retrieved {len(context_results)} context articles")
            else:
                logger.info("Step 4: Skipping retrieval based on routing decision")
            
            # Step 5: Generate response using ResponseGeneratorAgent
            logger.info("Step 5: ResponseGeneratorAgent - Generating response")
            response_data = self.response_generator.generate(query, context_results)
            
            return {
                "message": response_data.get("message"),
                "sources": self._format_sources(search_results),
                "conversationId": session_id or "default",
                "metadata": {
                    "analysis": analysis,
                    "retrieved": routing_decision.get("should_retrieve"),
                    "optimized_query": optimized_query,
                    "query_builder_result": query_build_result
                }
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            import traceback
            logger.error(traceback.format_exc())
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
