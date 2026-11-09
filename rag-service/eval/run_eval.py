"""Retrieval eval: compare chunking strategies on a fixed PubMed corpus.

Strategies (all use all-MiniLM-L6-v2 and exact cosine search, so only the
chunking differs):
  whole_doc        one vector per article (title + abstract), LLM context is
                   the first 300 chars of the abstract -- the previous pipeline
  whole_doc_full   same retrieval, but the full abstract goes to the LLM
                   (reference point: maximum context, no chunking)
  fixed_size       512-char windows with 50-char overlap
  section          section-based chunking via DocumentProcessor (current)
  *+<reranker>     the same, with the top RERANK_CANDIDATES chunks reordered
                   by a cross-encoder before grouping into articles
plus `section_chroma*`, the production VectorStore (Chroma HNSW) end to end.

Metrics, over questions labelled with a gold PMID and verbatim evidence:
  hit@1, hit@3     gold article ranked first / in the top 3
  mrr@10           mean reciprocal rank of the gold article
  ctx_hit@3        gold article in the top 3 AND the text handed to the LLM
                   for it contains the evidence -- i.e. the answer reached the LLM
  ctx_words        mean words of context sent to the LLM per query (top 3)
  ms/query         mean search latency (includes reranking; machine-dependent)

Usage (from rag-service/):  python -m eval.run_eval
"""
import json
import os
import re
import tempfile
import time
from typing import Callable, Dict, List

import numpy as np

from src.retrieval.reranker import Reranker
from src.retrieval.vector_store import VectorStore

