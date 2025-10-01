import fastify from 'fastify';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';
import dotenv from 'dotenv';
import { healthRoutes } from './routes/health';
import { registerSampleRoutes } from './routes/samples';
import { registerQualityPlanRoutes } from './routes/quality-plans';
import { registerNonConformityRoutes } from './routes/non-conformities';
import { registerCapaRoutes } from './routes/capas';
import { registerMLInsightsRoutes } from './routes/ml-insights';
import { authMiddleware } from './middleware/auth';
import { tenantMiddleware } from './middleware/tenant';
import { requestIdMiddleware } from './middleware/request-id';
import { loggerMiddleware } from './middleware/logger';
import { errorHandler } from './middleware/error-handler';
import { setupTelemetry, tracingMiddleware } from '../infra/telemetry/tracer';
import { initEventPublisher, closeEventPublisher } from '../infra/messaging/publisher';
import { startHiddenMonitoring, stopHiddenMonitoring } from '../domain/services/hidden-monitoring';

dotenv.config();

const server = fastify({
  logger: {
    level: process.env.LOG_LEVEL || 'info',
    serializers: {
      req: (req) => ({
        method: req.method,
        url: req.url,
        hostname: req.hostname,
        remoteAddress: req.ip,
      }),
      res: (res) => ({
        statusCode: res.statusCode,
      }),
    },
  },
  disableRequestLogging: false,
  requestIdLogLabel: 'requestId',
});

// Setup OpenTelemetry
setupTelemetry();

// Register Swagger/OpenAPI
server.register(swagger, {
  openapi: {
    openapi: '3.0.3',
    info: {
      title: 'Quality Domain API',
      description: 'REST API for Quality Management & Quality Assurance (QM/QS)',
      version: '1.0.0',
    },
    servers: [
      {
        url: process.env.API_BASE_URL || 'http://localhost:3007',
        description: 'Development server',
      },
    ],
    tags: [
      { name: 'quality-plans', description: 'Quality plan operations' },
      { name: 'samples', description: 'Sample operations' },
      { name: 'non-conformities', description: 'Non-conformity operations' },
      { name: 'capa', description: 'CAPA operations' },
      { name: 'health', description: 'Health check endpoints' },
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

// Register global middlewares
server.addHook('onRequest', requestIdMiddleware);
server.addHook('onRequest', loggerMiddleware);
server.addHook('onRequest', tenantMiddleware);
// server.addHook('onRequest', authMiddleware); // Enable in production
server.addHook('onRequest', tracingMiddleware);

// Register error handler
server.setErrorHandler(errorHandler);

// Register routes
server.register(healthRoutes);
server.register(registerSampleRoutes, { prefix: '/quality/api/v1' });
server.register(registerQualityPlanRoutes, { prefix: '/quality/api/v1' });
server.register(registerNonConformityRoutes, { prefix: '/quality/api/v1' });
server.register(registerCapaRoutes, { prefix: '/quality/api/v1' });
server.register(registerMLInsightsRoutes, { prefix: '/quality/api/v1' });

// OpenAPI JSON endpoint
server.get('/quality/api/v1/openapi.json', async () => {
  return server.swagger();
});

/**
 * Start server
 */
export async function start(): Promise<void> {
  try {
    // Initialize event publisher
    await initEventPublisher();

    // Start hidden monitoring (AI-powered background monitoring)
    startHiddenMonitoring();

    const port = parseInt(process.env.PORT || '3007', 10);
    const host = process.env.HOST || '0.0.0.0';

    await server.listen({ port, host });
    server.log.info(`🚀 Quality Domain server listening on ${host}:${port}`);
    server.log.info(`📚 API Documentation: http://${host}:${port}/documentation`);
    server.log.info(`🤖 AI-Powered Hidden Monitoring: ${process.env.HIDDEN_MONITORING_ENABLED !== 'false' ? 'ENABLED' : 'DISABLED'}`);
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
    stopHiddenMonitoring();
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
