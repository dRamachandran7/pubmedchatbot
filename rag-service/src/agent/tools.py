import logging
from typing import List, Dict
from .pubmed_retriever import PubMedRetriever

logger = logging.getLogger(__name__)

class RAGTools:
    def __init__(self, pubmed_email: str):
        self.pubmed = PubMedRetriever(pubmed_email)
    
    def search_pubmed(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search PubMed and return article details"""
        logger.info(f"Searching PubMed for: {query}")
        pmids = self.pubmed.search(query, max_results)
        return self.pubmed.fetch_details(pmids)
    
    def retrieve_context(self, query: str, k: int = 3) -> List[Dict]:
        """Retrieve context articles for RAG"""
        logger.info(f"Retrieving context for: {query}")
        pmids = self.pubmed.search(query, max_results=k)
        return self.pubmed.fetch_details(pmids)
    
    def get_tool_names(self) -> List[str]:
        """Return available tool names"""
        return ["search_pubmed", "retrieve_context"]