EVAL_DIR = os.path.dirname(__file__)
TOP_K = 10
CHUNKS_PER_ARTICLE = 2  # matches VectorStore.search default
RERANK_CANDIDATES = 50  # matches VectorStore default
RERANKERS = {
    "minilm": "cross-encoder/ms-marco-MiniLM-L-6-v2",
    "medcpt": "ncbi/MedCPT-Cross-Encoder",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def contains_evidence(text: str, evidence: List[str]) -> bool:
    text = normalize(text)
    return any(normalize(e) in text for e in evidence)


def fixed_size_chunks(article: Dict, size: int = 512, overlap: int = 50) -> List[Dict]:
    text = article.get("abstract", "")
    return [
        {"text": text[i:i + size], "embed_text": text[i:i + size], "chunk_index": n}
        for n, i in enumerate(range(0, len(text), size - overlap))
    ]


def whole_doc_chunks(article: Dict) -> List[Dict]:
    text = f"{article.get('title', '')} {article.get('abstract', '')}"
    return [{"text": article.get("abstract", ""), "embed_text": text, "chunk_index": 0}]


class ExactIndex:
    """Embed every chunk, rank by cosine, regroup hits by article."""

    def __init__(self, model, corpus: List[Dict], chunker: Callable[[Dict], List[Dict]]):
        self.model = model
        self.chunks = []
        for article in corpus:
            for chunk in chunker(article):
                self.chunks.append({**chunk, "pmid": article["pmid"]})
        self.embeddings = model.encode(
            [c["embed_text"] for c in self.chunks], normalize_embeddings=True,
            convert_to_numpy=True, batch_size=64)

    def search(self, query: str, k: int, reranker: Reranker = None) -> List[Dict]:
        q = self.model.encode(query, normalize_embeddings=True, convert_to_numpy=True)
        # macOS Accelerate emits spurious matmul overflow warnings; scores are finite
        with np.errstate(all="ignore"):
            order = list(np.argsort(-(self.embeddings @ q)))
        if reranker:
            candidates = order[:RERANK_CANDIDATES]
            scores = reranker.score(query, [self.chunks[i]["embed_text"] for i in candidates])
            order = [i for _, i in sorted(zip(scores, candidates), key=lambda p: -p[0])]
        by_pmid: Dict[str, Dict] = {}
        for idx in order:
            chunk = self.chunks[idx]
            pmid = chunk["pmid"]
            if pmid not in by_pmid:
                if len(by_pmid) >= k:
                    continue
                by_pmid[pmid] = {"pmid": pmid, "chunks": []}
            if len(by_pmid[pmid]["chunks"]) < CHUNKS_PER_ARTICLE:
                by_pmid[pmid]["chunks"].append(chunk)
        results = []
        for article in by_pmid.values():
            article["chunks"].sort(key=lambda c: c["chunk_index"])
            article["context"] = " ".join(c["text"] for c in article["chunks"])
            results.append(article)
        return results


def score(name: str, questions: List[Dict], search: Callable[[str], List[Dict]],
          context_of: Callable[[Dict], str]) -> Dict:
    rows = []
    elapsed = 0.0
    for q in questions:
        start = time.perf_counter()
        results = search(q["question"])
        elapsed += time.perf_counter() - start
        ranked = [r["pmid"] for r in results]
        rank = ranked.index(q["pmid"]) + 1 if q["pmid"] in ranked else None
        top3 = results[:3]
        gold = next((r for r in top3 if r["pmid"] == q["pmid"]), None)
        rows.append({
            "id": q["id"],
            "rank": rank,
            "ctx_hit": bool(gold and contains_evidence(context_of(gold), q["evidence"])),
            "ctx_words": sum(len(context_of(r).split()) for r in top3),
        })
    n = len(rows)
    return {
        "strategy": name,
        "hit@1": sum(r["rank"] == 1 for r in rows) / n,
        "hit@3": sum(bool(r["rank"]) and r["rank"] <= 3 for r in rows) / n,
        "mrr@10": sum(1 / r["rank"] for r in rows if r["rank"]) / n,
        "ctx_hit@3": sum(r["ctx_hit"] for r in rows) / n,
        "ctx_words": sum(r["ctx_words"] for r in rows) / n,
        "ms_per_query": 1000 * elapsed / n,
        "per_question": rows,
    }


def main():
    with open(os.path.join(EVAL_DIR, "corpus.json")) as f:
        corpus = json.load(f)
    with open(os.path.join(EVAL_DIR, "questions.json")) as f:
        questions = json.load(f)

    # Fail loudly on bad labels rather than silently scoring them as misses
    by_pmid = {a["pmid"]: a for a in corpus}
    for q in questions:
        assert q["pmid"] in by_pmid, f"{q['id']}: PMID {q['pmid']} not in corpus"
        assert contains_evidence(by_pmid[q["pmid"]]["abstract"], q["evidence"]), \
            f"{q['id']}: evidence not found in abstract of {q['pmid']}"

    with tempfile.TemporaryDirectory() as db_path:
        rerankers = {name: Reranker(model) for name, model in RERANKERS.items()}
        store = VectorStore(db_path=db_path)
        model, processor = store.embeddings_model, store.processor
        print(f"Corpus: {len(corpus)} articles, {len(questions)} questions\n")

        whole = ExactIndex(model, corpus, whole_doc_chunks)
        fixed = ExactIndex(model, corpus, fixed_size_chunks)
        section = ExactIndex(model, corpus, processor.chunk_article)
        store.add_documents(corpus)

        results = [
            score("whole_doc", questions, lambda q: whole.search(q, TOP_K),
                  lambda r: by_pmid[r["pmid"]]["abstract"][:300]),
            score("whole_doc_full", questions, lambda q: whole.search(q, TOP_K),
                  lambda r: by_pmid[r["pmid"]]["abstract"]),
            score("fixed_size", questions, lambda q: fixed.search(q, TOP_K),
                  lambda r: r["context"]),
            score("section", questions, lambda q: section.search(q, TOP_K),
                  lambda r: r["context"]),
            score("section_chroma", questions, lambda q: store.search(q, k=TOP_K),
                  lambda r: r["abstract"]),
        ]
        for name, reranker in rerankers.items():
            results += [
                score(f"fixed_size+{name}", questions,
                      lambda q: fixed.search(q, TOP_K, reranker), lambda r: r["context"]),
                score(f"section+{name}", questions,
                      lambda q: section.search(q, TOP_K, reranker), lambda r: r["context"]),
            ]
        # Production path with each reranker plugged into the real VectorStore
        for name, reranker in rerankers.items():
            store.reranker = reranker
            results.append(score(f"section_chroma+{name}", questions,
                                 lambda q: store.search(q, k=TOP_K), lambda r: r["abstract"]))

    chunk_counts = {"whole_doc": len(whole.chunks), "fixed_size": len(fixed.chunks),
                    "section": len(section.chunks)}
    print(f"Chunks indexed: {chunk_counts}\n")
    header = f"{'strategy':<24}{'hit@1':>8}{'hit@3':>8}{'mrr@10':>8}{'ctx_hit@3':>11}{'ctx_words':>11}{'ms/query':>10}"
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['strategy']:<24}{r['hit@1']:>8.2f}{r['hit@3']:>8.2f}{r['mrr@10']:>8.2f}"
              f"{r['ctx_hit@3']:>11.2f}{r['ctx_words']:>11.0f}{r['ms_per_query']:>10.0f}")

    out_path = os.path.join(EVAL_DIR, "results.json")
    with open(out_path, "w") as f:
        json.dump({"chunks_indexed": chunk_counts, "results": results}, f, indent=1)
    print(f"\nPer-question results written to {out_path}")


if __name__ == "__main__":
    main()
