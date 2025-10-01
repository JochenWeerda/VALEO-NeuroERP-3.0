import fastify from 'fastify';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';
import dotenv from 'dotenv';
import { registerMessageRoutes } from './routes/messages';
import { initEventPublisher, closeEventPublisher } from '../infra/messaging/publisher';
import pino from 'pino';

dotenv.config();

const server = fastify({
  logger: pino({ level: process.env.LOG_LEVEL ?? 'info' }),
  requestIdLogLabel: 'requestId',
});

void server.register(swagger, {
  openapi: {
    openapi: '3.0.3',
    info: {
      title: 'Notifications Domain API',
      description: 'Multi-Channel Notification Platform (Email, SMS, WhatsApp, Push)',
      version: '1.0.0',
    },
    servers: [{ url: process.env.API_BASE_URL ?? 'http://localhost:3080' }],
  },
});

void server.register(swaggerUi, { routePrefix: '/documentation' });

server.get('/health', async () => ({ status: 'ok', service: 'notifications-domain' }));
server.get('/ready', async () => ({ status: 'ready' }));
server.get('/live', async () => ({ status: 'alive' }));

void server.register(registerMessageRoutes, { prefix: '/notifications/api/v1' });
server.get('/notifications/api/v1/openapi.json', async () => server.swagger());

export async function start(): Promise<void> {
  try {
    await initEventPublisher();
    const port = parseInt(process.env.PORT ?? '3080', 10);
    await server.listen({ port, host: '0.0.0.0' });
    server.log.info(`🚀 Notifications Domain on port ${port}`);
  } catch (error) {
    server.log.error(error);
    process.exit(1);
  }
}

export async function stop(): Promise<void> {
  await closeEventPublisher();
  await server.close();
}

process.on('SIGTERM', () => {
  void stop();
});
process.on('SIGINT', () => {
  void stop();
});

if (require.main === module) {
  void start();
}

export default server;
