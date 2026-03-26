# PubMed Chatbot - Hybrid RAG System

A full-stack agentic RAG (Retrieval-Augmented Generation) system for querying PubMed research articles. Built with TypeScript/Express backend and Python FastAPI RAG service.

## Architecture

- **Backend**: TypeScript Express API for handling chat requests
- **RAG Service**: Python FastAPI for retrieval, processing, and generation
- **Shared**: Common types and constants

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose (optional)

### Local Development

#### Backend Setup

```bash
cd backend
npm install
cp .env.example .env
npm run dev
```

#### RAG Service Setup

```bash
cd rag-service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python src/main.py
```

### Docker Deployment

```bash
cp .env.example .env
# Edit .env with your credentials
docker-compose up
```

## API Usage

### Chat Endpoint

```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest treatments for COVID-19?"}'
```

## Project Structure

See `/backend`, `/rag-service`, and `/shared` directories for detailed documentation.

## Environment Variables

Create a `.env` file at project root:

```
OPENAI_API_KEY=your_key
PUBMED_EMAIL=your_email@example.com
```

## Contributing

1. Create feature branches
2. Follow TypeScript/Python best practices
3. Add tests for new features
4. Submit pull requests

## License

MIT
