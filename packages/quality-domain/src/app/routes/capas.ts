import { FastifyInstance } from 'fastify';
import { CreateCapaSchema, UpdateCapaSchema } from '../../domain/entities/capa';
import {
  createCapa,
  getCapaById,
  updateCapa,
  implementCapa,
  verifyCapa,
  closeCapa,
  escalateCapa,
  listCapas,
  getOverdueCapas,
  getCapaStatistics,
} from '../../domain/services/capa-service';

export async function registerCapaRoutes(server: FastifyInstance): Promise<void> {
  // Create CAPA
  server.post('/capas', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId ?? 'system';

    const data = CreateCapaSchema.parse({ ...(request.body as any), tenantId });
    const capa = await createCapa(data, userId);

    reply.code(201).send(capa);
  });

  // Get CAPA by ID
  server.get('/capas/:id', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };

    const capa = await getCapaById(tenantId, id);
    if (capa === undefined || capa === null) {
      reply.code(404).send({ error: 'NotFound', message: 'CAPA not found' });
      return;
    }

    reply.send(capa);
  });

  // List CAPAs with pagination
  server.get('/capas', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as Record<string, string>;

    const result = await listCapas(
      tenantId,
      {
        status: query.status,
        type: query.type,
        responsibleUserId: query.responsibleUserId,
        overdue: query.overdue === 'true',
        search: query.search,
      } as any,
      {
        page: query.page ? parseInt(query.page) : 1,
        limit: query.limit ? parseInt(query.limit) : 50,
      }
    );

    reply.send(result);
  });

  // Update CAPA
  server.patch('/capas/:id', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId ?? 'system';
    const { id } = request.params as { id: string };

    const data = UpdateCapaSchema.parse(request.body);
    const capa = await updateCapa(tenantId, id, data, userId);

    reply.send(capa);
  });

  // Implement CAPA
  server.post('/capas/:id/implement', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId ?? 'system';
    const { id } = request.params as { id: string };

    const capa = await implementCapa(tenantId, id, userId);
    reply.send(capa);
  });

  // Verify CAPA
  server.post('/capas/:id/verify', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId ?? 'system';
    const { id } = request.params as { id: string };
    const { effectivenessCheck, effectivenessComment } = request.body as {
      effectivenessCheck: boolean;
      effectivenessComment?: string;
    };

    if (typeof effectivenessCheck !== 'boolean') {
      reply.code(400).send({ error: 'BadRequest', message: 'effectivenessCheck is required' });
      return;
    }

    const capa = await verifyCapa(tenantId, id, userId, effectivenessCheck, effectivenessComment);
    reply.send(capa);
  });

  // Close CAPA
  server.post('/capas/:id/close', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId ?? 'system';
    const { id } = request.params as { id: string };
    const { closureComment } = request.body as { closureComment?: string };

    const capa = await closeCapa(tenantId, id, userId, closureComment);
    reply.send(capa);
  });

  // Escalate CAPA
  server.post('/capas/:id/escalate', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };
    const { escalatedTo, reason } = request.body as { escalatedTo: string; reason: string };

    if (!escalatedTo || !reason) {
      reply.code(400).send({ error: 'BadRequest', message: 'escalatedTo and reason are required' });
      return;
    }

    const capa = await escalateCapa(tenantId, id, escalatedTo, reason);
    reply.send(capa);
  });

  // Get overdue CAPAs
  server.get('/capas/overdue', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const capas = await getOverdueCapas(tenantId);
    reply.send({ data: capas, count: capas.length });
  });

  // Get CAPA statistics
  server.get('/capas/stats', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as Record<string, string>;

    const filters: { startDate?: string; endDate?: string } = {};
    if (query.startDate) filters.startDate = query.startDate;
    if (query.endDate) filters.endDate = query.endDate;
    const stats = await getCapaStatistics(tenantId, filters);

    reply.send(stats);
  });
}

