import { FastifyInstance } from 'fastify';
import { CreateNonConformitySchema, UpdateNonConformitySchema } from '../../domain/entities/non-conformity';
import {
  createNonConformity,
  getNonConformityById,
  updateNonConformity,
  closeNonConformity,
  assignNonConformity,
  linkNcToCapa,
  listNonConformities,
  getNcStatistics,
} from '../../domain/services/nc-service';

export async function registerNonConformityRoutes(server: FastifyInstance): Promise<void> {
  // Create NC
  server.post('/ncs', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId || 'system';

    const data = CreateNonConformitySchema.parse({ ...request.body, tenantId });
    const nc = await createNonConformity(data, userId);

    reply.code(201).send(nc);
  });

  // Get NC by ID
  server.get('/ncs/:id', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };

    const nc = await getNonConformityById(tenantId, id);
    if (!nc) {
      reply.code(404).send({ error: 'NotFound', message: 'Non-conformity not found' });
      return;
    }

    reply.send(nc);
  });

  // List NCs with pagination
  server.get('/ncs', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as Record<string, string>;

    const result = await listNonConformities(
      tenantId,
      {
        batchId: query.batchId,
        contractId: query.contractId,
        status: query.status,
        severity: query.severity,
        type: query.type,
        supplierId: query.supplierId,
        assignedTo: query.assignedTo,
        search: query.search,
      },
      {
        page: query.page ? parseInt(query.page) : 1,
        limit: query.limit ? parseInt(query.limit) : 50,
      }
    );

    reply.send(result);
  });

  // Update NC
  server.patch('/ncs/:id', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId || 'system';
    const { id } = request.params as { id: string };

    const data = UpdateNonConformitySchema.parse(request.body);
    const nc = await updateNonConformity(tenantId, id, data, userId);

    reply.send(nc);
  });

  // Close NC
  server.post('/ncs/:id/close', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId || 'system';
    const { id } = request.params as { id: string };
    const { comment } = request.body as { comment?: string };

    const nc = await closeNonConformity(tenantId, id, userId, comment);
    reply.send(nc);
  });

  // Assign NC
  server.post('/ncs/:id/assign', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };
    const { assignedTo } = request.body as { assignedTo: string };

    if (!assignedTo) {
      reply.code(400).send({ error: 'BadRequest', message: 'assignedTo is required' });
      return;
    }

    const nc = await assignNonConformity(tenantId, id, assignedTo);
    reply.send(nc);
  });

  // Link NC to CAPA
  server.post('/ncs/:id/link-capa', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };
    const { capaId } = request.body as { capaId: string };

    if (!capaId) {
      reply.code(400).send({ error: 'BadRequest', message: 'capaId is required' });
      return;
    }

    const nc = await linkNcToCapa(tenantId, id, capaId);
    reply.send(nc);
  });

  // Get NC statistics
  server.get('/ncs/stats', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as Record<string, string>;

    const stats = await getNcStatistics(tenantId, {
      startDate: query.startDate,
      endDate: query.endDate,
    });

    reply.send(stats);
  });
}
