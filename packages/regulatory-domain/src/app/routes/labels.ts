import { FastifyInstance } from 'fastify';
import { LabelEvaluateInputSchema } from '../../domain/entities/label';
import { evaluateLabel, createOrUpdateLabel } from '../../domain/services/label-evaluation-service';
import { db } from '../../infra/db/connection';
import { labels } from '../../infra/db/schema';
import { eq, and } from 'drizzle-orm';

export async function registerLabelRoutes(server: FastifyInstance): Promise<void> {
  // Evaluate label eligibility
  server.post('/labels/evaluate', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId || 'system';

    const input = LabelEvaluateInputSchema.parse({ ...request.body, tenantId });
    const evaluation = await evaluateLabel(tenantId, input);

    // Optional: Create/Update label record
    if (request.query && (request.query as any).persist === 'true') {
      const label = await createOrUpdateLabel(tenantId, input, evaluation, userId);
      reply.send({ evaluation, label });
    } else {
      reply.send(evaluation);
    }
  });

  // Get label by ID
  server.get('/labels/:id', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };

    const [label] = await db
      .select()
      .from(labels)
      .where(and(eq(labels.id, id), eq(labels.tenantId, tenantId)))
      .limit(1);

    if (!label) {
      reply.code(404).send({ error: 'NotFound', message: 'Label not found' });
      return;
    }

    reply.send(label);
  });

  // List labels for target
  server.get('/labels', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as Record<string, string>;

    let dbQuery = db.select().from(labels).where(eq(labels.tenantId, tenantId));

    const results = await dbQuery;

    let filtered = results;
    if (query.targetType && query.targetId) {
      filtered = filtered.filter(l => l.targetType === query.targetType && l.targetId === query.targetId);
    }
    if (query.code) {
      filtered = filtered.filter(l => l.code === query.code);
    }
    if (query.status) {
      filtered = filtered.filter(l => l.status === query.status);
    }

    reply.send({ data: filtered, count: filtered.length });
  });

  // Revoke label
  server.post('/labels/:id/revoke', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId || 'system';
    const { id } = request.params as { id: string };
    const { reason } = request.body as { reason: string };

    const [revoked] = await db
      .update(labels)
      .set({
        status: 'Ineligible',
        revokedAt: new Date(),
        revokedBy: userId,
        revokedReason: reason,
        updatedAt: new Date(),
      })
      .where(and(eq(labels.id, id), eq(labels.tenantId, tenantId)))
      .returning();

    if (!revoked) {
      reply.code(404).send({ error: 'NotFound', message: 'Label not found' });
      return;
    }

    reply.send(revoked);
  });
}
