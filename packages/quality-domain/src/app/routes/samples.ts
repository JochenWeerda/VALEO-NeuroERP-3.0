import { FastifyInstance } from 'fastify';
import { CreateSampleSchema, CreateSampleResultSchema } from '../../domain/entities/sample';
import {
  createSample,
  getSampleById,
  addSampleResult,
  analyzeSample,
  getSampleResults,
  listSamples,
} from '../../domain/services/sample-service';

export async function registerSampleRoutes(server: FastifyInstance): Promise<void> {
  // Create sample
  server.post('/samples', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const userId = request.authContext?.userId ?? 'system';

    const data = CreateSampleSchema.parse({ ...request.body as any, tenantId });
    const sample = await createSample(data, userId);

    reply.code(201).send(sample);
  });

  // Get sample by ID
  server.get('/samples/:id', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };

    const sample = await getSampleById(tenantId, id);
    if (sample === undefined || sample === null) {
      reply.code(404).send({ error: 'NotFound', message: 'Sample not found' });
      return;
    }

    reply.send(sample);
  });

  // List samples
  server.get('/samples', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const query = request.query as Record<string, string>;

    const filters: { batchId?: string; contractId?: string; status?: string; source?: string } = {};
    if (query.batchId) filters.batchId = query.batchId;
    if (query.contractId) filters.contractId = query.contractId;
    if (query.status) filters.status = query.status;
    if (query.source) filters.source = query.source;
    const samples = await listSamples(tenantId, filters);

    reply.send({ data: samples, count: samples.length });
  });

  // Add sample result
  server.post('/samples/:id/results', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };

    const data = CreateSampleResultSchema.parse({ ...request.body as any, tenantId, sampleId: id });
    const result = await addSampleResult(data);

    reply.code(201).send(result);
  });

  // Get sample results
  server.get('/samples/:id/results', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };

    const results = await getSampleResults(tenantId, id);
    reply.send({ data: results, count: results.length });
  });

  // Analyze sample
  server.post('/samples/:id/analyze', async (request, reply) => {
    const tenantId = request.headers['x-tenant-id'] as string;
    const { id } = request.params as { id: string };

    const result = await analyzeSample(tenantId, id);
    reply.send(result);
  });
}

