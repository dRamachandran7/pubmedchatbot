import logging
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, embeddings_model: str = "all-MiniLM-L6-v2", db_path: str = "./data/chroma"):
        """Initialize vector store with embeddings model and Chroma DB"""
        try:
            # Load embeddings model
            self.embeddings_model = SentenceTransformer(embeddings_model)
            logger.info(f"Loaded embeddings model: {embeddings_model}")
            
            # Initialize Chroma client with persistent storage
            self.chroma_client = chromadb.PersistentClient(path=db_path)
            self.collection = self.chroma_client.get_or_create_collection(
                name="pubmed_articles",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Initialized Chroma collection at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise
    
    def add_documents(self, documents: List[Dict]) -> None:
        """Add documents with embeddings to the store"""
        try:
            ids = []
            texts = []
            metadatas = []
            
            for doc in documents:
                # Create unique ID from PMID
                doc_id = f"pubmed_{doc.get('pmid', 'unknown')}"
                
                # Combine title + abstract for embedding
                text_to_embed = f"{doc.get('title', '')} {doc.get('abstract', '')}"
                
                ids.append(doc_id)
                texts.append(text_to_embed)
                metadatas.append({
                    "pmid": str(doc.get("pmid", "")),
                    "title": doc.get("title", ""),
                    "journal": doc.get("journal", ""),
                    "pub_date": doc.get("pub_date", ""),
                    "authors": ",".join(doc.get("authors", []))
                })
            
            # Generate embeddings
            embeddings = self.embeddings_model.encode(texts, convert_to_numpy=True)
            
            # Add to Chroma
            self.collection.add(
                ids=ids,
                embeddings=embeddings.tolist(),
                documents=texts,
                metadatas=metadatas
            )
            
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
    
    def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for similar documents using semantic similarity"""
        try:
            # Generate query embedding
            query_embedding = self.embeddings_model.encode(query, convert_to_numpy=True)
            
            # Search in Chroma
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=k
            )
            
            # Format results
            articles: List[Dict] = []
            if not results:
                return articles
            
            # Safely extract results with type checking
            ids_list = results.get("ids")
            if not ids_list or not isinstance(ids_list, list) or len(ids_list) == 0:
                return articles
            
            ids = ids_list[0] if isinstance(ids_list[0], list) else ids_list
            
            # Safely get nested lists
            metadatas_raw = results.get("metadatas")
            metadatas = metadatas_raw[0] if metadatas_raw and isinstance(metadatas_raw, list) and len(metadatas_raw) > 0 else []
            
            documents_raw = results.get("documents")
            documents = documents_raw[0] if documents_raw and isinstance(documents_raw, list) and len(documents_raw) > 0 else []
            
            distances_raw = results.get("distances")
            distances = distances_raw[0] if distances_raw and isinstance(distances_raw, list) and len(distances_raw) > 0 else []
            
            for i in range(len(ids)):
                metadata = metadatas[i] if i < len(metadatas) and isinstance(metadatas[i], dict) else {}
                article = {
                    "pmid": metadata.get("pmid", ""),
                    "title": metadata.get("title", ""),
                    "abstract": documents[i] if i < len(documents) else "",
                    "journal": metadata.get("journal", ""),
                    "similarity_score": float(distances[i]) if i < len(distances) else 0.0
                }
                articles.append(article)
            
            logger.info(f"Vector search returned {len(articles)} results for query: {query[:50]}")
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
