import type { FastifyInstance } from 'fastify';
import { eq, and, desc, sql, ilike } from 'drizzle-orm';
import { drizzle } from 'drizzle-orm/node-postgres';
import {
  CreateKpiRequestSchema,
  UpdateKpiRequestSchema,
  KpiResponseSchema,
  KpiQuerySchema,
  KpiListResponseSchema,
  RecalculateKpisRequestSchema,
  BulkKpiRecalculationResponseSchema,
} from '../../contracts/kpi-contracts';
import { kpis } from '../../infra/db/schema';
import { KpiCalculationEngine } from '../../domain/services/kpi-calculation-engine';
import { createKpiCalculatedEvent } from '../../domain/events/event-factories';
import { getEventPublisher } from '../../infra/messaging/publisher';

export async function registerKpiRoutes(fastify: FastifyInstance, db: ReturnType<typeof drizzle>) {
  const kpiEngine = new KpiCalculationEngine(db);

  // GET /kpis - List KPIs with filtering and pagination
  fastify.get('/kpis', {
    schema: {
      description: 'Get KPIs with filtering and pagination',
      tags: ['KPIs'],
      querystring: KpiQuerySchema,
      response: {
        200: KpiListResponseSchema,
      },
    },
    handler: async (request, _reply) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const query = request.query as any;

      // Build where conditions
      const conditions = [eq(kpis.tenantId, request.tenantId)];

      // Apply filters
      if (query.name != null && query.name !== '') {
        conditions.push(ilike(kpis.name, `%${query.name}%`));
      }

      if (query.from != null && query.from !== '') {
        conditions.push(sql`${kpis.calculatedAt} >= ${new Date(query.from)}`);
      }

      if (query.to != null && query.to !== '') {
        conditions.push(sql`${kpis.calculatedAt} <= ${new Date(query.to)}`);
      }

      // Pagination
      const DEFAULT_PAGE = 1;
      const DEFAULT_PAGE_SIZE = 20;
      const page = (query.page != null && query.page !== 0) ? query.page : DEFAULT_PAGE;
      const pageSize = (query.pageSize != null && query.pageSize !== 0) ? query.pageSize : DEFAULT_PAGE_SIZE;
      const offset = (page - 1) * pageSize;

      const results = await db
        .select()
        .from(kpis)
        .where(and(...conditions))
        .orderBy(desc(kpis.calculatedAt))
        .limit(pageSize)
        .offset(offset);

      // Get total count for pagination
      const totalQuery = db
        .select({ count: sql<number>`count(*)` })
        .from(kpis)
        .where(eq(kpis.tenantId, request.tenantId));

      const totalResult = await totalQuery;
      const total = totalResult[0]?.count ?? 0;

      const kpiResponses = results.map(row => ({
        id: row.id,
        tenantId: row.tenantId,
        name: row.name,
        description: row.description,
        value: JSON.parse(row.value), // Parse stored JSON value
        unit: row.unit,
        context: (row.context != null && typeof row.context === 'object') ? row.context : {},
        calculatedAt: row.calculatedAt.toISOString(),
        metadata: (row.metadata != null && typeof row.metadata === 'object') ? row.metadata : {},
        version: row.version,
      }));

      return {
        data: kpiResponses,
        pagination: {
          page,
          pageSize,
          total,
          totalPages: Math.ceil(total / pageSize),
        },
      };
    },
  });

  // GET /kpis/:id - Get specific KPI
  fastify.get('/kpis/:id', {
    schema: {
      description: 'Get a specific KPI by ID',
      tags: ['KPIs'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' },
        },
        required: ['id'],
      },
      response: {
        200: KpiResponseSchema,
        404: {
          type: 'object',
          properties: {
            error: { type: 'string' },
            message: { type: 'string' },
          },
        },
      },
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };

      const result = await db
        .select()
        .from(kpis)
        .where(and(
          eq(kpis.id, id),
          eq(kpis.tenantId, request.tenantId)
        ))
        .limit(1);

      if (result.length === 0) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'KPI not found',
        });
      }

      const row = result[0];
      if (row == null) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'KPI not found',
        });
      }

      return {
        id: row.id,
        tenantId: row.tenantId,
        name: row.name,
        description: row.description,
        value: JSON.parse(row.value),
        unit: row.unit,
        context: (row.context != null && typeof row.context === 'object') ? row.context : {},
        calculatedAt: row.calculatedAt.toISOString(),
        metadata: (row.metadata != null && typeof row.metadata === 'object') ? row.metadata : {},
        version: row.version,
      };
    },
  });

  // POST /kpis - Create a new KPI
  fastify.post('/kpis', {
    schema: {
      description: 'Create a new KPI',
      tags: ['KPIs'],
      body: CreateKpiRequestSchema,
      response: {
        201: KpiResponseSchema,
      },
    },
    handler: async (request, reply) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const body = request.body as any;

      const RANDOM_ID_BASE = 36;
      const RANDOM_ID_START = 2;
      const RANDOM_ID_LENGTH = 9;
      const kpiData = {
        id: `kpi-${request.tenantId}-${Date.now()}-${Math.random().toString(RANDOM_ID_BASE).substr(RANDOM_ID_START, RANDOM_ID_LENGTH)}`,
        tenantId: request.tenantId,
        name: body.name,
        description: body.description,
        value: JSON.stringify(body.value), // Store as JSON string
        unit: body.unit,
        context: (body.context != null && typeof body.context === 'object') ? body.context : {},
        calculatedAt: new Date(),
        metadata: (body.metadata != null && typeof body.metadata === 'object') ? body.metadata : {},
      };

      await db.insert(kpis).values(kpiData);

      // Publish domain event
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const kpi = {
        id: kpiData.id,
        tenantId: kpiData.tenantId,
        name: kpiData.name,
        description: kpiData.description,
        value: body.value,
        unit: kpiData.unit,
        context: kpiData.context,
        calculatedAt: kpiData.calculatedAt,
        metadata: kpiData.metadata,
        version: 1,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      } as any;

      const event = createKpiCalculatedEvent(kpi);
      await getEventPublisher().publish(event);

      return reply.code(201).send({
        id: kpiData.id,
        tenantId: kpiData.tenantId,
        name: kpiData.name,
        description: kpiData.description,
        value: body.value,
        unit: kpiData.unit,
        context: kpiData.context,
        calculatedAt: kpiData.calculatedAt.toISOString(),
        metadata: kpiData.metadata,
        version: 1,
      });
    },
  });

  // PATCH /kpis/:id - Update KPI
  fastify.patch('/kpis/:id', {
    schema: {
      description: 'Update an existing KPI',
      tags: ['KPIs'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' },
        },
        required: ['id'],
      },
      body: UpdateKpiRequestSchema,
      response: {
        200: KpiResponseSchema,
        404: {
          type: 'object',
          properties: {
            error: { type: 'string' },
            message: { type: 'string' },
          },
        },
      },
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const body = request.body as any;

      // Check if KPI exists
      const existing = await db
        .select()
        .from(kpis)
        .where(and(
          eq(kpis.id, id),
          eq(kpis.tenantId, request.tenantId)
        ))
        .limit(1);

      if (existing.length === 0) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'KPI not found',
        });
      }

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const updateData: any = {
        updatedAt: new Date(),
      };

      if (body.value !== undefined) {
        updateData.value = JSON.stringify(body.value);
      }

      if (body.context !== undefined) {
        updateData.context = body.context;
      }

      if (body.metadata !== undefined) {
        updateData.metadata = body.metadata;
      }

      await db
        .update(kpis)
        .set(updateData)
        .where(and(
          eq(kpis.id, id),
          eq(kpis.tenantId, request.tenantId)
        ));

      // Get updated KPI
      const updated = await db
        .select()
        .from(kpis)
        .where(and(
          eq(kpis.id, id),
          eq(kpis.tenantId, request.tenantId)
        ))
        .limit(1);

      const row = updated[0];
      if (row == null) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'KPI not found',
        });
      }

      return {
        id: row.id,
        tenantId: row.tenantId,
        name: row.name,
        description: row.description,
        value: JSON.parse(row.value),
        unit: row.unit,
        context: (row.context != null && typeof row.context === 'object') ? row.context : {},
        calculatedAt: row.calculatedAt.toISOString(),
        metadata: (row.metadata != null && typeof row.metadata === 'object') ? row.metadata : {},
        version: row.version,
      };
    },
  });

  // DELETE /kpis/:id - Delete KPI
  fastify.delete('/kpis/:id', {
    schema: {
      description: 'Delete a KPI',
      tags: ['KPIs'],
      params: {
        type: 'object',
        properties: {
          id: { type: 'string', format: 'uuid' },
        },
        required: ['id'],
      },
      response: {
        204: {
          type: 'null',
          description: 'KPI deleted successfully',
        },
        404: {
          type: 'object',
          properties: {
            error: { type: 'string' },
            message: { type: 'string' },
          },
        },
      },
    },
    handler: async (request, reply) => {
      const { id } = request.params as { id: string };

      const result = await db
        .delete(kpis)
        .where(and(
          eq(kpis.id, id),
          eq(kpis.tenantId, request.tenantId)
        ));

      if (result.rowCount === 0) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'KPI not found',
        });
      }

      return reply.code(204).send();
    },
  });

  // POST /kpis/recalculate - Recalculate KPIs
  fastify.post('/kpis/recalculate', {
    schema: {
      description: 'Recalculate KPIs based on current data',
      tags: ['KPIs'],
      body: RecalculateKpisRequestSchema,
      response: {
        200: BulkKpiRecalculationResponseSchema,
      },
    },
    handler: async (request, _reply) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const body = request.body as any;

      const context = {
        tenantId: request.tenantId,
        startDate: (body.from != null && body.from !== '') ? new Date(body.from) : undefined,
        endDate: (body.to != null && body.to !== '') ? new Date(body.to) : undefined,
      };

      const result = await kpiEngine.calculateAllKpis(context);

      // Publish events for successful calculations
      for (const calcResult of result.results) {
        if (calcResult.success) {
          const event = createKpiCalculatedEvent(calcResult.kpi);
          await getEventPublisher().publish(event);
        }
      }

      return {
        totalRequested: result.summary.total,
        successful: result.summary.successful,
        failed: result.summary.failed,
        results: result.results.map(r => ({
          kpiId: r.kpi.id,
          kpiName: r.kpi.name,
          success: r.success,
          value: r.success ? r.kpi.value : undefined,
          error: r.error,
          executionTimeMs: r.executionTimeMs,
        })),
        executionTimeMs: result.summary.totalExecutionTimeMs,
      };
    },
  });
}

// Extend FastifyRequest to include tenantId
declare module 'fastify' {
  interface FastifyRequest {
    tenantId: string;
  }
}