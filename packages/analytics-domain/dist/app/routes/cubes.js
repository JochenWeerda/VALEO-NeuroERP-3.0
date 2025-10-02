"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerCubeRoutes = registerCubeRoutes;
const drizzle_orm_1 = require("drizzle-orm");
const cube_contracts_1 = require("../../contracts/cube-contracts");
const schema_1 = require("../../infra/db/schema");
async function registerCubeRoutes(fastify, db, aggregationService) {
    fastify.get('/cubes/contract-positions', {
        schema: {
            description: 'Get contract position cube data',
            tags: ['Cubes'],
            querystring: cube_contracts_1.ContractPositionQuerySchema,
            response: {
                200: cube_contracts_1.ContractPositionResponseSchema,
            },
        },
        handler: async (request, reply) => {
            const query = request.query;
            const conditions = [(0, drizzle_orm_1.eq)(schema_1.mvContractPositions.tenantId, request.tenantId)];
            if (query.commodity) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvContractPositions.commodity, query.commodity));
            }
            if (query.month) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvContractPositions.month, query.month));
            }
            const page = query.page || 1;
            const pageSize = query.pageSize || 100;
            const offset = (page - 1) * pageSize;
            const results = await db
                .select()
                .from(schema_1.mvContractPositions)
                .where((0, drizzle_orm_1.and)(...conditions))
                .limit(pageSize)
                .offset(offset);
            const summary = {
                totalShort: results.reduce((sum, r) => sum + Number(r.shortPosition || 0), 0),
                totalLong: results.reduce((sum, r) => sum + Number(r.longPosition || 0), 0),
                netExposure: results.reduce((sum, r) => sum + Number(r.netPosition || 0), 0),
                avgHedgingRatio: results.length > 0
                    ? results.reduce((sum, r) => sum + Number(r.hedgingRatio || 0), 0) / results.length
                    : 0,
            };
            return {
                data: results.map(row => ({
                    tenantId: row.tenantId,
                    commodity: row.commodity,
                    month: row.month,
                    shortPosition: row.shortPosition,
                    longPosition: row.longPosition,
                    netPosition: row.netPosition,
                    hedgingRatio: row.hedgingRatio,
                    lastUpdated: row.lastUpdated.toISOString(),
                })),
                summary,
            };
        },
    });
    fastify.get('/cubes/weighing-volumes', {
        schema: {
            description: 'Get weighing volume cube data',
            tags: ['Cubes'],
            querystring: cube_contracts_1.WeighingVolumeQuerySchema,
            response: {
                200: cube_contracts_1.WeighingVolumeResponseSchema,
            },
        },
        handler: async (request, reply) => {
            const query = request.query;
            const conditions = [(0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.tenantId, request.tenantId)];
            if (query.commodity) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.commodity, query.commodity));
            }
            if (query.customerId) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.customerId, query.customerId));
            }
            if (query.siteId) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.siteId, query.siteId));
            }
            if (query.period) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvWeighingVolumes.period, query.period));
            }
            const page = query.page || 1;
            const pageSize = query.pageSize || 100;
            const offset = (page - 1) * pageSize;
            const results = await db
                .select()
                .from(schema_1.mvWeighingVolumes)
                .where((0, drizzle_orm_1.and)(...conditions))
                .limit(pageSize)
                .offset(offset);
            const summary = {
                totalWeight: results.reduce((sum, r) => sum + Number(r.totalWeight || 0), 0),
                totalTickets: results.reduce((sum, r) => sum + Number(r.totalTickets || 0), 0),
                avgWeightPerTicket: results.reduce((sum, r) => sum + Number(r.totalTickets || 0), 0) > 0
                    ? results.reduce((sum, r) => sum + Number(r.totalWeight || 0), 0) /
                        results.reduce((sum, r) => sum + Number(r.totalTickets || 0), 0)
                    : 0,
                overallToleranceRate: results.reduce((sum, r) => sum + Number(r.totalTickets || 0), 0) > 0
                    ? results.reduce((sum, r) => sum + Number(r.withinTolerance || 0), 0) /
                        results.reduce((sum, r) => sum + Number(r.totalTickets || 0), 0)
                    : 0,
            };
            return {
                data: results.map(row => ({
                    tenantId: row.tenantId,
                    commodity: row.commodity,
                    customerId: row.customerId,
                    siteId: row.siteId,
                    period: row.period,
                    totalWeight: row.totalWeight,
                    totalTickets: row.totalTickets,
                    avgWeight: row.avgWeight,
                    withinTolerance: row.withinTolerance,
                    outsideTolerance: row.outsideTolerance,
                    lastUpdated: row.lastUpdated.toISOString(),
                })),
                summary,
            };
        },
    });
    fastify.get('/cubes/quality', {
        schema: {
            description: 'Get quality statistics cube data',
            tags: ['Cubes'],
            querystring: cube_contracts_1.QualityQuerySchema,
            response: {
                200: cube_contracts_1.QualityResponseSchema,
            },
        },
        handler: async (request, reply) => {
            const query = request.query;
            const conditions = [(0, drizzle_orm_1.eq)(schema_1.mvQualityStats.tenantId, request.tenantId)];
            if (query.commodity) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvQualityStats.commodity, query.commodity));
            }
            if (query.period) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvQualityStats.period, query.period));
            }
            const page = query.page || 1;
            const pageSize = query.pageSize || 100;
            const offset = (page - 1) * pageSize;
            const results = await db
                .select()
                .from(schema_1.mvQualityStats)
                .where((0, drizzle_orm_1.and)(...conditions))
                .limit(pageSize)
                .offset(offset);
            const summary = {
                totalSamples: results.reduce((sum, r) => sum + Number(r.totalSamples || 0), 0),
                overallPassRate: results.reduce((sum, r) => sum + Number(r.totalSamples || 0), 0) > 0
                    ? results.reduce((sum, r) => sum + Number(r.passedSamples || 0), 0) /
                        results.reduce((sum, r) => sum + Number(r.totalSamples || 0), 0)
                    : 0,
                avgMoisture: results.length > 0
                    ? results.reduce((sum, r) => sum + Number(r.avgMoisture || 0), 0) / results.length
                    : 0,
                avgProtein: results.length > 0
                    ? results.reduce((sum, r) => sum + Number(r.avgProtein || 0), 0) / results.length
                    : 0,
            };
            return {
                data: results.map(row => ({
                    tenantId: row.tenantId,
                    commodity: row.commodity,
                    period: row.period,
                    totalSamples: row.totalSamples,
                    passedSamples: row.passedSamples,
                    failedSamples: row.failedSamples,
                    passRate: row.passRate,
                    failureRate: row.failureRate,
                    avgMoisture: row.avgMoisture,
                    avgProtein: row.avgProtein,
                    lastUpdated: row.lastUpdated.toISOString(),
                })),
                summary,
            };
        },
    });
    fastify.get('/cubes/regulatory', {
        schema: {
            description: 'Get regulatory compliance cube data',
            tags: ['Cubes'],
            querystring: cube_contracts_1.RegulatoryQuerySchema,
            response: {
                200: cube_contracts_1.RegulatoryResponseSchema,
            },
        },
        handler: async (request, reply) => {
            const query = request.query;
            const conditions = [(0, drizzle_orm_1.eq)(schema_1.mvRegulatoryStats.tenantId, request.tenantId)];
            if (query.commodity) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvRegulatoryStats.commodity, query.commodity));
            }
            if (query.labelType) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvRegulatoryStats.labelType, query.labelType));
            }
            if (query.period) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvRegulatoryStats.period, query.period));
            }
            const page = query.page || 1;
            const pageSize = query.pageSize || 100;
            const offset = (page - 1) * pageSize;
            const results = await db
                .select()
                .from(schema_1.mvRegulatoryStats)
                .where((0, drizzle_orm_1.and)(...conditions))
                .limit(pageSize)
                .offset(offset);
            const summary = {
                totalEligible: results.reduce((sum, r) => sum + (r.totalEligible || 0), 0),
                totalIneligible: results.reduce((sum, r) => sum + (r.totalIneligible || 0), 0),
                overallEligibilityRate: results.reduce((sum, r) => sum + ((r.totalEligible || 0) + (r.totalIneligible || 0)), 0) > 0
                    ? results.reduce((sum, r) => sum + (r.totalEligible || 0), 0) /
                        results.reduce((sum, r) => sum + ((r.totalEligible || 0) + (r.totalIneligible || 0)), 0)
                    : 0,
            };
            return {
                data: results.map(row => ({
                    tenantId: row.tenantId,
                    commodity: row.commodity,
                    labelType: row.labelType,
                    period: row.period,
                    totalEligible: row.totalEligible,
                    totalIneligible: row.totalIneligible,
                    eligibilityRate: row.eligibilityRate,
                    ineligibilityRate: row.ineligibilityRate,
                    lastUpdated: row.lastUpdated.toISOString(),
                })),
                summary,
            };
        },
    });
    fastify.get('/cubes/finance', {
        schema: {
            description: 'Get finance KPIs cube data',
            tags: ['Cubes'],
            querystring: cube_contracts_1.FinanceQuerySchema,
            response: {
                200: cube_contracts_1.FinanceResponseSchema,
            },
        },
        handler: async (request, reply) => {
            const query = request.query;
            const conditions = [(0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.tenantId, request.tenantId)];
            if (query.commodity) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.commodity, query.commodity));
            }
            if (query.customerId) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.customerId, query.customerId));
            }
            if (query.period) {
                conditions.push((0, drizzle_orm_1.eq)(schema_1.mvFinanceKpis.period, query.period));
            }
            const page = query.page || 1;
            const pageSize = query.pageSize || 100;
            const offset = (page - 1) * pageSize;
            const results = await db
                .select()
                .from(schema_1.mvFinanceKpis)
                .where((0, drizzle_orm_1.and)(...conditions))
                .limit(pageSize)
                .offset(offset);
            const summary = {
                totalRevenue: results.reduce((sum, r) => sum + Number(r.totalRevenue || 0), 0),
                totalCost: results.reduce((sum, r) => sum + Number(r.totalCost || 0), 0),
                totalMargin: results.reduce((sum, r) => sum + Number(r.grossMargin || 0), 0),
                avgMarginPercentage: results.length > 0
                    ? results.reduce((sum, r) => sum + Number(r.marginPercentage || 0), 0) / results.length
                    : 0,
                totalOutstanding: results.reduce((sum, r) => sum + Number(r.outstandingInvoices || 0), 0),
                totalOverdue: results.reduce((sum, r) => sum + Number(r.overdueInvoices || 0), 0),
            };
            return {
                data: results.map(row => ({
                    tenantId: row.tenantId,
                    commodity: row.commodity,
                    customerId: row.customerId,
                    period: row.period,
                    totalRevenue: row.totalRevenue,
                    totalCost: row.totalCost,
                    grossMargin: row.grossMargin,
                    marginPercentage: row.marginPercentage,
                    outstandingInvoices: row.outstandingInvoices,
                    overdueInvoices: row.overdueInvoices,
                    lastUpdated: row.lastUpdated.toISOString(),
                })),
                summary,
            };
        },
    });
    fastify.post('/cubes/refresh', {
        schema: {
            description: 'Refresh cube materialized views',
            tags: ['Cubes'],
            body: cube_contracts_1.CubeRefreshRequestSchema,
            response: {
                200: cube_contracts_1.BulkCubeRefreshResponseSchema,
            },
        },
        handler: async (request, reply) => {
            const body = request.body;
            const cubeNames = body.cubeNames || [
                'contractPositions',
                'qualityStats',
                'regulatoryStats',
                'financeKpis',
                'weighingVolumes',
            ];
            const results = [];
            for (const cubeName of cubeNames) {
                const startTime = Date.now();
                try {
                    let result;
                    switch (cubeName) {
                        case 'contractPositions':
                            result = await aggregationService.refreshContractPositions(request.tenantId);
                            break;
                        case 'qualityStats':
                            result = await aggregationService.refreshQualityStats(request.tenantId);
                            break;
                        case 'regulatoryStats':
                            result = await aggregationService.refreshRegulatoryStats(request.tenantId);
                            break;
                        case 'financeKpis':
                            result = await aggregationService.refreshFinanceKpis(request.tenantId);
                            break;
                        case 'weighingVolumes':
                            result = await aggregationService.refreshWeighingVolumes(request.tenantId);
                            break;
                        default:
                            result = {
                                success: false,
                                recordCount: 0,
                                executionTimeMs: Date.now() - startTime,
                                error: `Unknown cube: ${cubeName}`,
                            };
                    }
                    results.push({
                        cubeName,
                        success: result.success,
                        recordCount: result.recordCount,
                        executionTimeMs: result.executionTimeMs,
                        error: result.error,
                        refreshedAt: new Date().toISOString(),
                    });
                }
                catch (error) {
                    results.push({
                        cubeName,
                        success: false,
                        recordCount: 0,
                        executionTimeMs: Date.now() - startTime,
                        error: error instanceof Error ? error.message : 'Unknown error',
                        refreshedAt: new Date().toISOString(),
                    });
                }
            }
            const totalExecutionTimeMs = results.reduce((sum, r) => sum + r.executionTimeMs, 0);
            return {
                totalRequested: cubeNames.length,
                successful: results.filter(r => r.success).length,
                failed: results.filter(r => !r.success).length,
                results,
                totalExecutionTimeMs,
            };
        },
    });
    fastify.get('/cubes/status', {
        schema: {
            description: 'Get cube refresh status and record counts',
            tags: ['Cubes'],
            response: {
                200: {
                    type: 'object',
                    properties: {
                        lastRefresh: {
                            type: 'object',
                            properties: {
                                contractPositions: { type: 'string', format: 'date-time', nullable: true },
                                qualityStats: { type: 'string', format: 'date-time', nullable: true },
                                regulatoryStats: { type: 'string', format: 'date-time', nullable: true },
                                financeKpis: { type: 'string', format: 'date-time', nullable: true },
                                weighingVolumes: { type: 'string', format: 'date-time', nullable: true },
                            },
                        },
                        recordCounts: {
                            type: 'object',
                            properties: {
                                contractPositions: { type: 'integer' },
                                qualityStats: { type: 'integer' },
                                regulatoryStats: { type: 'integer' },
                                financeKpis: { type: 'integer' },
                                weighingVolumes: { type: 'integer' },
                            },
                        },
                    },
                },
            },
        },
        handler: async (request, reply) => {
            const status = await aggregationService.getAggregationStatus(request.tenantId);
            return {
                lastRefresh: {
                    contractPositions: status.lastRefresh.contractPositions?.toISOString(),
                    qualityStats: status.lastRefresh.qualityStats?.toISOString(),
                    regulatoryStats: status.lastRefresh.regulatoryStats?.toISOString(),
                    financeKpis: status.lastRefresh.financeKpis?.toISOString(),
                    weighingVolumes: status.lastRefresh.weighingVolumes?.toISOString(),
                },
                recordCounts: status.recordCounts,
            };
        },
    });
}
//# sourceMappingURL=cubes.js.map