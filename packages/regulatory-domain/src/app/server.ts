import fastify from 'fastify';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';
import dotenv from 'dotenv';
import { registerLabelRoutes } from './routes/labels';
import { registerPSMRoutes } from './routes/psm';
import { registerGHGRoutes } from './routes/ghg';
import { registerKTBLRoutes } from './routes/ktbl';
import { initEventPublisher, closeEventPublisher } from '../infra/messaging/publisher';
import pino from 'pino';

dotenv.config();

const server = fastify({
  logger: pino({
    level: process.env.LOG_LEVEL ?? 'info',
  }),
  disableRequestLogging: false,
  requestIdLogLabel: 'requestId',
});

// Register Swagger/OpenAPI
server.register(swagger, {
  openapi: {
    openapi: '3.0.3',
    info: {
      title: 'Regulatory Domain API',
      description: 'REST API for Regulatory Compliance (VLOG, QS, PSM, RED II, Labels)',
      version: '1.0.0',
    },
    servers: [
      {
        url: process.env.API_BASE_URL ?? 'http://localhost:3008',
        description: 'Development server',
      },
    ],
    tags: [
      { name: 'labels', description: 'Label & Compliance evaluation' },
      { name: 'psm', description: 'PSM (Pflanzenschutzmittel) checks' },
      { name: 'ghg', description: 'GHG/THG emissions (RED II)' },
      { name: 'policies', description: 'Regulatory policies' },
      { name: 'evidence', description: 'Compliance evidence' },
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
        },
      },
    },
    security: [{ bearerAuth: [] }],
  },
});

server.register(swaggerUi, {
  routePrefix: '/documentation',
  uiConfig: {
    docExpansion: 'list',
    deepLinking: true,
  },
});

// Health endpoints
server.get('/health', async () => ({ status: 'ok', service: 'regulatory-domain', timestamp: new Date().toISOString() }));
server.get('/ready', async () => ({ status: 'ready', timestamp: new Date().toISOString() }));
server.get('/live', async () => ({ status: 'alive', timestamp: new Date().toISOString() }));

// Register routes
server.register(registerLabelRoutes, { prefix: '/regulatory/api/v1' });
server.register(registerPSMRoutes, { prefix: '/regulatory/api/v1' });
server.register(registerGHGRoutes, { prefix: '/regulatory/api/v1' });
server.register(registerKTBLRoutes, { prefix: '/regulatory/api/v1' });

// OpenAPI JSON endpoint
server.get('/regulatory/api/v1/openapi.json', async () => {
  return server.swagger();
});

/**
 * Start server
 */
export async function start(): Promise<void> {
  try {
    await initEventPublisher();

    const port = parseInt(process.env.PORT ?? '3008', 10);
    const host = process.env.HOST ?? '0.0.0.0';

    await server.listen({ port, host });
    server.log.info(`🚀 Regulatory Domain server listening on ${host}:${port}`);
    server.log.info(`📚 API Documentation: http://${host}:${port}/documentation`);
  } catch (error) {
    server.log.error(error);
    process.exit(1);
  }
}

/**
 * Stop server gracefully
 */
export async function stop(): Promise<void> {
  try {
    await closeEventPublisher();
    await server.close();
    server.log.info('Server stopped gracefully');
  } catch (error) {
    server.log.error(error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on('SIGTERM', stop);
process.on('SIGINT', stop);

// Start server if executed directly
if (require.main === module) {
  start();
}

export default server;

