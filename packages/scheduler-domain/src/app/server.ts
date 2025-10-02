import Fastify, { FastifyInstance } from 'fastify';
import { registerScheduleRoutes } from './routes/schedules';
import { authMiddleware } from './middleware/auth';
import { tenantMiddleware } from './middleware/tenant';
import { requestLoggerMiddleware } from './middleware/logger';
import { initializeJWTAuthenticator } from '../infra/security/jwt';
import { initializeTracing } from '../infra/telemetry/tracer';
import { getLogger } from '../infra/telemetry/logger';
import { scheduleRepository } from '../infra/repo/schedule-repository';

const logger = getLogger();

export async function createServer(): Promise<FastifyInstance> {
  const server = Fastify({
    logger: false, // We use our own logger
    disableRequestLogging: true, // We handle request logging manually
    trustProxy: true,
  });

  // Initialize infrastructure
  await initializeJWTAuthenticator();
  await initializeTracing();

  // Register middleware
  server.addHook('onRequest', requestLoggerMiddleware);
  server.addHook('onRequest', authMiddleware);
  server.addHook('onRequest', tenantMiddleware);

  // Health check endpoints
  server.get('/health', async () => {
    return { status: 'ok', timestamp: new Date().toISOString() };
  });

  server.get('/ready', async () => {
    // Check database connectivity
    try {
      await scheduleRepository.countByTenant('health-check');
      return {
        status: 'ready',
        database: 'connected',
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      logger.error('Database health check failed', error as Error);
      throw new Error('Database not ready');
    }
  });

  server.get('/live', async () => {
    return {
      status: 'alive',
      timestamp: new Date().toISOString()
    };
  });

  // Register routes
  await registerScheduleRoutes(server, scheduleRepository);

  // Error handling
  server.setErrorHandler((error, request, reply) => {
    logger.error('Request error', error, {
      requestId: (request as any).requestId,
      tenantId: request.auth?.tenantId,
      userId: request.auth?.user.sub,
      method: request.method,
      url: request.url,
    });

    // Don't leak internal errors
    const statusCode = error.statusCode || 500;
    const message = statusCode >= 500 ? 'Internal server error' : error.message;

    reply.code(statusCode).send({
      error: error.name || 'Error',
      message,
      requestId: (request as any).requestId,
    });
  });

  // Not found handler
  server.setNotFoundHandler((request, reply) => {
    logger.warn('Route not found', {
      requestId: (request as any).requestId,
      method: request.method,
      url: request.url,
    });

    reply.code(404).send({
      error: 'Not Found',
      message: 'Route not found',
      requestId: (request as any).requestId,
    });
  });

  return server;
}

export async function startServer(): Promise<void> {
  try {
    const server = await createServer();
    const port = parseInt(process.env.PORT || '3080');
    const host = process.env.HOST || '0.0.0.0';

    await server.listen({ port, host });

    logger.info('Scheduler domain server started', {
      port,
      host,
      environment: process.env.NODE_ENV || 'development',
    });

    // Graceful shutdown
    const shutdown = async (signal: string) => {
      logger.info(`Received ${signal}, shutting down gracefully`);

      await server.close();

      // Shutdown tracing
      try {
        const { shutdownTracing } = await import('../infra/telemetry/tracer');
        await shutdownTracing();
      } catch (error) {
        logger.error('Error shutting down tracing', error as Error);
      }

      process.exit(0);
    };

    process.on('SIGTERM', () => shutdown('SIGTERM'));
    process.on('SIGINT', () => shutdown('SIGINT'));

  } catch (error) {
    logger.error('Failed to start server', error as Error);
    process.exit(1);
  }
}

// Start server if this file is run directly
if (require.main === module) {
  startServer();
}