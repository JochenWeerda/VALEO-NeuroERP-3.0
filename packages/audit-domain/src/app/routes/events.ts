import { FastifyInstance } from 'fastify';
import { CreateAuditEventSchema } from '../../domain/entities/audit-event';
import {
  logAuditEvent,
  getAuditEvents,
  getAuditEventById,
} from '../../domain/services/audit-logger';

export async function registerEventRoutes(server: FastifyInstance): Promise<void> {
  // Create audit event (manual logging)
  server.post('/events', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;

    const input = CreateAuditEventSchema.parse(request.body);
    const event = await logAuditEvent(tenantId, input);

    await reply.code(201).send(event);
  });

  // Get audit event by ID
  server.get('/events/:id', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };

    const event = await getAuditEventById(tenantId, id);
    if (event === undefined || event === null) {
      await reply.code(404).send({ error: 'NotFound', message: 'Audit event not found' });
      return;
    }

    await reply.send(event);
  });

  // Query audit events
  server.get('/events', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as {
      from?: string;
      to?: string;
      actor?: string;
      action?: string;
      targetType?: string;
    };

    const events = await getAuditEvents(tenantId, query);
    await reply.send({ count: events.length, events });
  });
}

