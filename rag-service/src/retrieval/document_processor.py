import logging
import re
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# Sentence boundary: terminal punctuation followed by whitespace and an uppercase
# letter, digit or opening bracket. Skips common abbreviations ("e.g.", "et al.").
_ABBREVIATIONS = r"(?<!\be\.g)(?<!\bi\.e)(?<!\bet al)(?<!\bvs)(?<!\bFig)(?<!\bapprox)"
_SENTENCE_BOUNDARY = re.compile(_ABBREVIATIONS + r"(?<=[.!?])\s+(?=[A-Z0-9(\[])")


def _whitespace_token_count(text: str) -> int:
    return len(text.split())


class DocumentProcessor:
    """Structure-aware chunker for PubMed abstracts.

    Structured abstracts (Background/Methods/Results/Conclusions) are split on
    their section labels. Sections that are too small are merged with the next
    one; sections that are too large are split on sentence boundaries with a
    one-sentence overlap. Unstructured abstracts get the same sentence-based
    treatment as a single section. Every chunk is prefixed with the article
    title so it stays interpretable on its own.
    """

    def __init__(
        self,
        max_tokens: int = 200,
        min_tokens: int = 40,
        overlap_sentences: int = 1,
        count_tokens: Optional[Callable[[str], int]] = None,
    ):
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens
        self.overlap_sentences = overlap_sentences
        self.count_tokens = count_tokens or _whitespace_token_count

    def split_sentences(self, text: str) -> List[str]:
        return [s.strip() for s in _SENTENCE_BOUNDARY.split(text) if s.strip()]

    def _split_long_sentence(self, sentence: str, budget: int) -> List[str]:
        """Last resort for a single sentence over budget: split on words."""
        pieces, current = [], []
        for word in sentence.split():
            if current and self.count_tokens(" ".join(current + [word])) > budget:
                pieces.append(" ".join(current))
                current = []
            current.append(word)
        if current:
            pieces.append(" ".join(current))
        return pieces

    def _pack_sentences(self, text: str, budget: int) -> List[str]:
        """Group sentences into chunks under budget, overlapping by N sentences."""
        sentences: List[str] = []
        for sentence in self.split_sentences(text):
            if self.count_tokens(sentence) > budget:
                sentences.extend(self._split_long_sentence(sentence, budget))
            else:
                sentences.append(sentence)

        chunks: List[str] = []
        current: List[str] = []
        for sentence in sentences:
            if current and self.count_tokens(" ".join(current + [sentence])) > budget:
                chunks.append(" ".join(current))
                overlap = current[-self.overlap_sentences:] if self.overlap_sentences else []
                # Drop the overlap if it would push the next chunk over budget
                if overlap and self.count_tokens(" ".join(overlap + [sentence])) > budget:
                    overlap = []
                current = overlap
            current.append(sentence)
        if current:
            chunks.append(" ".join(current))
        return chunks

    @staticmethod
    def _labelled_text(section: Dict) -> str:
        """Section text with its label inline (merged sections already have it)."""
        if section.get("labelled"):
            return section["text"]
        return f"{section['label']}: {section['text']}"

    def _combine(self, first: Dict, second: Dict) -> Dict:
        return {
            "label": f"{first['label']} / {second['label']}",
            "text": f"{self._labelled_text(first)} {self._labelled_text(second)}",
            "labelled": True,
        }

    def _merge_small_sections(self, sections: List[Dict]) -> List[Dict]:
        """Fold sections under min_tokens into the following section."""
        merged: List[Dict] = []
        pending: Optional[Dict] = None
        for section in sections:
            if pending:
                section = self._combine(pending, section)
                pending = None
            if self.count_tokens(section["text"]) < self.min_tokens:
                pending = section
            else:
                merged.append(section)
        if pending:
            # A trailing small section joins the previous one, or stands alone
            if merged:
                merged[-1] = self._combine(merged[-1], pending)
            else:
                merged.append(pending)
        return merged

    def chunk_article(self, article: Dict) -> List[Dict]:
        """Split an article into chunks with text ready for embedding."""
        title = str(article.get("title", "")).strip()
        sections = [
            {"label": s.get("label") or "Abstract", "text": str(s.get("text", "")).strip()}
            for s in article.get("abstract_sections") or []
            if str(s.get("text", "")).strip()
        ]
        if not sections and article.get("abstract"):
            sections = [{"label": "Abstract", "text": str(article["abstract"]).strip()}]

        if not sections:
            # No abstract: embed the title alone so the article is still findable
            return [{"section": "Title", "text": title, "embed_text": title, "chunk_index": 0}] if title else []

        if len(sections) > 1:
            sections = self._merge_small_sections(sections)

        header = f"{title}\n" if title else ""
        budget = max(self.max_tokens - self.count_tokens(header), self.min_tokens)

        chunks: List[Dict] = []
        for section in sections:
            prefix = "" if section.get("labelled") else f"{section['label']}: "
            for text in self._pack_sentences(section["text"], budget - self.count_tokens(prefix)):
                chunks.append({
                    "section": section["label"],
                    "text": f"{prefix}{text}",
                    "embed_text": f"{header}{prefix}{text}",
                    "chunk_index": len(chunks),
                })
        return chunks
