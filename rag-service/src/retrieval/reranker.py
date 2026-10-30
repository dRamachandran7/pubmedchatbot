import logging
from typing import List
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", max_length: int = 512):
        """Cross-encoder that scores (query, passage) pairs jointly for reranking"""
        self.model = CrossEncoder(model_name, max_length=max_length)
        logger.info(f"Loaded reranker model: {model_name}")

    def score(self, query: str, passages: List[str]) -> List[float]:
        """Return a relevance score per passage; higher is more relevant"""
        if not passages:
            return []
        scores = self.model.predict([(query, p) for p in passages], batch_size=32)
        return [float(s) for s in scores]
