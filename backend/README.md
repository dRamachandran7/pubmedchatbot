# PubMed Chatbot - Backend Service

TypeScript Express API that handles chat requests and integrates with the Python RAG service.

## Setup

```bash
npm install
```

## Development

```bash
npm run dev
```

## Build

```bash
npm run build
npm start
```

## Environment Variables

Copy `.env.example` to `.env` and update values:

```
PORT=3000
PYTHON_RAG_SERVICE_URL=http://localhost:5000
```

## API Endpoints

- `POST /api/chat` - Send a chat query
- `GET /api/conversation/:sessionId` - Get conversation history
