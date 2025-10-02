"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerKpiRoutes = registerKpiRoutes;
const drizzle_orm_1 = require("drizzle-orm");
const kpi_contracts_1 = require("../../contracts/kpi-contracts");
const schema_1 = require("../../infra/db/schema");
const kpi_calculation_engine_1 = require("../../domain/services/kpi-calculation-engine");
const event_factories_1 = require("../../domain/events/event-factories");
const publisher_1 = require("../../infra/messaging/publisher");
async function registerKpiRoutes(fastify, db) {
    const kpiEngine = new kpi_calculation_engine_1.KpiCalculationEngine(db);
    fastify.get('/kpis', {
        schema: {
            description: 'Get KPIs with filtering and pagination',
            tags: ['KPIs'],
            querystring: kpi_contracts_1.KpiQuerySchema,
            response: {
                200: kpi_contracts_1.KpiListResponseSchema,
            },
        },
        handler: async (request, reply) => {
            const query = request.query;
            let dbQuery = db
                .select()
                .from(schema_1.kpis)
                .where((0, drizzle_orm_1.eq)(schema_1.kpis.tenantId, request.tenantId))
                .orderBy((0, drizzle_orm_1.desc)(schema_1.kpis.calculatedAt));
            if (query.name) {
                dbQuery = dbQuery.where(schema_1.kpis.name.ilike(`%${query.name}%`));
            }
            if (query.from) {
                dbQuery = dbQuery.where(sql `${schema_1.kpis.calculatedAt} >= ${new Date(query.from)}`);
            }
            if (query.to) {
                dbQuery = dbQuery.where(sql `${schema_1.kpis.calculatedAt} <= ${new Date(query.to)}`);
            }
            const page = query.page || 1;
            const pageSize = query.pageSize || 20;
            const offset = (page - 1) * pageSize;
            dbQuery = dbQuery.limit(pageSize).offset(offset);
            const results = await dbQuery;
            const totalQuery = db
                .select({ count: sql `count(*)` })
                .from(schema_1.kpis)
                .where((0, drizzle_orm_1.eq)(schema_1.kpis.tenantId, request.tenantId));
            const totalResult = await totalQuery;
            const total = totalResult[0]?.count || 0;
            const kpiResponses = results.map(row => ({
                id: row.id,
                tenantId: row.tenantId,
                name: row.name,
                description: row.description,
                value: JSON.parse(row.value),
                unit: row.unit,
                context: row.context || {},
                calculatedAt: row.calculatedAt.toISOString(),
                metadata: row.metadata || {},
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
                200: kpi_contracts_1.KpiResponseSchema,
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
            const { id } = request.params;
            const result = await db
                .select()
                .from(schema_1.kpis)
                .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.kpis.id, id), (0, drizzle_orm_1.eq)(schema_1.kpis.tenantId, request.tenantId)))
                .limit(1);
            if (result.length === 0) {
                return reply.code(404).send({
                    error: 'Not Found',
                    message: 'KPI not found',
                });
            }
            const row = result[0];
            return {
                id: row.id,
                tenantId: row.tenantId,
                name: row.name,
                description: row.description,
                value: JSON.parse(row.value),
                unit: row.unit,
                context: row.context || {},
                calculatedAt: row.calculatedAt.toISOString(),
                metadata: row.metadata || {},
                version: row.version,
            };
        },
    });
    fastify.post('/kpis', {
        schema: {
            description: 'Create a new KPI',
            tags: ['KPIs'],
            body: kpi_contracts_1.CreateKpiRequestSchema,
            response: {
                201: kpi_contracts_1.KpiResponseSchema,
            },
        },
        handler: async (request, reply) => {
            const body = request.body;
            const kpiData = {
                id: `kpi-${request.tenantId}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                tenantId: request.tenantId,
                name: body.name,
                description: body.description,
                value: JSON.stringify(body.value),
                unit: body.unit,
                context: body.context || {},
                calculatedAt: new Date(),
                metadata: body.metadata || {},
            };
            await db.insert(schema_1.kpis).values(kpiData);
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
            };
            const event = (0, event_factories_1.createKpiCalculatedEvent)(kpi);
            await (0, publisher_1.getEventPublisher)().publish(event);
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
            body: kpi_contracts_1.UpdateKpiRequestSchema,
            response: {
                200: kpi_contracts_1.KpiResponseSchema,
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
            const { id } = request.params;
            const body = request.body;
            const existing = await db
                .select()
                .from(schema_1.kpis)
                .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.kpis.id, id), (0, drizzle_orm_1.eq)(schema_1.kpis.tenantId, request.tenantId)))
                .limit(1);
            if (existing.length === 0) {
                return reply.code(404).send({
                    error: 'Not Found',
                    message: 'KPI not found',
                });
            }
            const updateData = {
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
                .update(schema_1.kpis)
                .set(updateData)
                .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.kpis.id, id), (0, drizzle_orm_1.eq)(schema_1.kpis.tenantId, request.tenantId)));
            const updated = await db
                .select()
                .from(schema_1.kpis)
                .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.kpis.id, id), (0, drizzle_orm_1.eq)(schema_1.kpis.tenantId, request.tenantId)))
                .limit(1);
            const row = updated[0];
            return {
                id: row.id,
                tenantId: row.tenantId,
                name: row.name,
                description: row.description,
                value: JSON.parse(row.value),
                unit: row.unit,
                context: row.context || {},
                calculatedAt: row.calculatedAt.toISOString(),
                metadata: row.metadata || {},
                version: row.version,
            };
        },
    });
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
            const { id } = request.params;
            const result = await db
                .delete(schema_1.kpis)
                .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.kpis.id, id), (0, drizzle_orm_1.eq)(schema_1.kpis.tenantId, request.tenantId)));
            if (result.rowCount === 0) {
                return reply.code(404).send({
                    error: 'Not Found',
                    message: 'KPI not found',
                });
            }
            return reply.code(204).send();
        },
    });
    fastify.post('/kpis/recalculate', {
        schema: {
            description: 'Recalculate KPIs based on current data',
            tags: ['KPIs'],
            body: kpi_contracts_1.RecalculateKpisRequestSchema,
            response: {
                200: kpi_contracts_1.BulkKpiRecalculationResponseSchema,
            },
        },
        handler: async (request, reply) => {
            const body = request.body;
            const context = {
                tenantId: request.tenantId,
                startDate: body.from ? new Date(body.from) : undefined,
                endDate: body.to ? new Date(body.to) : undefined,
            };
            const result = await kpiEngine.calculateAllKpis(context);
            for (const calcResult of result.results) {
                if (calcResult.success) {
                    const event = (0, event_factories_1.createKpiCalculatedEvent)(calcResult.kpi);
                    await (0, publisher_1.getEventPublisher)().publish(event);
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
//# sourceMappingURL=kpis.js.map