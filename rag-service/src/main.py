from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
from .agent.agent import RAGAgent
from .config.settings import settings

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(title="PubMed RAG Service")
agent = RAGAgent()

class ChatRequest(BaseModel):
    query: str
    sessionId: Optional[str] = None
    conversationHistory: Optional[List[dict]] = None

class ChatResponse(BaseModel):
    message: str
    sources: List[dict]
    conversationId: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat requests"""
    try:
        response = agent.process_query(request.query, request.sessionId)
        return ChatResponse(**response)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation history"""
    return {"sessionId": session_id, "messages": []}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
