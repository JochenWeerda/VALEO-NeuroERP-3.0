import express from 'express';
// @ts-ignore
import cors from 'cors';
// @ts-ignore
import helmet from 'helmet';
// @ts-ignore
import compression from 'compression';
// @ts-ignore
import morgan from 'morgan';
// @ts-ignore
import { createServer } from 'http';
// @ts-ignore
import { Server } from 'socket.io';

import { LogisticsDashboardService, RealtimeUpdate } from './services/dashboard-service';
import { VoiceChatService, ChatMessage } from './services/voice-chat-service';
import { DispatchActionService, DispatchAction, QuickAction } from './services/dispatch-action-service';

const app = express();
const server = createServer(app);
// @ts-ignore
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

app.use(cors());
app.use(helmet());
// @ts-ignore
app.use(compression());
app.use(morgan('combined'));
app.use(express.json());

// Initialize services
const dashboardService = new LogisticsDashboardService();
const voiceChatService = new VoiceChatService();
const dispatchActionService = new DispatchActionService();

// Socket.IO connection handling for real-time updates
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  // Subscribe to dashboard updates
  const unsubscribe = dashboardService.subscribe((update: RealtimeUpdate) => {
    socket.emit('dashboard_update', update);
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
    unsubscribe();
  });

  // Handle chat messages
  socket.on('chat_message', async (data: { userId: string; message: string }) => {
    try {
      const response = await voiceChatService.processChatMessage(data.message, data.userId);
      socket.emit('chat_response', response);
    } catch (error) {
      socket.emit('chat_error', { message: 'Failed to process message' });
    }
  });

  // Handle voice commands
  socket.on('voice_command', async (data: { audioData: Buffer; tenantId: string }) => {
    try {
      const command = await voiceChatService.processVoiceCommand(data.audioData, data.tenantId);
      socket.emit('voice_response', command);
    } catch (error) {
      socket.emit('voice_error', { message: 'Failed to process voice command' });
    }
  });
});

// REST API Endpoints

// Dashboard endpoints
app.get('/api/dashboard/metrics/:tenantId', (req, res) => {
  const metrics = dashboardService.getMetrics(req.params.tenantId);
  res.json(metrics);
});

// Chat endpoints
app.post('/api/chat/message', async (req, res) => {
  try {
    const { message, userId } = req.body;
    const response = await voiceChatService.processChatMessage(message, userId);
    res.json(response);
  } catch (error) {
    res.status(500).json({ error: 'Failed to process chat message' });
  }
});

app.get('/api/chat/history/:userId', (req, res) => {
  const history = voiceChatService.getChatHistory(req.params.userId);
  res.json(history);
});

// Dispatch actions endpoints
app.post('/api/dispatch/actions', (req, res) => {
  try {
    const actionData = req.body;
    const action = dispatchActionService.createAction(actionData);
    res.status(201).json(action);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create dispatch action' });
  }
});

app.get('/api/dispatch/actions/pending', (req, res) => {
  const actions = dispatchActionService.getPendingActions();
  res.json(actions);
});

app.post('/api/dispatch/actions/:actionId/approve', (req, res) => {
  const { approvedBy } = req.body;
  const success = dispatchActionService.approveAction(req.params.actionId, approvedBy);
  if (success) {
    res.json({ message: 'Action approved' });
  } else {
    res.status(404).json({ error: 'Action not found' });
  }
});

app.post('/api/dispatch/actions/:actionId/reject', (req, res) => {
  const { reason } = req.body;
  const success = dispatchActionService.rejectAction(req.params.actionId, reason);
  if (success) {
    res.json({ message: 'Action rejected' });
  } else {
    res.status(404).json({ error: 'Action not found' });
  }
});

// Quick actions endpoints
app.get('/api/dispatch/quick-actions', (req, res) => {
  const actions = dispatchActionService.getQuickActions();
  res.json(actions);
});

app.post('/api/dispatch/quick-actions/:actionId/execute', (req, res) => {
  const { shipmentId, userId } = req.body;
  const action = dispatchActionService.executeQuickAction(
    req.params.actionId,
    shipmentId,
    userId
  );
  if (action) {
    res.status(201).json(action);
  } else {
    res.status(404).json({ error: 'Quick action not found' });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'logistics-bff' });
});

const PORT = Number(process.env.LOGISTICS_BFF_PORT ?? 3071);

export function startLogisticsBFF(): void {
  server.listen(PORT, () => {
    console.log(`Logistics BFF listening on port ${PORT}`);
    console.log(`WebSocket endpoint ready for real-time updates`);
  });
}

if (require.main === module) {
  startLogisticsBFF();
}