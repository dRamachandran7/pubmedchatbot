import logging
from typing import List

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.overlap):
            chunk = text[i:i + self.chunk_size]
            chunks.append(chunk)
        return chunks
    
    def process_pubmed_article(self, article: dict) -> dict:
        """Process a PubMed article into structured format"""
        processed = {
            "pmid": article.get("pmid", ""),
            "title": article.get("title", ""),
            "abstract": article.get("abstract", ""),
            "authors": article.get("authors", []),
            "publication_date": article.get("publication_date", ""),
            "chunks": []
        }
        
        # Chunk the abstract
        abstract_text = processed["abstract"]
        if abstract_text:
            processed["chunks"] = self.chunk_text(abstract_text)
        
        return processed
    
    def process_batch(self, articles: List[dict]) -> List[dict]:
        """Process multiple articles"""
        return [self.process_pubmed_article(article) for article in articles]
