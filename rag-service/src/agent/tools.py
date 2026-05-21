import logging
from typing import List, Dict
from .pubmed_retriever import PubMedRetriever
from ..retrieval.vector_store import VectorStore

logger = logging.getLogger(__name__)

class RAGTools:
    def __init__(self, pubmed_email: str):
        self.pubmed = PubMedRetriever(pubmed_email)
        try:
            self.vector_store = VectorStore()
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            self.vector_store = None
    
    def search_pubmed(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search PubMed and return article details"""
        logger.info(f"Searching PubMed for: {query}")
        pmids = self.pubmed.search(query, max_results)
        articles = self.pubmed.fetch_details(pmids)
        
        # Store in vector DB for future semantic searches
        if articles and self.vector_store:
            try:
                self.vector_store.add_documents(articles)
            except Exception as e:
                logger.error(f"Error adding articles to vector store: {e}")
        
        return articles
    
    def retrieve_context(self, query: str, k: int = 3) -> List[Dict]:
        """Retrieve context articles using semantic similarity or PubMed search"""
        logger.info(f"Retrieving context for: {query}")
        
        articles: List[Dict] = []
        
        # Try vector store first (semantic search)
        if self.vector_store:
            try:
                articles = self.vector_store.search(query, k=k)
                logger.info(f"Retrieved {len(articles)} articles from vector store")
            except Exception as e:
                logger.error(f"Vector store search failed: {e}")
        
        # Fallback to PubMed if vector store is empty or unavailable
        if not articles:
            logger.info("Falling back to PubMed search")
            pmids = self.pubmed.search(query, max_results=k)
            articles = self.pubmed.fetch_details(pmids)
        
        # Simplify for LLM context
        try:
            return [
                {
                    "pmid": article.get("pmid", ""),
                    "title": article.get("title", ""),
                    "summary": article.get("abstract", "")[:300]  # Truncated abstract
                }
                for article in articles
            ]
        except Exception as e:
            logger.error(f"Error simplifying context: {e}")
            return []
    
    def get_tool_names(self) -> List[str]:
        """Return available tool names"""
        return ["search_pubmed", "retrieve_context"]
