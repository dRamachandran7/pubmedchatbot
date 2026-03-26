# PubMed RAG Service

Python-based RAG (Retrieval-Augmented Generation) service for retrieving and processing PubMed articles.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running

```bash
python src/main.py
```

The service will start on `http://localhost:5000`

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```
OPENAI_API_KEY=your_key
PUBMED_EMAIL=your_email@example.com
```

## API Endpoints

- `POST /chat` - Send a chat query
- `GET /conversation/{session_id}` - Get conversation history
- `GET /health` - Health check
