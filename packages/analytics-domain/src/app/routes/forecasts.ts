import type { FastifyInstance } from 'fastify';
import { eq, and, sql } from 'drizzle-orm';
import { drizzle } from 'drizzle-orm/node-postgres';
import {
  CreateForecastRequestSchema,
  ForecastResponseSchema,
  ForecastQuerySchema,
  ForecastListResponseSchema,
  ForecastComparisonSchema,
} from '../../contracts/forecast-contracts';
import { forecasts } from '../../infra/db/schema';
import { ForecastingService } from '../../domain/services/forecasting-service';

export async function registerForecastRoutes(
  fastify: FastifyInstance,
  db: ReturnType<typeof drizzle>,
  forecastingService: ForecastingService
) {
  // GET /forecasts - List forecasts with filtering and pagination
  fastify.get('/forecasts', {
    schema: {
      description: 'Get forecasts with filtering and pagination',
      tags: ['Forecasts'],
      querystring: ForecastQuerySchema,
      response: {
        200: ForecastListResponseSchema,
      },
    },
    handler: async (request, _reply) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const query = request.query as any;

      const DEFAULT_PAGE = 1;
      const DEFAULT_PAGE_SIZE = 20;
      const page = (query.page != null && query.page !== 0) ? query.page : DEFAULT_PAGE;
      const pageSize = (query.pageSize != null && query.pageSize !== 0) ? query.pageSize : DEFAULT_PAGE_SIZE;

      const filters = {
        metricName: query.metricName,
        model: query.model,
        fromDate: (query.from != null && query.from !== '') ? new Date(query.from) : undefined,
        toDate: (query.to != null && query.to !== '') ? new Date(query.to) : undefined,
        limit: pageSize,
        offset: (page - 1) * pageSize,
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

      // Get total count for pagination
      const totalConditions = [eq(forecasts.tenantId, request.tenantId)];

      if (query.metricName != null && query.metricName !== '') {
        totalConditions.push(eq(forecasts.metricName, query.metricName));
      }

      if (query.model != null && query.model !== '') {
        totalConditions.push(eq(forecasts.model, query.model));
      }

      const totalResult = await db
        .select({ count: sql<number>`count(*)` })
        .from(forecasts)
        .where(and(...totalConditions));

      const total = totalResult[0]?.count ?? 0;

      return {
        data: forecastResponses,
        pagination: {
          page,
          pageSize,
          total,
          totalPages: Math.ceil(total / pageSize),
        },
      };
    },
  });

  // GET /forecasts/:id - Get specific forecast
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
        200: ForecastResponseSchema,
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
        .from(forecasts)
        .where(and(
          eq(forecasts.id, id),
          eq(forecasts.tenantId, request.tenantId)
        ))
        .limit(1);

      if (result.length === 0) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'Forecast not found',
        });
      }

      const row = result[0];
      if (row == null) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'Forecast not found',
        });
      }

      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const forecastValues = (row.forecastValues != null && Array.isArray(row.forecastValues)) ? (row.forecastValues as any[]) : [];
      return {
        id: row.id,
        tenantId: row.tenantId,
        metricName: row.metricName,
        horizon: row.horizon,
        horizonUnit: row.horizonUnit,
        model: row.model,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        forecastValues: forecastValues.map((fv: any) => ({
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

  // POST /forecasts - Create a new forecast
  fastify.post('/forecasts', {
    schema: {
      description: 'Generate a new forecast',
      tags: ['Forecasts'],
      body: CreateForecastRequestSchema,
      response: {
        201: ForecastResponseSchema,
      },
    },
    handler: async (request, reply) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const body = request.body as any;

      // Prepare historical data
      const historicalData = (body.historicalData != null && Array.isArray(body.historicalData)) ? body.historicalData : [];

      const forecastRequest = {
        tenantId: request.tenantId,
        metricName: body.metricName,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        historicalData: historicalData.map((d: any) => ({
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

      if (result.success === false) {
        return reply.code(400).send({
          error: 'Forecast Generation Failed',
          message: (result.error != null && result.error !== '') ? result.error : 'Unknown error occurred during forecast generation',
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

  // GET /forecasts/:id/compare - Compare forecast with actual data
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
        200: ForecastComparisonSchema,
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
      const query = request.query as any;

      // Get forecast
      const forecastResult = await db
        .select()
        .from(forecasts)
        .where(and(
          eq(forecasts.id, id),
          eq(forecasts.tenantId, request.tenantId)
        ))
        .limit(1);

      if (forecastResult.length === 0) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'Forecast not found',
        });
      }

      const forecast = forecastResult[0];
      if (forecast == null) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'Forecast not found',
        });
      }

      // Prepare actual data
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const actualValues = ((query.actualData != null && Array.isArray(query.actualData)) ? query.actualData : []).map((d: any) => ({
        timestamp: d.timestamp,
        value: d.value,
      }));

      // Calculate accuracy metrics (simplified)
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const forecastValues = (forecast.forecastValues != null && Array.isArray(forecast.forecastValues)) ? (forecast.forecastValues as any[]) : [];
      let mse = 0;
      let mae = 0;
      let count = 0;

      // Match forecast and actual values by timestamp (simplified)
      const MILLISECONDS_PER_DAY = 24 * 60 * 60 * 1000;
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      for (const actual of actualValues) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const forecastPoint = forecastValues.find((f: any) =>
          Math.abs(f.timestamp.getTime() - new Date(actual.timestamp).getTime()) < MILLISECONDS_PER_DAY // Within 1 day
        );

        if (forecastPoint != null) {
          const error = actual.value - forecastPoint.value;
          mse += error * error;
          mae += Math.abs(error);
          count++;
        }
      }

      const accuracy = {
        forecastId: forecast.id,
        metricName: forecast.metricName,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        accuracy: count > 0 ? 1 - Math.min(1, Math.sqrt(mse / count) / Math.max(...actualValues.map((a: any) => a.value))) : 0,
        mse: count > 0 ? mse / count : undefined,
        mae: count > 0 ? mae / count : undefined,
      };

      return {
        actualValues,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        forecastValues: forecastValues.map((fv: any) => ({
          timestamp: fv.timestamp.toISOString(),
          value: fv.value,
          lowerBound: fv.lowerBound,
          upperBound: fv.upperBound,
        })),
        accuracy,
      };
    },
  });

  // DELETE /forecasts/:id - Delete forecast
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
      const { id } = request.params as { id: string };

      const result = await db
        .delete(forecasts)
        .where(and(
          eq(forecasts.id, id),
          eq(forecasts.tenantId, request.tenantId)
        ));

      if (result.rowCount === 0) {
        return reply.code(404).send({
          error: 'Not Found',
          message: 'Forecast not found',
        });
      }

      return reply.code(204).send();
    },
  });

  // DELETE /forecasts/cleanup - Clean up old forecasts
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
    handler: async (request, _reply) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const query = request.query as any;
      const DEFAULT_CLEANUP_DAYS = 90;
      const olderThanDays = (query.olderThanDays != null && query.olderThanDays !== 0) ? query.olderThanDays : DEFAULT_CLEANUP_DAYS;

      const deletedCount = await forecastingService.cleanupOldForecasts(request.tenantId, olderThanDays);

      return {
        deletedCount,
        message: `Successfully deleted ${deletedCount} old forecasts`,
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