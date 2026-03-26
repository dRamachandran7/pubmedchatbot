import requests
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class PubMedClient:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, email: str):
        self.email = email
    
    def search(self, query: str, max_results: int = 10) -> List[str]:
        """Search PubMed and return PMIDs"""
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "rettype": "json",
            "email": self.email
        }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/esearch.fcgi",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            logger.error(f"PubMed search error: {e}")
            return []
    
    def fetch_articles(self, pmids: List[str]) -> List[Dict]:
        """Fetch article details for given PMIDs"""
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "rettype": "json",
            "email": self.email
        }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/efetch.fcgi",
                params=params
            )
            response.raise_for_status()
            return response.json().get("result", {}).get("uids", [])
        except Exception as e:
            logger.error(f"PubMed fetch error: {e}")
            return []
