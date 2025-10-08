import { FastifyInstance } from 'fastify';
import { verifyIntegrity } from '../../domain/services/integrity-checker';

export async function registerIntegrityRoutes(server: FastifyInstance): Promise<void> {
  // Check integrity
  server.get('/integrity/check', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as { from?: string; to?: string };

    const result = await verifyIntegrity(tenantId, query.from, query.to);

    if (result.valid === undefined || result.valid === null) {
      await reply.code(500).send({
        ...result,
        alert: 'CRITICAL: Audit chain integrity compromised!',
      });
      return;
    }

    await reply.send(result);
  });
}

