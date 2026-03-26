import { Router } from 'express';
import { handleChat, getConversationHistory } from '../controllers/chatController';

const router = Router();

router.post('/chat', handleChat);
router.get('/conversation/:sessionId', getConversationHistory);

export default router;
