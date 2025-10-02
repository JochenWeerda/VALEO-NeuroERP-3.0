"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerForecastRoutes = registerForecastRoutes;
const drizzle_orm_1 = require("drizzle-orm");
const forecast_contracts_1 = require("../../contracts/forecast-contracts");
const schema_1 = require("../../infra/db/schema");
async function registerForecastRoutes(fastify, db, forecastingService) {
    fastify.get('/forecasts', {
        schema: {
            description: 'Get forecasts with filtering and pagination',
            tags: ['Forecasts'],
            querystring: forecast_contracts_1.ForecastQuerySchema,
            response: {
                200: forecast_contracts_1.ForecastListResponseSchema,
            },
        },
        handler: async (request, reply) => {
            const query = request.query;
            const filters = {
                metricName: query.metricName,
                model: query.model,
                fromDate: query.from ? new Date(query.from) : undefined,
                toDate: query.to ? new Date(query.to) : undefined,
                limit: query.pageSize || 20,
                offset: ((query.page || 1) - 1) * (query.pageSize || 20),
            };
            const forecastResults = await forecastingService.getForecasts(request.tenantId, filters);
            const forecastResponses = forecastResults.map(f => ({
                id: f.id,
                tenantId: f.tenantId,
                metricName: f.metricName,
                horizon: f.horizon,
                horizonUnit: f.horizonUnit,
                model: f.model,
                forecastValues: f.forecastValues.map(fv => ({
                    timestamp: fv.timestamp.toISOString(),
                    value: fv.value,
                    lowerBound: fv.lowerBound,
                    upperBound: fv.upperBound,
                    confidence: fv.confidence,
                })),
                confidenceInterval: f.confidenceInterval,
                createdAt: f.createdAt.toISOString(),
                metadata: f.metadata,
                version: f.version,
            }));
            const totalConditions = [(0, drizzle_orm_1.eq)(schema_1.forecasts.tenantId, request.tenantId)];
            if (query.metricName) {
                totalConditions.push((0, drizzle_orm_1.eq)(schema_1.forecasts.metricName, query.metricName));
            }
            if (query.model) {
                totalConditions.push((0, drizzle_orm_1.eq)(schema_1.forecasts.model, query.model));
            }
            const totalResult = await db
                .select({ count: (0, drizzle_orm_1.sql) `count(*)` })
                .from(schema_1.forecasts)
                .where((0, drizzle_orm_1.and)(...totalConditions));
            const total = totalResult[0]?.count || 0;
            return {
                data: forecastResponses,
                pagination: {
                    page: query.page || 1,
                    pageSize: query.pageSize || 20,
                    total,
                    totalPages: Math.ceil(total / (query.pageSize || 20)),
                },
            };
        },
    });
    fastify.get('/forecasts/:id', {
        schema: {
            description: 'Get a specific forecast by ID',
            tags: ['Forecasts'],
            params: {
                type: 'object',
                properties: {
                    id: { type: 'string', format: 'uuid' },
                },
                required: ['id'],
            },
            response: {
                200: forecast_contracts_1.ForecastResponseSchema,
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
                .from(schema_1.forecasts)
                .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.forecasts.id, id), (0, drizzle_orm_1.eq)(schema_1.forecasts.tenantId, request.tenantId)))
                .limit(1);
            if (result.length === 0) {
                return reply.code(404).send({
                    error: 'Not Found',
                    message: 'Forecast not found',
                });
            }
            const row = result[0];
            if (!row) {
                return reply.code(404).send({
                    error: 'Not Found',
                    message: 'Forecast not found',
                });
            }
            const forecastValues = row.forecastValues || [];
            return {
                id: row.id,
                tenantId: row.tenantId,
                metricName: row.metricName,
                horizon: row.horizon,
                horizonUnit: row.horizonUnit,
                model: row.model,
                forecastValues: forecastValues.map((fv) => ({
                    timestamp: fv.timestamp.toISOString(),
                    value: fv.value,
                    lowerBound: fv.lowerBound,
                    upperBound: fv.upperBound,
                    confidence: fv.confidence,
                })),
                confidenceInterval: row.confidenceInterval,
                createdAt: row.createdAt.toISOString(),
                metadata: row.metadata,
                version: row.version,
            };
        },
    });
    fastify.post('/forecasts', {
        schema: {
            description: 'Generate a new forecast',
            tags: ['Forecasts'],
            body: forecast_contracts_1.CreateForecastRequestSchema,
            response: {
                201: forecast_contracts_1.ForecastResponseSchema,
            },
        },
        handler: async (request, reply) => {
            const body = request.body;
            const historicalData = body.historicalData || [];
            const forecastRequest = {
                tenantId: request.tenantId,
                metricName: body.metricName,
                historicalData: historicalData.map((d) => ({
                    timestamp: new Date(d.timestamp),
                    value: d.value,
                    metadata: d.metadata,
                })),
                horizon: body.horizon,
                horizonUnit: body.horizonUnit,
                model: body.model,
                confidenceInterval: body.confidenceInterval,
                parameters: body.parameters,
            };
            const result = await forecastingService.generateForecast(forecastRequest);
            if (!result.success) {
                return reply.code(400).send({
                    error: 'Forecast Generation Failed',
                    message: result.error || 'Unknown error occurred during forecast generation',
                });
            }
            return reply.code(201).send({
                id: result.forecast.id,
                tenantId: result.forecast.tenantId,
                metricName: result.forecast.metricName,
                horizon: result.forecast.horizon,
                horizonUnit: result.forecast.horizonUnit,
                model: result.forecast.model,
                forecastValues: result.forecast.forecastValues.map(fv => ({
                    timestamp: fv.timestamp.toISOString(),
                    value: fv.value,
                    lowerBound: fv.lowerBound,
                    upperBound: fv.upperBound,
                    confidence: fv.confidence,
                })),
                confidenceInterval: result.forecast.confidenceInterval,
                createdAt: result.forecast.createdAt.toISOString(),
                metadata: result.forecast.metadata,
                version: result.forecast.version,
            });
        },
    });
    fastify.get('/forecasts/:id/compare', {
        schema: {
            description: 'Compare forecast with actual historical data',
            tags: ['Forecasts'],
            params: {
                type: 'object',
                properties: {
                    id: { type: 'string', format: 'uuid' },
                },
                required: ['id'],
            },
            querystring: {
                type: 'object',
                properties: {
                    actualData: {
                        type: 'array',
                        items: {
                            type: 'object',
                            properties: {
                                timestamp: { type: 'string', format: 'date-time' },
                                value: { type: 'number' },
                            },
                        },
                    },
                },
            },
            response: {
                200: forecast_contracts_1.ForecastComparisonSchema,
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
            const query = request.query;
            const forecastResult = await db
                .select()
                .from(schema_1.forecasts)
                .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.forecasts.id, id), (0, drizzle_orm_1.eq)(schema_1.forecasts.tenantId, request.tenantId)))
                .limit(1);
            if (forecastResult.length === 0) {
                return reply.code(404).send({
                    error: 'Not Found',
                    message: 'Forecast not found',
                });
            }
            const forecast = forecastResult[0];
            if (!forecast) {
                return reply.code(404).send({
                    error: 'Not Found',
                    message: 'Forecast not found',
                });
            }
            const actualValues = (query.actualData || []).map((d) => ({
                timestamp: d.timestamp,
                value: d.value,
            }));
            const forecastValues = forecast.forecastValues || [];
            let mse = 0;
            let mae = 0;
            let count = 0;
            for (const actual of actualValues) {
                const forecastPoint = forecastValues.find((f) => Math.abs(f.timestamp.getTime() - new Date(actual.timestamp).getTime()) < 24 * 60 * 60 * 1000);
                if (forecastPoint) {
                    const error = actual.value - forecastPoint.value;
                    mse += error * error;
                    mae += Math.abs(error);
                    count++;
                }
            }
            const accuracy = {
                forecastId: forecast.id,
                metricName: forecast.metricName,
                accuracy: count > 0 ? 1 - Math.min(1, Math.sqrt(mse / count) / Math.max(...actualValues.map((a) => a.value))) : 0,
                mse: count > 0 ? mse / count : undefined,
                mae: count > 0 ? mae / count : undefined,
            };
            return {
                actualValues,
                forecastValues: forecastValues.map((fv) => ({
                    timestamp: fv.timestamp.toISOString(),
                    value: fv.value,
                    lowerBound: fv.lowerBound,
                    upperBound: fv.upperBound,
                })),
                accuracy,
            };
        },
    });
    fastify.delete('/forecasts/:id', {
        schema: {
            description: 'Delete a forecast',
            tags: ['Forecasts'],
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
                    description: 'Forecast deleted successfully',
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
                .delete(schema_1.forecasts)
                .where((0, drizzle_orm_1.and)((0, drizzle_orm_1.eq)(schema_1.forecasts.id, id), (0, drizzle_orm_1.eq)(schema_1.forecasts.tenantId, request.tenantId)));
            if (result.rowCount === 0) {
                return reply.code(404).send({
                    error: 'Not Found',
                    message: 'Forecast not found',
                });
            }
            return reply.code(204).send();
        },
    });
    fastify.delete('/forecasts/cleanup', {
        schema: {
            description: 'Clean up old forecasts',
            tags: ['Forecasts'],
            querystring: {
                type: 'object',
                properties: {
                    olderThanDays: {
                        type: 'integer',
                        minimum: 1,
                        default: 90,
                    },
                },
            },
            response: {
                200: {
                    type: 'object',
                    properties: {
                        deletedCount: { type: 'integer' },
                        message: { type: 'string' },
                    },
                },
            },
        },
        handler: async (request, reply) => {
            const query = request.query;
            const olderThanDays = query.olderThanDays || 90;
            const deletedCount = await forecastingService.cleanupOldForecasts(request.tenantId, olderThanDays);
            return {
                deletedCount,
                message: `Successfully deleted ${deletedCount} old forecasts`,
            };
        },
    });
}
//# sourceMappingURL=forecasts.js.map