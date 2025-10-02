import fastify from 'fastify';
import { registerTicketRoutes } from './routes/tickets';
import { WeighingService } from '../domain/services/weighing-service';
import { WeighingTicketRepository } from '../infra/repo/weighing-ticket-repository';
import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';

// Create database connection
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || process.env.POSTGRES_URL,
});

const db = drizzle(pool);

// Initialize dependencies
const ticketRepository = new WeighingTicketRepository(db);
const weighingService = new WeighingService(ticketRepository);

// Create Fastify app
const app = fastify({
  logger: {
    level: process.env.LOG_LEVEL || 'info',
    transport: {
      target: 'pino-pretty',
      options: {
        translateTime: 'HH:MM:ss Z',
        ignore: 'pid,hostname',
      },
    },
  },
});

// Register Swagger/OpenAPI
app.register(import('@fastify/swagger'), {
  openapi: {
    openapi: '3.0.0',
    info: {
      title: 'Weighing Domain API',
      description: 'API for agricultural weighing operations',
      version: '1.0.0',
    },
    servers: [
      {
        url: `http://localhost:${process.env.PORT || 3005}`,
        description: 'Development server',
      },
    ],
    tags: [
      { name: 'weighing-tickets', description: 'Weighing ticket operations' },
    ],
  },
});

app.register(import('@fastify/swagger-ui'), {
  routePrefix: '/documentation',
  uiConfig: {
    docExpansion: 'full',
    deepLinking: false,
  },
});

// Health check endpoints
app.get('/health', async () => {
  return { status: 'ok', service: 'weighing-domain' };
});

app.get('/ready', async () => {
  try {
    // Check database connection
    await pool.query('SELECT 1');
    return { status: 'ready', database: 'connected' };
  } catch (error) {
    app.log.error({ error }, 'Database health check failed');
    return { status: 'not ready', database: 'disconnected' };
  }
});

app.get('/live', async () => {
  return { status: 'live', timestamp: new Date().toISOString() };
});

// Register routes
registerTicketRoutes(app, weighingService);

// Graceful shutdown
const closeGracefully = async (signal: string) => {
  app.log.info(`Received signal ${signal}, shutting down gracefully`);

  try {
    await app.close();
    await pool.end();
    process.exit(0);
  } catch (error) {
    app.log.error({ error }, 'Error during shutdown');
    process.exit(1);
  }
};

process.on('SIGINT', () => closeGracefully('SIGINT'));
process.on('SIGTERM', () => closeGracefully('SIGTERM'));

// Start server
const start = async () => {
  try {
    const port = parseInt(process.env.PORT || '3005', 10);
    const host = process.env.HOST || '0.0.0.0';

    await app.listen({ port, host });

    app.log.info(`Weighing Domain API listening on http://${host}:${port}`);
    app.log.info(`API Documentation available at http://${host}:${port}/documentation`);

  } catch (error) {
    app.log.error({ error }, 'Failed to start server');
    process.exit(1);
  }
};

start();