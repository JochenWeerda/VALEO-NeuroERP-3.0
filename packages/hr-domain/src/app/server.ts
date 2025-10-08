/**
 * HR Domain Server for VALEO NeuroERP 3.0
 * Fastify server with OpenAPI documentation
 */

import cors from '@fastify/cors';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';
import Fastify from 'fastify';
import pino from 'pino';

import { authMiddleware, initializeAuth } from './middleware/auth';
import { registerEmployeeRoutes } from './routes/employees';
import { registerTimeEntryRoutes } from './routes/time-entries';

import { EmployeeService } from '../domain/services/employee-service';
import { TimeEntryService } from '../domain/services/time-entry-service';
import type { HREvent } from '../domain/events';
import { PostgresEmployeeRepository } from '../infra/repo/postgres-employee-repository';
import { PostgresTimeEntryRepository } from '../infra/repo/postgres-time-entry-repository';

const DEFAULT_PORT = 3030;
const DEFAULT_HOST = '0.0.0.0';
const DEFAULT_LOG_LEVEL = 'info';

const HTTP_STATUS = {
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500
} as const;

const logger = pino({
  level: process.env.LOG_LEVEL ?? DEFAULT_LOG_LEVEL,
  transport: process.env.NODE_ENV === 'development'
    ? {
        target: 'pino-pretty',
        options: {
          colorize: true
        }
      }
    : undefined
});

const PORT = Number(process.env.PORT ?? DEFAULT_PORT);
const HOST = process.env.HOST ?? DEFAULT_HOST;
const BASE_URL = ['http://', HOST, ':', String(PORT)].join('');

const employeeRepository = new PostgresEmployeeRepository();
const timeEntryRepository = new PostgresTimeEntryRepository();

type DomainEventPublisher = (event: HREvent) => Promise<void>;

const eventPublisher: DomainEventPublisher = async (event) => {
  logger.info({ eventType: event.eventType, eventId: event.eventId }, 'Publishing domain event');
};

const employeeService = new EmployeeService(employeeRepository, eventPublisher);
const timeEntryService = new TimeEntryService(timeEntryRepository, employeeRepository, eventPublisher);

const fastify = Fastify({
  logger
});

async function registerPlugins(): Promise<void> {
  await fastify.register(cors, {
    origin: true,
    credentials: true
  });

  await fastify.register(swagger, {
    openapi: {
      info: {
        title: 'VALEO NeuroERP 3.0 - HR Domain API',
        description: 'Human Resources Domain API for employee management, time tracking, and payroll preparation',
        version: '1.0.0'
      },
      servers: [
        {
          url: BASE_URL,
          description: 'HR Domain Server'
        }
      ],
      components: {
        securitySchemes: {
          bearerAuth: {
            type: 'http',
            scheme: 'bearer',
            bearerFormat: 'JWT'
          }
        }
      },
      security: [
        {
          bearerAuth: []
        }
      ]
    }
  });

  await fastify.register(swaggerUi, {
    routePrefix: '/docs',
    uiConfig: {
      docExpansion: 'full',
      deepLinking: false
    },
    staticCSP: true
  });
}

async function registerMiddleware(): Promise<void> {
  await initializeAuth();
  fastify.addHook('onRequest', authMiddleware);
}

async function registerRoutes(): Promise<void> {
  fastify.get('/health', async () => ({
    ok: true,
    service: 'hr-domain',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  }));

  fastify.get('/ready', async () => ({
    ok: true,
    database: true,
    timestamp: new Date().toISOString()
  }));

  fastify.get('/live', async () => ({
    ok: true,
    timestamp: new Date().toISOString()
  }));

  registerEmployeeRoutes(fastify, employeeService);
  registerTimeEntryRoutes(fastify, timeEntryService);
}

fastify.setErrorHandler(async (error, request, reply) => {
  fastify.log.error({ err: error, url: request.url }, 'Unhandled error');

  if ('validation' in error && error.validation) {
    await reply.code(HTTP_STATUS.BAD_REQUEST).send({
      error: 'Validation failed',
      details: error.validation
    });
    return;
  }

  if (error.statusCode === HTTP_STATUS.UNAUTHORIZED) {
    await reply.code(HTTP_STATUS.UNAUTHORIZED).send({
      error: 'Unauthorized',
      message: error.message
    });
    return;
  }

  if (error.statusCode === HTTP_STATUS.FORBIDDEN) {
    await reply.code(HTTP_STATUS.FORBIDDEN).send({
      error: 'Forbidden',
      message: error.message
    });
    return;
  }

  if (error.statusCode === HTTP_STATUS.NOT_FOUND) {
    await reply.code(HTTP_STATUS.NOT_FOUND).send({
      error: 'Not found',
      message: error.message
    });
    return;
  }

  await reply.code(HTTP_STATUS.INTERNAL_SERVER_ERROR).send({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? error.message : 'An unexpected error occurred'
  });
});

async function start(): Promise<void> {
  try {
    await registerPlugins();
    await registerMiddleware();
    await registerRoutes();

    const address = await fastify.listen({ port: PORT, host: HOST });
    logger.info({ address }, 'HR Domain Server running');
    logger.info({ docs: `${BASE_URL}/docs` }, 'API documentation available');
  } catch (error) {
    logger.error({ err: error }, 'Failed to start server');
    process.exit(1);
  }
}

async function gracefulShutdown(): Promise<void> {
  logger.info('Gracefully shutting down...');

  try {
    await fastify.close();
    logger.info('Server shut down successfully');
    process.exit(0);
  } catch (error) {
    logger.error({ err: error }, 'Error during shutdown');
    process.exit(1);
  }
}

process.on('SIGTERM', () => {
  void gracefulShutdown();
});

process.on('SIGINT', () => {
  void gracefulShutdown();
});

if (require.main === module) {
  void start();
}

export default fastify;
