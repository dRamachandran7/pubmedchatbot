from Bio import Entrez
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class PubMedRetriever:
    def __init__(self, email: str):
        """Initialize PubMed retriever with required email for NCBI"""
        self.email = email
        Entrez.email = email
        Entrez.tool = "PubMedChatbot/1.0"
    
    def search(self, query: str, max_results: int = 5) -> List[str]:
        """Search PubMed and return PMIDs"""
        try:
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            record = Entrez.read(handle)
            handle.close()
            return record["IdList"]
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return []
    
    def fetch_details(self, pmids: List[str]) -> List[Dict]:
        """Fetch full details for given PMIDs"""
        try:
            handle = Entrez.efetch(db="pubmed", id=",".join(pmids), rettype="xml")
            records = Entrez.read(handle)
            handle.close()
            
            articles = []
            for article in records["PubmedArticle"]:
                article_data = self._parse_article(article)
                articles.append(article_data)
            return articles
        except Exception as e:
            logger.error(f"Failed to fetch PubMed details: {e}")
            return []
    
    def _parse_article(self, article: Dict) -> Dict:
        """Parse PubMed article XML into structured format"""
        try:
            medline = article["MedlineCitation"]
            article_info = medline["Article"]
            
            return {
                "pmid": medline["PMID"],
                "title": article_info.get("ArticleTitle", ""),
                "abstract": self._get_abstract(article_info),
                "authors": self._get_authors(article_info),
                "journal": article_info.get("Journal", {}).get("Title", ""),
                "pub_date": self._get_pub_date(article_info)
            }
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return {}
    
    def _get_abstract(self, article: Dict) -> str:
        """Extract abstract text from article"""
        abstract = article.get("Abstract", {})
        if isinstance(abstract, dict):
            sections = abstract.get("AbstractText", [])
            if sections:
                return " ".join([str(s) for s in sections])
        return ""
    
    def _get_authors(self, article: Dict) -> List[str]:
        """Extract author names from article"""
        authors = []
        author_list = article.get("AuthorList", [])
        for author in author_list[:3]:  # Limit to first 3 authors
            if "LastName" in author:
                authors.append(author["LastName"])
        return authors
    
    def _get_pub_date(self, article: Dict) -> str:
        """Extract publication date from article"""
        pub_date = article.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
        year = pub_date.get("Year", "")
        month = pub_date.get("Month", "")
        return f"{year}-{month}" if year else year
