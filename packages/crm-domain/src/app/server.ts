import fastify from 'fastify';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';
import { checkDatabaseConnection } from '../infra/db/connection';
import { getEventPublisher } from '../infra/messaging/publisher';
import { CustomerRepository } from '../infra/repo';
import { CustomerService } from '../domain/services';
import { registerCustomerRoutes } from './routes/customers';
import { registerContactRoutes } from './routes/contacts';
import { registerOpportunityRoutes } from './routes/opportunities';
import { registerInteractionRoutes } from './routes/interactions';

// Create Fastify instance
const server = fastify({
  logger: process.env.NODE_ENV === 'development' ? {
    level: process.env.LOG_LEVEL ?? 'info',
    transport: {
      target: 'pino-pretty',
      options: {
        colorize: true,
        translateTime: 'SYS:yyyy-mm-dd HH:MM:ss.l',
        ignore: 'pid,hostname'
      }
    }
  } : {
    level: process.env.LOG_LEVEL ?? 'info'
  }
});

// Register Swagger/OpenAPI
server.register(swagger, {
  openapi: {
    info: {
      title: 'CRM Domain API',
      description: 'Customer Relationship Management Domain Service API',
      version: '1.0.0'
    },
    servers: [
      {
        url: 'http://localhost:3010',
        description: 'Development server'
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
    }
  }
});

// Register Swagger UI
server.register(swaggerUi, {
  routePrefix: '/docs',
  uiConfig: {
    docExpansion: 'list',
    deepLinking: false
  },
  staticCSP: true,
  transformStaticCSP: (header: string) => header
});

// Health check endpoints
server.get('/health', async () => {
  const dbHealthy = await checkDatabaseConnection();
  const eventPublisher = getEventPublisher();
  const messagingHealthy = eventPublisher.isHealthy();

  const health = {
    status: dbHealthy && messagingHealthy ? 'healthy' : 'unhealthy',
    timestamp: new Date().toISOString(),
    services: {
      database: dbHealthy ? 'healthy' : 'unhealthy',
      messaging: messagingHealthy ? 'healthy' : 'unhealthy'
    }
  };

  return health;
});

// Readiness check
server.get('/ready', async () => {
  const dbHealthy = await checkDatabaseConnection();
  const eventPublisher = getEventPublisher();
  const messagingHealthy = eventPublisher.isHealthy();

  if (!dbHealthy || !messagingHealthy) {
    throw new Error('Service not ready');
  }

  return {
    status: 'ready',
    timestamp: new Date().toISOString()
  };
});

// Liveness check
server.get('/live', async () => {
  return {
    status: 'alive',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  };
});

// OpenAPI JSON endpoint
server.get('/openapi.json', async () => {
  return server.swagger();
});

// Initialize services
async function initializeServices() {
  try {
    // Initialize database connection
    const dbHealthy = await checkDatabaseConnection();
    if (dbHealthy === undefined || dbHealthy === null) {
      throw new Error('Database connection failed');
    }

    // Initialize event publisher
    const eventPublisher = getEventPublisher();
    await eventPublisher.connect();

    // Initialize repositories and services
    const customerRepo = new CustomerRepository();
    const customerService = new CustomerService({ customerRepo });

    return {
      customerService
    };
  } catch (error) {
    server.log.error('Failed to initialize services:', error as any);
    throw error;
  }
}

// Register routes
async function registerRoutes() {
  const services = await initializeServices();

  // Register API routes
  await registerCustomerRoutes(server, services);
  await registerContactRoutes(server, services);
  await registerOpportunityRoutes(server, services);
  await registerInteractionRoutes(server, services);
}

// Graceful shutdown
async function gracefulShutdown() {
  server.log.info('Starting graceful shutdown...');

  try {
    // Close event publisher connection
    const eventPublisher = getEventPublisher();
    await eventPublisher.disconnect();

    // Close server
    await server.close();

    server.log.info('Graceful shutdown completed');
  } catch (error) {
    server.log.error('Error during graceful shutdown:', error as any);
    process.exit(1);
  }
}

// Handle shutdown signals
process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

// Start server
async function startServer() {
  try {
    const port = Number(process.env.PORT) || 3010;
    const host = '0.0.0.0';

    await registerRoutes();

    await server.listen({ port, host });

    server.log.info(`CRM Domain API server listening on ${host}:${port}`);
    server.log.info(`API Documentation available at http://localhost:${port}/docs`);

  } catch (error) {
    server.log.error('Failed to start server:', error as any);
    process.exit(1);
  }
}

// Start the server
startServer();
