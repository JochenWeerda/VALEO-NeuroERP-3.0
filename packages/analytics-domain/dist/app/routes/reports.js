"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerReportRoutes = registerReportRoutes;
const drizzle_orm_1 = require("drizzle-orm");
const fs_1 = require("fs");
const promises_1 = require("fs/promises");
const report_contracts_1 = require("../../contracts/report-contracts");
const schema_1 = require("../../infra/db/schema");
const report_1 = require("../../domain/entities/report");
const event_factories_1 = require("../../domain/events/event-factories");
const publisher_1 = require("../../infra/messaging/publisher");
async function registerReportRoutes(fastify, db, reportGenerator) {
    fastify.get('/reports', {
        schema: {
            description: 'Get reports with filtering and pagination',
            tags: ['Reports'],
            querystring: report_contracts_1.ReportQuerySchema,
            response: {
                200: report_contracts_1.ReportListResponseSchema,
            },
        },
        handler: async (request, reply) => {
            const query = request.query;
            const conditions = [(0, drizzle_orm_1.eq)(schema_1.reports.tenantId, request.tenantId)];
            if (query.type) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.reports.type, query.type));
            }
            if (query.format) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.reports.format, query.format));
            }
            if (query.from) {
                conditions.push((0, drizzle_orm_1.sql) `${schema_1.reports.generatedAt} >= ${new Date(query.from)}`);
            }
            if (query.to) {
                conditions.push((0, drizzle_orm_1.sql) `${schema_1.reports.generatedAt} <= ${new Date(query.to)}`);
            }
            const page = query.page || 1;
            const pageSize = query.pageSize || 20;
            const offset = (page - 1) * pageSize;
            const results = await db
                .select()
                .from(schema_1.reports)
                .where((0, drizzle_orm_1.and)(...conditions))
                .orderBy((0, drizzle_orm_1.desc)(schema_1.reports.generatedAt))
                .limit(pageSize)
                .offset(offset);
            const totalResult = await db
                .select({ count: (0, drizzle_orm_1.sql) `count(*)` })
                .from(schema_1.reports)
                .where((0, drizzle_orm_1.and)(...conditions));
            const total = totalResult[0]?.count || 0;
            const reportResponses = results.map(row => ({
                id: row.id,
                tenantId: row.tenantId,
                type: row.type,
                parameters: row.parameters,
                generatedAt: row.generatedAt.toISOString(),
                uri: row.uri || undefined,
                format: row.format,
                metadata: row.metadata || {},
                version: row.version,
            }));
            return {
                data: reportResponses,
                pagination: {
                    page,
                    pageSize,
                    total,
                    totalPages: Math.ceil(total / pageSize),
                },
            };
        },
    });
    fastify.get('/reports/:id', {
        schema: {
            description: 'Get a specific report by ID',
            tags: ['Reports'],
            params: {
                type: 'object',
                properties: {
                    id: { type: 'string', format: 'uuid' },
                },
                required: ['id'],
            },
            response: {
                200: report_contracts_1.ReportResponseSchema,
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
                .from(schema_1.reports)
                .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.reports.id, id), (0, drizzle_orm_1.eq)(schema_1.reports.tenantId, request.tenantId)))
                .limit(1);
            if (result.length === 0) {
                return reply.code(404).send({
                    error: 'Not Found',
                    message: 'Report not found',
                });
            }
            const row = result[0];
            if (!row) {
                return reply.code(404).send({
                    error: 'Not Found',
                    message: 'Report not found',
                });
            }
            return {
                id: row.id,
                tenantId: row.tenantId,
                type: row.type,
                parameters: row.parameters,
                generatedAt: row.generatedAt.toISOString(),
                uri: row.uri || undefined,
                format: row.format,
                metadata: row.metadata || {},
                version: row.version,
            };
        },
    });
    fastify.get('/reports/:id/content', {
        schema: {
            description: 'Get report content/data',
            tags: ['Reports'],
            params: {
                type: 'object',
                properties: {
                    id: { type: 'string', format: 'uuid' },
                },
                required: ['id'],
            },
            response: {
                200: report_contracts_1.ReportContentResponseSchema,
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
                .from(schema_1.reports)
                .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.reports.id, id), (0, drizzle_orm_1.eq)(schema_1.reports.tenantId, request.tenantId)))
                .limit(1);
            if (result.length === 0) {
                return reply.code(404).send({
                    error: 'Not Found',
                    message: 'Report not found',
                });
            }
            const row = result[0];
            if (!row) {
                return reply.code(404).send({
                    error: 'Not Found',
                    message: 'Report not found',
                });
            }
            if (row.uri && row.format !== 'json') {
                try {
                    const fileStat = await (0, promises_1.stat)(row.uri);
                    const stream = (0, fs_1.createReadStream)(row.uri);
                    let contentType = 'application/octet-stream';
                    switch (row.format) {
                        case 'csv':
                            contentType = 'text/csv';
                            break;
                        case 'excel':
                            contentType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
                            break;
                        case 'pdf':
                            contentType = 'application/pdf';
                            break;
                    }
                    return reply
                        .header('Content-Type', contentType)
                        .header('Content-Length', fileStat.size)
                        .header('Content-Disposition', `attachment; filename="report-${id}.${row.format}"`)
                        .send(stream);
                }
                catch (error) {
                    return reply.code(500).send({
                        error: 'Internal Server Error',
                        message: 'Failed to read report file',
                    });
                }
            }
            const metadata = row.metadata;
            return {
                report: {
                    id: row.id,
                    tenantId: row.tenantId,
                    type: row.type,
                    parameters: row.parameters,
                    generatedAt: row.generatedAt.toISOString(),
                    uri: row.uri || undefined,
                    format: row.format,
                    metadata: row.metadata || {},
                    version: row.version,
                },
                content: metadata?.data || {},
                contentType: 'application/json',
                contentLength: JSON.stringify(metadata?.data || {}).length,
            };
        },
    });
    fastify.post('/reports', {
        schema: {
            description: 'Generate a new report',
            tags: ['Reports'],
            body: report_contracts_1.GenerateReportRequestSchema,
            response: {
                202: report_contracts_1.ReportResponseSchema,
            },
        },
        handler: async (request, reply) => {
            const body = request.body;
            const reportId = `report-${request.tenantId}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
            setImmediate(async () => {
                try {
                    const startTime = Date.now();
                    const result = await reportGenerator.generateReport(request.tenantId, body.type, body.parameters, body.format);
                    const executionTimeMs = Date.now() - startTime;
                    const report = report_1.Report.create({
                        id: reportId,
                        tenantId: request.tenantId,
                        type: body.type,
                        parameters: body.parameters,
                        format: body.format,
                        metadata: {
                            totalRecords: result.recordCount,
                            executionTimeMs,
                            ...(body.format === 'json' && { data: result.data }),
                        },
                    });
                    if (result.uri) {
                        report.uri = result.uri;
                    }
                    await db.insert(schema_1.reports).values({
                        id: report.id,
                        tenantId: report.tenantId,
                        type: report.type,
                        parameters: report.parameters,
                        generatedAt: report.generatedAt,
                        uri: report.uri,
                        format: report.format,
                        metadata: report.metadata,
                    });
                    const event = (0, event_factories_1.createReportGeneratedEvent)(report, result.recordCount);
                    await (0, publisher_1.getEventPublisher)().publish(event);
                }
                catch (error) {
                    console.error('Report generation failed:', error);
                    await db
                        .update(schema_1.reports)
                        .set({
                        metadata: {
                            error: error instanceof Error ? error.message : 'Unknown error',
                            status: 'failed',
                        },
                        updatedAt: new Date(),
                    })
                        .where((0, drizzle_orm_1.eq)(schema_1.reports.id, reportId));
                }
            });
            return reply.code(202).send({
                id: reportId,
                tenantId: request.tenantId,
                type: body.type,
                parameters: body.parameters,
                generatedAt: new Date().toISOString(),
                format: body.format,
                metadata: {
                    status: 'processing',
                },
                version: 1,
            });
        },
    });
    fastify.delete('/reports/:id', {
        schema: {
            description: 'Delete a report',
            tags: ['Reports'],
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
                    description: 'Report deleted successfully',
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
                .delete(schema_1.reports)
                .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.reports.id, id), (0, drizzle_orm_1.eq)(schema_1.reports.tenantId, request.tenantId)));
            if (result.rowCount === 0) {
                return reply.code(404).send({
                    error: 'Not Found',
                    message: 'Report not found',
                });
            }
            return reply.code(204).send();
        },
    });
}
//# sourceMappingURL=reports.js.map