import fastify from 'fastify';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';
import dotenv from 'dotenv';
import { registerDocumentRoutes } from './routes/documents';
import { initEventPublisher, closeEventPublisher } from '../infra/messaging/publisher';
import pino from 'pino';

dotenv.config();

const server = fastify({
  logger: pino({ level: process.env.LOG_LEVEL || 'info' }),
  requestIdLogLabel: 'requestId',
});

server.register(swagger, {
  openapi: {
    openapi: '3.0.3',
    info: { title: 'Document Domain API', description: 'Document Platform (Templates, Rendering, Archiving)', version: '1.0.0' },
    servers: [{ url: process.env.API_BASE_URL || 'http://localhost:3070' }],
  },
});

server.register(swaggerUi, { routePrefix: '/documentation' });

server.get('/health', async () => ({ status: 'ok', service: 'document-domain' }));
server.get('/ready', async () => ({ status: 'ready' }));
server.get('/live', async () => ({ status: 'alive' }));

server.register(registerDocumentRoutes, { prefix: '/document/api/v1' });
server.get('/document/api/v1/openapi.json', async () => server.swagger());

export async function start(): Promise<void> {
  try {
    await initEventPublisher();
    const port = parseInt(process.env.PORT || '3070', 10);
    await server.listen({ port, host: '0.0.0.0' });
    server.log.info(`🚀 Document Domain on port ${port}`);
  } catch (error) {
    server.log.error(error);
    process.exit(1);
  }
}

export async function stop(): Promise<void> {
  await closeEventPublisher();
  await server.close();
}

process.on('SIGTERM', stop);
process.on('SIGINT', stop);

if (require.main === module) start();

export default server;
