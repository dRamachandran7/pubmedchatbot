import logging
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb
from .document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, embeddings_model: str = "all-MiniLM-L6-v2", db_path: str = "./data/chroma"):
        """Initialize vector store with embeddings model and Chroma DB"""
        try:
            # Load embeddings model
            self.embeddings_model = SentenceTransformer(embeddings_model)
            logger.info(f"Loaded embeddings model: {embeddings_model}")
            
            # Size chunks with the model's own tokenizer, leaving headroom
            # under its max sequence length for special tokens
            tokenizer = self.embeddings_model.tokenizer
            max_seq_length = self.embeddings_model.max_seq_length
            self.processor = DocumentProcessor(
                max_tokens=max_seq_length - 16,
                count_tokens=lambda text: len(tokenizer.tokenize(text))
            )
            
            # Initialize Chroma client with persistent storage
            self.chroma_client = chromadb.PersistentClient(path=db_path)
            self.collection = self.chroma_client.get_or_create_collection(
                name="pubmed_chunks",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Initialized Chroma collection at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def add_documents(self, documents: List[Dict]) -> None:
        """Chunk documents by abstract structure and add the chunks to the store"""
        try:
            ids = []
            texts = []
            metadatas = []
            
            for doc in documents:
                pmid = str(doc.get("pmid", "unknown"))
                for chunk in self.processor.chunk_article(doc):
                    # One record per chunk, keyed by PMID + position
                    ids.append(f"pubmed_{pmid}_{chunk['chunk_index']}")
                    texts.append(chunk["embed_text"])
                    metadatas.append({
                        "pmid": pmid,
                        "title": str(doc.get("title", "")),
                        "journal": str(doc.get("journal", "")),
                        "pub_date": str(doc.get("pub_date", "")),
                        "authors": ",".join(doc.get("authors", [])),
                        "section": chunk["section"],
                        "chunk_index": chunk["chunk_index"],
                        "chunk_text": chunk["text"]
                    })
            
            if not ids:
                return
            
            # Generate embeddings
            embeddings = self.embeddings_model.encode(texts, convert_to_numpy=True)
            
            # Upsert so re-fetching an article doesn't fail on duplicate IDs
            self.collection.upsert(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(ids)} chunks from {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
    
    def search(self, query: str, k: int = 5, chunks_per_article: int = 2) -> List[Dict]:
        """Search chunks by semantic similarity and group the hits by article"""
        try:
            # Generate query embedding
            query_embedding = self.embeddings_model.encode(query, convert_to_numpy=True)
            
            # Over-fetch chunks, since several may belong to the same article
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=k * 4
            )
            
            articles: List[Dict] = []
            if not results:
                return articles
            
            metadatas_raw = results.get("metadatas")
            metadatas = metadatas_raw[0] if metadatas_raw and len(metadatas_raw) > 0 else []
            
            distances_raw = results.get("distances")
            distances = distances_raw[0] if distances_raw and len(distances_raw) > 0 else []
            
            # Results come back nearest-first, so the first hit per PMID is its best
            by_pmid: Dict[str, Dict] = {}
            for i, metadata in enumerate(metadatas):
                if not isinstance(metadata, dict):
                    continue
                pmid = metadata.get("pmid", "")
                # Chroma returns cosine distance; convert to similarity
                similarity = 1.0 - float(distances[i]) if i < len(distances) else 0.0
                if pmid not in by_pmid:
                    if len(by_pmid) >= k:
                        continue
                    by_pmid[pmid] = {
                        "pmid": pmid,
                        "title": metadata.get("title", ""),
                        "journal": metadata.get("journal", ""),
                        "similarity_score": similarity,
                        "chunks": []
                    }
                article = by_pmid[pmid]
                if len(article["chunks"]) < chunks_per_article:
                    article["chunks"].append({
                        "section": metadata.get("section", ""),
                        "chunk_index": metadata.get("chunk_index", 0),
                        "text": metadata.get("chunk_text", "")
                    })
            
            for article in by_pmid.values():
                # Present matched chunks in abstract order
                article["chunks"].sort(key=lambda c: c["chunk_index"])
                article["abstract"] = " ".join(c["text"] for c in article["chunks"])
                articles.append(article)
            
            logger.info(f"Vector search returned {len(articles)} articles for query: {query[:50]}")
            return articles
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def save(self, path: str) -> None:
        """Persist vector store to disk"""
        try:
            # PersistentClient automatically persists data
            logger.info(f"Vector store data persisted to {path}")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
    
    def load(self, path: str) -> None:
        """Load vector store from disk"""
        logger.info(f"Vector store loaded from {path}")
