import { check } from 'k6';
import ws from 'k6/ws';
import { Rate, Counter } from 'k6/metrics';

// Custom metrics
const sseConnections = new Counter('sse_connections');
const sseMessages = new Counter('sse_messages');
const sseErrors = new Rate('sse_errors');

// Test configuration
export const options = {
  stages: [
    { duration: '30s', target: 100 },    // Ramp up to 100 connections
    { duration: '1m', target: 500 },     // Ramp up to 500 connections
    { duration: '3m', target: 1000 },    // Ramp up to 1000 connections
    { duration: '5m', target: 1000 },    // Stay at 1000 connections
    { duration: '1m', target: 0 },       // Ramp down
  ],
  thresholds: {
    'sse_errors': ['rate<0.01'],         // Error rate < 1%
    'sse_messages': ['count>1000'],      // At least 1000 messages received
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const WS_URL = BASE_URL.replace('http', 'ws');

export default function () {
  const channels = ['workflow', 'sales', 'inventory', 'policy'];
  const channel = channels[Math.floor(Math.random() * channels.length)];
  
  const url = `${WS_URL}/api/stream/${channel}`;
  
  const res = ws.connect(url, {}, function (socket) {
    sseConnections.add(1);
    
    socket.on('open', () => {
      console.log(`Connected to SSE channel: ${channel}`);
    });
    
    socket.on('message', (data) => {
      sseMessages.add(1);
      
      try {
        const message = JSON.parse(data);
        check(message, {
          'message has type': (m) => m.type !== undefined,
          'message has channel': (m) => m.channel !== undefined || m.topic !== undefined,
        });
      } catch (e) {
        sseErrors.add(1);
      }
    });
    
    socket.on('error', (e) => {
      console.error(`SSE error: ${e}`);
      sseErrors.add(1);
    });
    
    socket.on('close', () => {
      console.log(`Disconnected from SSE channel: ${channel}`);
    });
    
    // Keep connection open for 5 minutes
    socket.setTimeout(() => {
      socket.close();
    }, 300000);
  });
  
  check(res, {
    'SSE connection established': (r) => r && r.status === 101,
  });
}

