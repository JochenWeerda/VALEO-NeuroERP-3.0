/**
 * Agribusiness Analytics REST API Routes
 * Advanced Analytics & Reporting
 */

import { FastifyInstance } from 'fastify';
import { AgribusinessAnalyticsService } from '../../domain/services/agribusiness-analytics-service';
import { BatchRepository } from '../../infra/repositories/batch-repository';
import { CommodityContractRepository } from '../../infra/repositories/commodity-contract-repository';
import { FarmerRepository } from '../../infra/repositories/farmer-repository';
import { FieldServiceTaskRepository } from '../../infra/repositories/field-service-task-repository';

// Initialize services
const batchRepository = new BatchRepository();
const contractRepository = new CommodityContractRepository();
const farmerRepository = new FarmerRepository();
const taskRepository = new FieldServiceTaskRepository();

const analyticsService = new AgribusinessAnalyticsService({
  batchRepository,
  contractRepository,
  farmerRepository,
  taskRepository,
});

export async function registerAgribusinessAnalyticsRoutes(fastify: FastifyInstance) {
  fastify.register(async (analyticsRoutes) => {

    // GET /analytics/kpis - Get overall KPIs
    analyticsRoutes.get('/kpis', {
      schema: {
        description: 'Get overall agribusiness KPIs',
        tags: ['Analytics'],
        querystring: {
          type: 'object',
          properties: {
            dateFrom: { type: 'string', format: 'date-time' },
            dateTo: { type: 'string', format: 'date-time' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      const dateFrom = query.dateFrom ? new Date(query.dateFrom) : undefined;
      const dateTo = query.dateTo ? new Date(query.dateTo) : undefined;
      try {
        const kpis = await analyticsService.getKPIs(dateFrom, dateTo);
        return reply.send(kpis);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /analytics/farmer-performance - Get farmer performance metrics
    analyticsRoutes.get('/farmer-performance', {
      schema: {
        description: 'Get farmer performance metrics',
        tags: ['Analytics'],
        querystring: {
          type: 'object',
          properties: {
            farmerId: { type: 'string' },
            dateFrom: { type: 'string', format: 'date-time' },
            dateTo: { type: 'string', format: 'date-time' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      const farmerId = query.farmerId;
      const dateFrom = query.dateFrom ? new Date(query.dateFrom) : undefined;
      const dateTo = query.dateTo ? new Date(query.dateTo) : undefined;
      try {
        const metrics = await analyticsService.getFarmerPerformanceMetrics(farmerId, dateFrom, dateTo);
        return reply.send({ data: metrics });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /analytics/contract-performance - Get contract performance metrics
    analyticsRoutes.get('/contract-performance', {
      schema: {
        description: 'Get contract performance metrics',
        tags: ['Analytics'],
        querystring: {
          type: 'object',
          properties: {
            contractId: { type: 'string' },
            dateFrom: { type: 'string', format: 'date-time' },
            dateTo: { type: 'string', format: 'date-time' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      const contractId = query.contractId;
      const dateFrom = query.dateFrom ? new Date(query.dateFrom) : undefined;
      const dateTo = query.dateTo ? new Date(query.dateTo) : undefined;
      try {
        const metrics = await analyticsService.getContractPerformanceMetrics(contractId, dateFrom, dateTo);
        return reply.send({ data: metrics });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /analytics/seasonal-trends - Get seasonal trends
    analyticsRoutes.get('/seasonal-trends', {
      schema: {
        description: 'Get seasonal trends',
        tags: ['Analytics'],
        querystring: {
          type: 'object',
          required: ['year'],
          properties: {
            year: { type: 'integer', minimum: 2000, maximum: 2100 },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      try {
        const trends = await analyticsService.getSeasonalTrends(query.year);
        return reply.send({ data: trends });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /analytics/quality-trends - Get quality trends
    analyticsRoutes.get('/quality-trends', {
      schema: {
        description: 'Get quality trends',
        tags: ['Analytics'],
        querystring: {
          type: 'object',
          required: ['period'],
          properties: {
            period: { type: 'string' }, // e.g., "2024-Q1"
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      try {
        const trends = await analyticsService.getQualityTrends(query.period);
        return reply.send(trends);
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });

    // GET /analytics/batch-analytics - Get batch analytics
    analyticsRoutes.get('/batch-analytics', {
      schema: {
        description: 'Get batch analytics',
        tags: ['Analytics'],
        querystring: {
          type: 'object',
          properties: {
            batchId: { type: 'string' },
          },
        },
      },
    }, async (request, reply) => {
      const query = request.query as any;
      try {
        const analytics = await analyticsService.getBatchAnalytics(query.batchId);
        return reply.send({ data: analytics });
      } catch (error: any) {
        return reply.status(400).send({ error: error.message });
      }
    });
  });
}

