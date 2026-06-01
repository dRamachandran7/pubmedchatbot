
import { Request, Response, NextFunction } from 'express';
import axios from 'axios';
import { ChatRequest, ChatResponse } from '../types';
import { AppError } from '../middleware/errorHandler';

const RAG_SERVICE_URL = process.env.PYTHON_RAG_SERVICE_URL || 'http://localhost:8000';

const logger = console;

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

    logger.log('=== CHAT REQUEST ===');
    logger.log(`RAG Service URL: ${RAG_SERVICE_URL}`);
    logger.log(`Query: ${query}`);
    logger.log(`Session ID: ${sessionId}`);
    logger.log('Sending request to RAG service...');

    const ragResponse = await axios.post(`${RAG_SERVICE_URL}/chat`, {
      query,
      sessionId,
      conversationHistory
    });

    logger.log('=== RAG SERVICE RESPONSE ===');
    logger.log('Status:', ragResponse.status);
    logger.log('Data:', JSON.stringify(ragResponse.data, null, 2));

    const chatResponse: ChatResponse = ragResponse.data;
    logger.log('Sending response to frontend:', JSON.stringify(chatResponse, null, 2));
    res.status(200).json(chatResponse);
  } catch (error) {
    logger.error('=== ERROR IN CHAT REQUEST ===');
    if (axios.isAxiosError(error)) {
      logger.error(`Axios Error: ${error.message}`);
      logger.error(`Status: ${error.response?.status}`);
      logger.error(`Response data:`, error.response?.data);
      next(new AppError(error.response?.status || 502, error.message));
    } else {
      logger.error(`Error:`, error);
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
    if (axios.isAxiosError(error)) {
      next(new AppError(error.response?.status || 502, error.message));
    } else {
      next(error);
    }
  }
};
