# PubMed Chatbot Frontend

A modern React-based frontend for the PubMed research chatbot.

## Setup

```bash
npm install
npm run dev
```

The app will be available at `http://localhost:3000`

## Project Structure

- `src/components/` - React components (ChatWindow, Message, ChatInput, MessageList)
- `src/styles/` - CSS stylesheets for each component
- `src/utils/` - Utility functions (for future API integration)

## Features

- Clean, modern chat interface
- Mock data for testing
- Responsive design
- Syntax highlighting for sources
- Auto-scrolling message list
- Loading states

## API Integration

Currently using mock data. To connect to the backend:
1. Create `src/services/api.js` with API calls
2. Replace mock responses in `ChatWindow.jsx` with real API calls
3. Update environment variables in `.env`
