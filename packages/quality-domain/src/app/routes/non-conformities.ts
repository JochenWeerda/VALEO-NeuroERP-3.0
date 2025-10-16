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
    const userId = request.authContext?.userId ?? 'system';

    const data = CreateNonConformitySchema.parse({ ...request.body as any, tenantId });
    const nc = await createNonConformity(data, userId);

    reply.code(201).send(nc);
  });

  // Get NC by ID
  server.get('/ncs/:id', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };

    const nc = await getNonConformityById(tenantId, id);
    if (nc === undefined || nc === null) {
      reply.code(404).send({ error: 'NotFound', message: 'Non-conformity not found' });
      return;
    }

    reply.send(nc);
  });

  // List NCs with pagination
  server.get('/ncs', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as Record<string, string>;

    const filters: { batchId?: string; contractId?: string; status?: string; severity?: string; type?: string; supplierId?: string; assignedTo?: string; search?: string } = {};
    if (query.batchId) filters.batchId = query.batchId;
    if (query.contractId) filters.contractId = query.contractId;
    if (query.status) filters.status = query.status;
    if (query.severity) filters.severity = query.severity;
    if (query.type) filters.type = query.type;
    if (query.supplierId) filters.supplierId = query.supplierId;
    if (query.assignedTo) filters.assignedTo = query.assignedTo;
    if (query.search) filters.search = query.search;
    
    const result = await listNonConformities(
      tenantId,
      filters,
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
    const userId = request.authContext?.userId ?? 'system';
    const { id } = request.params as { id: string };

    const data = UpdateNonConformitySchema.parse(request.body as any);
    const nc = await updateNonConformity(tenantId, id, data, userId);

    reply.send(nc);
  });

  // Close NC
  server.post('/ncs/:id/close', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId ?? 'system';
    const { id } = request.params as { id: string };
    const { comment } = request.body as any as { comment?: string };

    const nc = await closeNonConformity(tenantId, id, userId, comment);
    reply.send(nc);
  });

  // Assign NC
  server.post('/ncs/:id/assign', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };
    const { assignedTo } = request.body as any as { assignedTo: string };

    if (assignedTo === undefined || assignedTo === null) {
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
    const { capaId } = request.body as any as { capaId: string };

    if (capaId === undefined || capaId === null) {
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

    const statsFilters: { startDate?: string; endDate?: string } = {};
    if (query.startDate) statsFilters.startDate = query.startDate;
    if (query.endDate) statsFilters.endDate = query.endDate;
    const stats = await getNcStatistics(tenantId, statsFilters);

    reply.send(stats);
  });
}

