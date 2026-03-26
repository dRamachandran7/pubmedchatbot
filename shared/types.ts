export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: number;
}

export interface PubMedArticle {
  pmid: string;
  title: string;
  abstract: string;
  authors: string[];
  publicationDate: string;
  relevanceScore?: number;
}

export interface AgentConfig {
  maxRetries: number;
  timeout: number;
  temperature: number;
}
