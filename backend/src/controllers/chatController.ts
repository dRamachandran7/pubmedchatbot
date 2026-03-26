import { Request, Response, NextFunction } from 'express';
import axios from 'axios';
import { ChatRequest, ChatResponse } from '../types';
import { AppError } from '../middleware/errorHandler';

const RAG_SERVICE_URL = process.env.PYTHON_RAG_SERVICE_URL || 'http://localhost:5000';

export const handleChat = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { query, sessionId, conversationHistory } = req.body as ChatRequest;

    if (!query) {
      throw new AppError(400, 'Query is required');
    }

    const ragResponse = await axios.post(`${RAG_SERVICE_URL}/chat`, {
      query,
      sessionId,
      conversationHistory
    });

    const chatResponse: ChatResponse = ragResponse.data;
    res.status(200).json(chatResponse);
  } catch (error) {
    if (axios.isAxiosError(error)) {
      next(new AppError(error.response?.status || 502, error.message));
    } else {
      next(error);
    }
  }
};

export const getConversationHistory = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { sessionId } = req.params;
    const history = await axios.get(
      `${RAG_SERVICE_URL}/conversation/${sessionId}`
    );
    res.status(200).json(history.data);
  } catch (error) {
    next(error);
  }
};
