import { FastifyInstance } from 'fastify';
import { CreateQualityPlanSchema, UpdateQualityPlanSchema } from '../../domain/entities/quality-plan';
import {
  createQualityPlan,
  getQualityPlanById,
  updateQualityPlan,
  listQualityPlans,
  deactivateQualityPlan,
} from '../../domain/services/quality-plan-service';

export async function registerQualityPlanRoutes(server: FastifyInstance): Promise<void> {
  // Create quality plan
  server.post('/plans', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId ?? 'system';

    const data = CreateQualityPlanSchema.parse({ ...request.body, tenantId });
    const plan = await createQualityPlan(data, userId);

    reply.code(201).send(plan);
  });

  // Get quality plan by ID
  server.get('/plans/:id', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };

    const plan = await getQualityPlanById(tenantId, id);
    if (plan === undefined || plan === null) {
      reply.code(404).send({ error: 'NotFound', message: 'Quality plan not found' });
      return;
    }

    reply.send(plan);
  });

  // List quality plans
  server.get('/plans', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as Record<string, string>;

    const plans = await listQualityPlans(tenantId, {
      commodity: query.commodity,
      contractId: query.contractId,
      active: query.active === 'true',
    });

    reply.send({ data: plans, count: plans.length });
  });

  // Update quality plan
  server.patch('/plans/:id', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId ?? 'system';
    const { id } = request.params as { id: string };

    const data = UpdateQualityPlanSchema.parse(request.body);
    const plan = await updateQualityPlan(tenantId, id, data, userId);

    reply.send(plan);
  });

  // Deactivate quality plan
  server.post('/plans/:id/deactivate', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId ?? 'system';
    const { id } = request.params as { id: string };

    await deactivateQualityPlan(tenantId, id, userId);
    reply.code(204).send();
  });
}

