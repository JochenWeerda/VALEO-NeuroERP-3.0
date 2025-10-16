import type { FastifyInstance } from 'fastify';
import { eq, and } from 'drizzle-orm';
import { drizzle } from 'drizzle-orm/node-postgres';
import {
  ContractPositionQuerySchema,
  ContractPositionResponseSchema,
  WeighingVolumeQuerySchema,
  WeighingVolumeResponseSchema,
  QualityQuerySchema,
  QualityResponseSchema,
  RegulatoryQuerySchema,
  RegulatoryResponseSchema,
  FinanceQuerySchema,
  FinanceResponseSchema,
  CubeRefreshRequestSchema,
  BulkCubeRefreshResponseSchema,
} from '../../contracts/cube-contracts';
import {
  mvContractPositions,
  mvQualityStats,
  mvRegulatoryStats,
  mvFinanceKpis,
  mvWeighingVolumes
} from '../../infra/db/schema';
import { AggregationService } from '../../domain/services/aggregation-service';

export async function registerCubeRoutes(
  fastify: FastifyInstance,
  db: ReturnType<typeof drizzle>,
  aggregationService: AggregationService
) {
  // GET /cubes/contract-positions - Get contract position cube data
  fastify.get('/cubes/contract-positions', {
    schema: {
      description: 'Get contract position cube data',
      tags: ['Cubes'],
      querystring: ContractPositionQuerySchema,
      response: {
        200: ContractPositionResponseSchema,
      },
    },
    handler: async (request, _reply) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const query = request.query as any;

      // Build conditions
      const conditions = [eq(mvContractPositions.tenantId, request.tenantId)];

      // Apply filters
      if (query.commodity != null && query.commodity !== '') {
        conditions.push(eq(mvContractPositions.commodity, query.commodity));
      }

      if (query.month != null && query.month !== '') {
        conditions.push(eq(mvContractPositions.month, query.month));
      }

      // Pagination
      const DEFAULT_PAGE = 1;
      const DEFAULT_PAGE_SIZE = 100;
      const page = (query.page != null && query.page !== 0) ? query.page : DEFAULT_PAGE;
      const pageSize = (query.pageSize != null && query.pageSize !== 0) ? query.pageSize : DEFAULT_PAGE_SIZE;
      const offset = (page - 1) * pageSize;

      const results = await db
        .select()
        .from(mvContractPositions)
        .where(and(...conditions))
        .limit(pageSize)
        .offset(offset);

      // Calculate summary
      const summary = {
        totalShort: results.reduce((sum, r) => sum + Number((r.shortPosition != null && Number(r.shortPosition) !== 0) ? r.shortPosition : 0), 0),
        totalLong: results.reduce((sum, r) => sum + Number((r.longPosition != null && Number(r.longPosition) !== 0) ? r.longPosition : 0), 0),
        netExposure: results.reduce((sum, r) => sum + Number((r.netPosition != null && Number(r.netPosition) !== 0) ? r.netPosition : 0), 0),
        avgHedgingRatio: results.length > 0
          ? results.reduce((sum, r) => sum + Number((r.hedgingRatio != null && Number(r.hedgingRatio) !== 0) ? r.hedgingRatio : 0), 0) / results.length
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

  // GET /cubes/weighing-volumes - Get weighing volume cube data
  fastify.get('/cubes/weighing-volumes', {
    schema: {
      description: 'Get weighing volume cube data',
      tags: ['Cubes'],
      querystring: WeighingVolumeQuerySchema,
      response: {
        200: WeighingVolumeResponseSchema,
      },
    },
    handler: async (request, _reply) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const query = request.query as any;

      // Build conditions
      const conditions = [eq(mvWeighingVolumes.tenantId, request.tenantId)];

      // Apply filters
      if (query.commodity != null && query.commodity !== '') {
        conditions.push(eq(mvWeighingVolumes.commodity, query.commodity));
      }

      if (query.customerId != null && query.customerId !== '') {
        conditions.push(eq(mvWeighingVolumes.customerId, query.customerId));
      }

      if (query.siteId != null && query.siteId !== '') {
        conditions.push(eq(mvWeighingVolumes.siteId, query.siteId));
      }

      if (query.period != null && query.period !== '') {
        conditions.push(eq(mvWeighingVolumes.period, query.period));
      }

      // Pagination
      const DEFAULT_PAGE = 1;
      const DEFAULT_PAGE_SIZE = 100;
      const page = (query.page != null && query.page !== 0) ? query.page : DEFAULT_PAGE;
      const pageSize = (query.pageSize != null && query.pageSize !== 0) ? query.pageSize : DEFAULT_PAGE_SIZE;
      const offset = (page - 1) * pageSize;

      const results = await db
        .select()
        .from(mvWeighingVolumes)
        .where(and(...conditions))
        .limit(pageSize)
        .offset(offset);

      // Calculate summary
      const summary = {
        totalWeight: results.reduce((sum, r) => sum + Number((r.totalWeight != null && Number(r.totalWeight) !== 0) ? r.totalWeight : 0), 0),
        totalTickets: results.reduce((sum, r) => sum + Number((r.totalTickets != null && Number(r.totalTickets) !== 0) ? r.totalTickets : 0), 0),
        avgWeightPerTicket: results.reduce((sum, r) => sum + Number((r.totalTickets != null && Number(r.totalTickets) !== 0) ? r.totalTickets : 0), 0) > 0
          ? results.reduce((sum, r) => sum + Number((r.totalWeight != null && Number(r.totalWeight) !== 0) ? r.totalWeight : 0), 0) /
            results.reduce((sum, r) => sum + Number((r.totalTickets != null && Number(r.totalTickets) !== 0) ? r.totalTickets : 0), 0)
          : 0,
        overallToleranceRate: results.reduce((sum, r) => sum + Number((r.totalTickets != null && Number(r.totalTickets) !== 0) ? r.totalTickets : 0), 0) > 0
          ? results.reduce((sum, r) => sum + Number((r.withinTolerance != null && Number(r.withinTolerance) !== 0) ? r.withinTolerance : 0), 0) /
            results.reduce((sum, r) => sum + Number((r.totalTickets != null && Number(r.totalTickets) !== 0) ? r.totalTickets : 0), 0)
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

  // GET /cubes/quality - Get quality statistics cube data
  fastify.get('/cubes/quality', {
    schema: {
      description: 'Get quality statistics cube data',
      tags: ['Cubes'],
      querystring: QualityQuerySchema,
      response: {
        200: QualityResponseSchema,
      },
    },
    handler: async (request, _reply) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const query = request.query as any;

      // Build conditions
      const conditions = [eq(mvQualityStats.tenantId, request.tenantId)];

      // Apply filters
      if (query.commodity != null && query.commodity !== '') {
        conditions.push(eq(mvQualityStats.commodity, query.commodity));
      }

      if (query.period != null && query.period !== '') {
        conditions.push(eq(mvQualityStats.period, query.period));
      }

      // Pagination
      const DEFAULT_PAGE = 1;
      const DEFAULT_PAGE_SIZE = 100;
      const page = (query.page != null && query.page !== 0) ? query.page : DEFAULT_PAGE;
      const pageSize = (query.pageSize != null && query.pageSize !== 0) ? query.pageSize : DEFAULT_PAGE_SIZE;
      const offset = (page - 1) * pageSize;

      const results = await db
        .select()
        .from(mvQualityStats)
        .where(and(...conditions))
        .limit(pageSize)
        .offset(offset);

      // Calculate summary
      const summary = {
        totalSamples: results.reduce((sum, r) => sum + Number((r.totalSamples != null && Number(r.totalSamples) !== 0) ? r.totalSamples : 0), 0),
        overallPassRate: results.reduce((sum, r) => sum + Number((r.totalSamples != null && Number(r.totalSamples) !== 0) ? r.totalSamples : 0), 0) > 0
          ? results.reduce((sum, r) => sum + Number((r.passedSamples != null && Number(r.passedSamples) !== 0) ? r.passedSamples : 0), 0) /
            results.reduce((sum, r) => sum + Number((r.totalSamples != null && Number(r.totalSamples) !== 0) ? r.totalSamples : 0), 0)
          : 0,
        avgMoisture: results.length > 0
          ? results.reduce((sum, r) => sum + Number((r.avgMoisture != null && Number(r.avgMoisture) !== 0) ? r.avgMoisture : 0), 0) / results.length
          : 0,
        avgProtein: results.length > 0
          ? results.reduce((sum, r) => sum + Number((r.avgProtein != null && Number(r.avgProtein) !== 0) ? r.avgProtein : 0), 0) / results.length
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

  // GET /cubes/regulatory - Get regulatory compliance cube data
  fastify.get('/cubes/regulatory', {
    schema: {
      description: 'Get regulatory compliance cube data',
      tags: ['Cubes'],
      querystring: RegulatoryQuerySchema,
      response: {
        200: RegulatoryResponseSchema,
      },
    },
    handler: async (request, _reply) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const query = request.query as any;

      // Build conditions
      const conditions = [eq(mvRegulatoryStats.tenantId, request.tenantId)];

      // Apply filters
      if (query.commodity != null && query.commodity !== '') {
        conditions.push(eq(mvRegulatoryStats.commodity, query.commodity));
      }

      if (query.labelType != null && query.labelType !== '') {
        conditions.push(eq(mvRegulatoryStats.labelType, query.labelType));
      }

      if (query.period != null && query.period !== '') {
        conditions.push(eq(mvRegulatoryStats.period, query.period));
      }

      // Pagination
      const DEFAULT_PAGE = 1;
      const DEFAULT_PAGE_SIZE = 100;
      const page = (query.page != null && query.page !== 0) ? query.page : DEFAULT_PAGE;
      const pageSize = (query.pageSize != null && query.pageSize !== 0) ? query.pageSize : DEFAULT_PAGE_SIZE;
      const offset = (page - 1) * pageSize;

      const results = await db
        .select()
        .from(mvRegulatoryStats)
        .where(and(...conditions))
        .limit(pageSize)
        .offset(offset);

      // Calculate summary
      const summary = {
        totalEligible: results.reduce((sum, r) => sum + ((r.totalEligible != null && r.totalEligible !== 0) ? r.totalEligible : 0), 0),
        totalIneligible: results.reduce((sum, r) => sum + ((r.totalIneligible != null && r.totalIneligible !== 0) ? r.totalIneligible : 0), 0),
        overallEligibilityRate: results.reduce((sum, r) => sum + (((r.totalEligible != null && r.totalEligible !== 0) ? r.totalEligible : 0) + ((r.totalIneligible != null && r.totalIneligible !== 0) ? r.totalIneligible : 0)), 0) > 0
          ? results.reduce((sum, r) => sum + ((r.totalEligible != null && r.totalEligible !== 0) ? r.totalEligible : 0), 0) /
            results.reduce((sum, r) => sum + (((r.totalEligible != null && r.totalEligible !== 0) ? r.totalEligible : 0) + ((r.totalIneligible != null && r.totalIneligible !== 0) ? r.totalIneligible : 0)), 0)
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

  // GET /cubes/finance - Get finance KPIs cube data
  fastify.get('/cubes/finance', {
    schema: {
      description: 'Get finance KPIs cube data',
      tags: ['Cubes'],
      querystring: FinanceQuerySchema,
      response: {
        200: FinanceResponseSchema,
      },
    },
    handler: async (request, _reply) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const query = request.query as any;

      // Build conditions
      const conditions = [eq(mvFinanceKpis.tenantId, request.tenantId)];

      // Apply filters
      if (query.commodity != null && query.commodity !== '') {
        conditions.push(eq(mvFinanceKpis.commodity, query.commodity));
      }

      if (query.customerId != null && query.customerId !== '') {
        conditions.push(eq(mvFinanceKpis.customerId, query.customerId));
      }

      if (query.period != null && query.period !== '') {
        conditions.push(eq(mvFinanceKpis.period, query.period));
      }

      // Pagination
      const DEFAULT_PAGE = 1;
      const DEFAULT_PAGE_SIZE = 100;
      const page = (query.page != null && query.page !== 0) ? query.page : DEFAULT_PAGE;
      const pageSize = (query.pageSize != null && query.pageSize !== 0) ? query.pageSize : DEFAULT_PAGE_SIZE;
      const offset = (page - 1) * pageSize;

      const results = await db
        .select()
        .from(mvFinanceKpis)
        .where(and(...conditions))
        .limit(pageSize)
        .offset(offset);

      // Calculate summary
      const summary = {
        totalRevenue: results.reduce((sum, r) => sum + Number((r.totalRevenue != null && Number(r.totalRevenue) !== 0) ? r.totalRevenue : 0), 0),
        totalCost: results.reduce((sum, r) => sum + Number((r.totalCost != null && Number(r.totalCost) !== 0) ? r.totalCost : 0), 0),
        totalMargin: results.reduce((sum, r) => sum + Number((r.grossMargin != null && Number(r.grossMargin) !== 0) ? r.grossMargin : 0), 0),
        avgMarginPercentage: results.length > 0
          ? results.reduce((sum, r) => sum + Number((r.marginPercentage != null && Number(r.marginPercentage) !== 0) ? r.marginPercentage : 0), 0) / results.length
          : 0,
        totalOutstanding: results.reduce((sum, r) => sum + Number((r.outstandingInvoices != null && Number(r.outstandingInvoices) !== 0) ? r.outstandingInvoices : 0), 0),
        totalOverdue: results.reduce((sum, r) => sum + Number((r.overdueInvoices != null && Number(r.overdueInvoices) !== 0) ? r.overdueInvoices : 0), 0),
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

  // POST /cubes/refresh - Refresh cube materialized views
  fastify.post('/cubes/refresh', {
    schema: {
      description: 'Refresh cube materialized views',
      tags: ['Cubes'],
      body: CubeRefreshRequestSchema,
      response: {
        200: BulkCubeRefreshResponseSchema,
      },
    },
    handler: async (request, _reply) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const body = request.body as any;

      const DEFAULT_CUBE_NAMES = [
        'contractPositions',
        'qualityStats',
        'regulatoryStats',
        'financeKpis',
        'weighingVolumes',
      ];
      const cubeNames = (body.cubeNames != null && Array.isArray(body.cubeNames)) ? body.cubeNames : DEFAULT_CUBE_NAMES;

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

        } catch (error) {
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
        failed: results.filter(r => r.success === false).length,
        results,
        totalExecutionTimeMs,
      };
    },
  });

  // GET /cubes/status - Get cube refresh status
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
    handler: async (request, _reply) => {
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

// Extend FastifyRequest to include tenantId
declare module 'fastify' {
  interface FastifyRequest {
    tenantId: string;
  }
}