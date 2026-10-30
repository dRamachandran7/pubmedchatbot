"""Fetch a fixed PubMed corpus for the retrieval eval and cache it to corpus.json.

The corpus is committed so eval results are reproducible; rerun this only to
rebuild it (and then re-check that every PMID in questions.json is still present).

Usage (from rag-service/):  python -m eval.build_corpus
"""
import json
import os
import time

from src.agent.pubmed_retriever import PubMedRetriever
from src.config.settings import settings

# Overlapping topics so that distractors are semantically close to the targets
TOPICS = [
    "metformin cardiovascular outcomes",
    "SGLT2 inhibitors heart failure",
    "GLP-1 receptor agonist weight loss",
    "statin primary prevention cardiovascular",
    "aspirin primary prevention",
    "CRISPR gene therapy sickle cell disease",
    "long COVID symptoms",
    "immune checkpoint inhibitors melanoma",
    "anti-amyloid antibody Alzheimer disease",
    "vitamin D supplementation randomized trial",
]
PER_TOPIC = 15
CORPUS_PATH = os.path.join(os.path.dirname(__file__), "corpus.json")


def main():
    retriever = PubMedRetriever(settings.PUBMED_EMAIL)
    corpus = {}
    for topic in TOPICS:
        # Only keep articles with an abstract, filtered at search time
        pmids = retriever.search(f"({topic}) AND hasabstract", PER_TOPIC)
        for article in retriever.fetch_details(pmids):
            if article and article.get("abstract"):
                article["pmid"] = str(article["pmid"])
                article["topic"] = topic
                corpus.setdefault(article["pmid"], article)
        time.sleep(0.5)  # stay under NCBI's unauthenticated rate limit
    with open(CORPUS_PATH, "w") as f:
        json.dump(list(corpus.values()), f, indent=1)
    print(f"Saved {len(corpus)} articles to {CORPUS_PATH}")


if __name__ == "__main__":
    main()
