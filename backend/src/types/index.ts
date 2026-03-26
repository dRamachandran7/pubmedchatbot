export interface ChatRequest {
  query: string;
  sessionId?: string;
  conversationHistory?: Message[];
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  message: string;
  sources?: Source[];
  conversationId: string;
}

export interface Source {
  title: string;
  pmid: string;
  relevance: number;
  excerpt: string;
}

export interface ErrorResponse {
  error: string;
  statusCode: number;
}
