import fastify from 'fastify';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';
import dotenv from 'dotenv';
import { registerQuoteRoutes } from './routes/quotes';
import { initEventPublisher, closeEventPublisher } from '../infra/messaging/publisher';
import pino from 'pino';

dotenv.config();

const server = fastify({
  logger: pino({ level: process.env.LOG_LEVEL || 'info' }),
  disableRequestLogging: false,
  requestIdLogLabel: 'requestId',
});

// Register Swagger
server.register(swagger, {
  openapi: {
    openapi: '3.0.3',
    info: {
      title: 'Pricing Domain API',
      description: 'REST API for Price Calculation (PriceLists, Conditions, Formulas, Quotes)',
      version: '1.0.0',
    },
    servers: [{ url: process.env.API_BASE_URL || 'http://localhost:3060' }],
    tags: [
      { name: 'quotes', description: 'Price quote calculation' },
      { name: 'pricelists', description: 'Price list management' },
      { name: 'conditions', description: 'Customer conditions' },
      { name: 'formulas', description: 'Dynamic formulas' },
    ],
  },
});

server.register(swaggerUi, {
  routePrefix: '/documentation',
  uiConfig: { docExpansion: 'list', deepLinking: true },
});

// Health
server.get('/health', async () => ({ status: 'ok', service: 'pricing-domain', timestamp: new Date().toISOString() }));
server.get('/ready', async () => ({ status: 'ready' }));
server.get('/live', async () => ({ status: 'alive' }));

// Routes
server.register(registerQuoteRoutes, { prefix: '/pricing/api/v1' });

// OpenAPI
server.get('/pricing/api/v1/openapi.json', async () => server.swagger());

export async function start(): Promise<void> {
  try {
    await initEventPublisher();
    const port = parseInt(process.env.PORT || '3060', 10);
    const host = process.env.HOST || '0.0.0.0';
    await server.listen({ port, host });
    server.log.info(`🚀 Pricing Domain listening on ${host}:${port}`);
    server.log.info(`📚 Docs: http://${host}:${port}/documentation`);
  } catch (error) {
    server.log.error(error);
    process.exit(1);
  }
}

export async function stop(): Promise<void> {
  try {
    await closeEventPublisher();
    await server.close();
    server.log.info('Server stopped');
  } catch (error) {
    server.log.error(error);
  }
}

process.on('SIGTERM', stop);
process.on('SIGINT', stop);

if (require.main === module) {
  start();
}

export default server;
