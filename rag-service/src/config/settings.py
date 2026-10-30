import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "dhruva.ramachandran@gmail.com")
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./data/vectors")
    # Cross-encoder used to rerank vector search hits; set empty to disable
    RERANKER_MODEL = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Service configuration
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "0.0.0.0")

settings = Settings()
