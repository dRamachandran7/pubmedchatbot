import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dhruva.ramachandran@gmail.com")
    PUBMED_EMAIL = os.getenv("PUBMED_EMAIL", "your-email@example.com")
    VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", "./data/vectors")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Service configuration
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "0.0.0.0")

settings = Settings()
