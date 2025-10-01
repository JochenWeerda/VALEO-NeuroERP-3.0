import { FastifyInstance } from 'fastify';
import { GHGCalculationInputSchema } from '../../domain/entities/ghg-pathway';
import { calculateGHG, getGHGPathways } from '../../domain/services/ghg-calculation-service';

export async function registerGHGRoutes(server: FastifyInstance): Promise<void> {
  // Calculate GHG emissions
  server.post('/ghg/calc', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId || 'system';

    const input = GHGCalculationInputSchema.parse(request.body);
    const pathway = await calculateGHG(tenantId, input, userId);

    reply.code(201).send(pathway);
  });

  // Get GHG pathways
  server.get('/ghg/pathways', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as Record<string, string>;

    const pathways = await getGHGPathways(tenantId, {
      commodity: query.commodity,
      method: query.method,
    });

    reply.send({ data: pathways, count: pathways.length });
  });
}
