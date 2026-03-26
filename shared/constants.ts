export const API_ENDPOINTS = {
  CHAT: '/api/chat',
  CONVERSATION: '/api/conversation',
  HEALTH: '/health'
};

export const HTTP_STATUS = {
  OK: 200,
  BAD_REQUEST: 400,
  INTERNAL_ERROR: 500,
  SERVICE_UNAVAILABLE: 503
};

export const DEFAULT_CONFIG = {
  MAX_RESULTS: 10,
  CHUNK_SIZE: 512,
  OVERLAP: 50,
  RETRIEVAL_K: 5
};
