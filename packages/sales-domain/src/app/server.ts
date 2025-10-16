import fastify from 'fastify';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';
import { registerQuoteRoutes } from './routes/quotes';
import { registerOrderRoutes } from './routes/orders';
import { registerInvoiceRoutes } from './routes/invoices';
import { registerCreditNoteRoutes } from './routes/credit-notes';
import { registerSalesOfferRoutes } from './routes/sales-offers';
import { authMiddleware } from './middleware/auth';
import { tenantMiddleware } from './middleware/tenant';
import { requestIdMiddleware } from './middleware/request-id';
import { loggerMiddleware } from './middleware/logger';
import { errorHandler } from './middleware/error-handler';
import { healthRoutes } from './routes/health';
import { getEventPublisher } from '../infra/messaging/publisher';
import { setupTelemetry, tracingMiddleware } from '../infra/telemetry/tracer';

const server = fastify({
  logger: {
    level: process.env.LOG_LEVEL ?? 'info',
    serializers: {
      req: (req: any) => ({
        method: req.method,
        url: req.url,
        hostname: req.hostname,
        remoteAddress: req.ip,
        remotePort: req.socket?.remotePort ?? undefined,
      }),
      res: (res: any) => ({
        statusCode: res.statusCode,
      }),
    },
  },
  disableRequestLogging: false,
  requestIdLogLabel: 'requestId',
  genReqId: () => require('crypto').randomUUID(),
});

// Register Swagger/OpenAPI
server.register(swagger, {
  openapi: {
    openapi: '3.0.3',
    info: {
      title: 'Sales Domain API',
      description: 'REST API for Sales Domain operations (Quotes, Sales Offers, Orders, Invoices, Credit Notes)',
      version: '1.0.0',
    },
    servers: [
      {
        url: process.env.API_BASE_URL ?? 'http://localhost:3001',
        description: 'Development server',
      },
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
    security: [
      {
        bearerAuth: [],
      },
    ],
  },
});

server.register(swaggerUi, {
  routePrefix: '/docs',
  uiConfig: {
    docExpansion: 'full',
    deepLinking: false,
  },
  staticCSP: true,
  transformStaticCSP: (header) => header,
});

// Initialize telemetry
setupTelemetry();

// Register middleware
server.addHook('onRequest', requestIdMiddleware);
server.addHook('onRequest', loggerMiddleware);
server.addHook('onRequest', authMiddleware);
server.addHook('onRequest', tenantMiddleware);

// Register tracing hooks
const tracing = tracingMiddleware();
server.addHook('onRequest', tracing.onRequest);
server.addHook('onResponse', tracing.onResponse);
server.addHook('onError', tracing.onError);

// Register error handler
server.setErrorHandler(errorHandler);

// Register routes
server.register(healthRoutes);
server.register(registerQuoteRoutes);
server.register(registerSalesOfferRoutes);
server.register(registerOrderRoutes);
server.register(registerInvoiceRoutes);
server.register(registerCreditNoteRoutes);

// Graceful shutdown
const gracefulShutdown = async (signal: string) => {
  server.log.info(`Received ${signal}, shutting down gracefully`);

  try {
    // Close event publisher
    const publisher = getEventPublisher();
    await publisher.disconnect();

    // Close server
    await server.close();
    server.log.info('Server closed successfully');
    process.exit(0);
  } catch (error) {
    server.log.error({ error }, 'Error during shutdown');
    process.exit(1);
  }
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Start server
const start = async () => {
  try {
    const port = Number(process.env.PORT) || 3001;
    const host = process.env.HOST ?? '0.0.0.0';

    // Initialize event publisher
    const publisher = getEventPublisher();
    await publisher.connect();

    await server.listen({ port, host });
    server.log.info(`Sales Domain API listening on http://${host}:${port}`);
    server.log.info(`API documentation available at http://${host}:${port}/docs`);
  } catch (err) {
    server.log.error(err);
    process.exit(1);
  }
};

export { server, start };
