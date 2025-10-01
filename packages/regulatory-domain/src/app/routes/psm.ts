import { FastifyInstance } from 'fastify';
import { PSMCheckInputSchema } from '../../domain/entities/psm-product';
import { checkPSM } from '../../domain/services/psm-check-service';
import { searchPSM } from '../../infra/integrations/bvl-api';

export async function registerPSMRoutes(server: FastifyInstance): Promise<void> {
  // Check PSM compliance
  server.post('/psm/check', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;

    const input = PSMCheckInputSchema.parse({ ...request.body, tenantId });
    const result = await checkPSM(tenantId, input);

    reply.send(result);
  });

  // Search PSM in BVL database
  server.get('/psm/search', async (request, reply) => {
    const query = request.query as Record<string, string>;

    if (!query.q) {
      reply.code(400).send({ error: 'BadRequest', message: 'Query parameter "q" is required' });
      return;
    }

    const results = await searchPSM(query.q, {
      activeSubstance: query.activeSubstance,
      crop: query.crop,
    });

    reply.send({ data: results, count: results.length });
  });
}
