import { FastifyInstance } from 'fastify';

export async function healthRoutes(server: FastifyInstance): Promise<void> {
  server.get('/health', async (request, reply) => {
    return { status: 'ok', service: 'quality-domain', timestamp: new Date().toISOString() };
  });

  server.get('/ready', async (request, reply) => {
    // Check if all dependencies are ready (DB, NATS, etc.)
    return { status: 'ready', timestamp: new Date().toISOString() };
  });

  server.get('/live', async (request, reply) => {
    return { status: 'alive', timestamp: new Date().toISOString() };
  });
}
