// import Fastify from 'fastify';
// import cors from '@fastify/cors';
// import { initTRPC } from '@trpc/server';
// import * as trpcAdapter from '@trpc/server/adapters/fastify';
// import { JWTValidator } from '@valero-neuroerp/auth';
// import { RBACPolicy } from '@valero-neuroerp/auth';
// import { TenantContextManager } from '@valero-neuroerp/auth';

// Import route handlers
// import { dashboardRoutes } from './routes/dashboard';
// import { shipmentRoutes } from './routes/shipments';
// import { orderRoutes } from './routes/orders';
// import { inventoryRoutes } from './routes/inventory';

// Simple HTTP server for now
import { createServer } from 'http';

/* eslint-disable @typescript-eslint/strict-boolean-expressions */

// HTTP status codes and constants
const httpStatusOk = 200;
const httpStatusOptions = 200;
const defaultPort = 4001;
const hostDefault = '0.0.0.0';

// Simple logger to replace console statements
const logger = {
  info: (message: string): void => {
    // eslint-disable-next-line no-console
    console.log(`ℹ️  ${message}`);
  },
  warn: (message: string): void => {
    // eslint-disable-next-line no-console
    console.warn(`⚠️  ${message}`);
  },
  error: (message: string): void => {
    // eslint-disable-next-line no-console
    console.error(`❌ ${message}`);
  }
};

// Initialize tRPC (commented out for now)
// const t = initTRPC.create();

// Create tRPC router (commented out for now)
// const appRouter = t.router({
//   health: t.procedure.query(() => ({ status: 'ok', timestamp: new Date().toISOString() })),
// });

// Export type for client
// export type AppRouter = typeof appRouter;

// Initialize services
// const jwtValidator = new JWTValidator({
//   issuer: process.env.JWT_ISSUER || 'valero-neuroerp',
//   audience: process.env.JWT_AUDIENCE || 'neuroerp-api'
// });

// const rbacPolicy = new RBACPolicy({
//   roles: [], // TODO: Load from configuration
//   permissions: [] // TODO: Load from configuration
// });

// const tenantContext = new TenantContextManager();

// Create simple HTTP server
const server = createServer((req, res) => {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    res.writeHead(httpStatusOptions);
    res.end();
    return;
  }

  // Health check endpoint
  if (req.url === '/health' && req.method === 'GET') {
    res.writeHead(httpStatusOk, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      ok: true,
      service: 'bff-web',
      timestamp: new Date().toISOString(),
      uptime: process.uptime()
    }));
    return;
  }

  // Default response
  res.writeHead(httpStatusOk, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    message: 'VALEO NeuroERP 3.0 - BFF-Web',
    version: '0.1.0',
    endpoints: {
      health: '/health',
      status: 'running'
    }
  }));
});

// Helper function to find an available port
async function findAvailablePort(startPort: number): Promise<number> {
  return new Promise((resolve, reject) => {
    const testServer = createServer();

    testServer.listen(startPort, '0.0.0.0', () => {
      const address = testServer.address();
      const port = typeof address === 'string' ? parseInt(address.split(':').pop() ?? '0', 10) : (address as { port: number }).port;
      testServer.close(() => resolve(port));
    });

    testServer.on('error', (error: Error & { code?: string }) => {
      if (error.code === 'EADDRINUSE') {
        // Try next port
        findAvailablePort(startPort + 1).then(resolve).catch(reject);
      } else {
        reject(error);
      }
    });
  });
}

// Start server function with better error handling
async function startServer(): Promise<void> {
  const portEnv = process.env.PORT;
  const portValue = portEnv ? Number(portEnv) : defaultPort;
  const hostEnv = process.env.HOST;
  const host = hostEnv ?? hostDefault;

  try {
    // Try to find an available port starting from the default
    const port = await findAvailablePort(defaultPort);

    if (port !== portValue) {
      logger.warn(`Port ${portValue} is occupied, using port ${port} instead`);
      logger.warn(`To avoid this, ensure no other services are using port ${portValue}`);
      logger.warn('Or set PORT environment variable to use a different port');
    }

    server.listen(port, host, () => {
      logger.info(`BFF-Web server running on http://${host}:${port}`);
      logger.info(`Health check: http://${host}:${port}/health`);
      logger.info(`Service: VALEO NeuroERP 3.0 - BFF-Web v0.1.0`);
    });

    server.on('error', (error: Error & { code?: string }) => {
      if (error.code === 'EADDRINUSE') {
        logger.error(`Port ${port} is already in use`);
        logger.error('Check if another instance is running:');
        logger.error(`  - Use 'netstat -ano | findstr :${port}' to find the process`);
        logger.error('  - Use \'taskkill /PID <PID> /F\' to stop it');
        logger.error('  - Or set PORT environment variable to use a different port');
      } else {
        const message = error.message ? (error.message.length > 0 ? error.message : 'Unknown error') : 'Unknown error';
        logger.error(`Failed to start server: ${message}`);
      }
      process.exit(1);
    });

  } catch (error) {
    logger.error(`Failed to start server: ${error instanceof Error ? error.message : String(error)}`);
    logger.error('This might be due to port conflicts or insufficient permissions');
    process.exit(1);
  }
}

// Start the server
startServer().catch((error) => {
  logger.error(`Failed to start server: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});