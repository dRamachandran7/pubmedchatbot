from Bio import Entrez
import logging
import re
from typing import List, Dict

logger = logging.getLogger(__name__)

# Some publishers send structured abstracts as one unlabelled block with
# inline bold headings, e.g. "<b>Background/Objectives:</b> ..."
_INLINE_HEADING = re.compile(r"<b>\s*([^<]{1,60}?)\s*:?\s*</b>\s*:?")
_TAG = re.compile(r"<[^>]+>")


def _strip_tags(text: str) -> str:
    return re.sub(r"\s+", " ", _TAG.sub("", text)).strip()


def _split_inline_headings(text: str) -> List[Dict]:
    """Split an unlabelled abstract on inline bold headings, if it has any."""
    parts = _INLINE_HEADING.split(text)
    # parts = [preamble, label1, body1, label2, body2, ...]
    if len(parts) < 3:
        return [{"label": "", "text": _strip_tags(text)}]
    sections = []
    if _strip_tags(parts[0]):
        sections.append({"label": "", "text": _strip_tags(parts[0])})
    for label, body in zip(parts[1::2], parts[2::2]):
        if _strip_tags(body):
            sections.append({"label": label.strip().title(), "text": _strip_tags(body)})
    return sections

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
            
            abstract_sections = self._get_abstract_sections(article_info)
            return {
                "pmid": medline["PMID"],
                "title": article_info.get("ArticleTitle", ""),
                "abstract": " ".join(s["text"] for s in abstract_sections),
                "abstract_sections": abstract_sections,
                "authors": self._get_authors(article_info),
                "journal": article_info.get("Journal", {}).get("Title", ""),
                "pub_date": self._get_pub_date(article_info)
            }
        except Exception as e:
            logger.error(f"Error parsing article: {e}")
            return {}
    
    def _get_abstract_sections(self, article: Dict) -> List[Dict]:
        """Extract abstract sections, keeping structured-abstract labels.

        Structured abstracts carry a Label attribute (e.g. "METHODS") on each
        AbstractText element; unstructured ones have a single unlabelled element.
        """
        abstract = article.get("Abstract", {})
        if not isinstance(abstract, dict):
            return []
        sections = []
        for s in abstract.get("AbstractText", []):
            text = str(s).strip()
            if not text:
                continue
            label = getattr(s, "attributes", {}).get("Label", "")
            if label:
                sections.append({"label": label.strip().title(), "text": _strip_tags(text)})
            else:
                sections.extend(_split_inline_headings(text))
        return sections
    
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
