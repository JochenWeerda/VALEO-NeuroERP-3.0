import { z } from 'zod';

// Contract Position Cube Schema
export const ContractPositionCubeSchema = z.object({
  tenantId: z.string(),
  commodity: z.string(),
  month: z.string(), // YYYY-MM format
  shortPosition: z.number(),
  longPosition: z.number(),
  netPosition: z.number(),
  hedgingRatio: z.number().optional(),
  lastUpdated: z.string().datetime(),
}).meta({
  title: 'Contract Position Cube',
  description: 'Aggregated contract positions by commodity and month',
});

// Weighing Volume Cube Schema
export const WeighingVolumeCubeSchema = z.object({
  tenantId: z.string(),
  commodity: z.string(),
  customerId: z.string().optional(),
  siteId: z.string().optional(),
  period: z.string(), // YYYY-MM-DD or YYYY-MM format
  totalWeight: z.number(),
  totalTickets: z.number(),
  avgWeight: z.number(),
  withinTolerance: z.number(),
  outsideTolerance: z.number(),
  lastUpdated: z.string().datetime(),
}).meta({
  title: 'Weighing Volume Cube',
  description: 'Aggregated weighing volumes by various dimensions',
});

// Quality Cube Schema
export const QualityCubeSchema = z.object({
  tenantId: z.string(),
  commodity: z.string(),
  period: z.string(), // YYYY-MM format
  totalSamples: z.number(),
  passedSamples: z.number(),
  failedSamples: z.number(),
  passRate: z.number(),
  failureRate: z.number(),
  avgMoisture: z.number().optional(),
  avgProtein: z.number().optional(),
  lastUpdated: z.string().datetime(),
}).meta({
  title: 'Quality Cube',
  description: 'Aggregated quality metrics by commodity and period',
});

// Regulatory Cube Schema
export const RegulatoryCubeSchema = z.object({
  tenantId: z.string(),
  commodity: z.string(),
  labelType: z.string(),
  period: z.string(), // YYYY-MM format
  totalEligible: z.number(),
  totalIneligible: z.number(),
  eligibilityRate: z.number(),
  ineligibilityRate: z.number(),
  lastUpdated: z.string().datetime(),
}).meta({
  title: 'Regulatory Cube',
  description: 'Aggregated regulatory compliance metrics',
});

// Finance Cube Schema
export const FinanceCubeSchema = z.object({
  tenantId: z.string(),
  commodity: z.string(),
  customerId: z.string().optional(),
  period: z.string(), // YYYY-MM format
  totalRevenue: z.number(),
  totalCost: z.number(),
  grossMargin: z.number(),
  marginPercentage: z.number(),
  outstandingInvoices: z.number(),
  overdueInvoices: z.number(),
  lastUpdated: z.string().datetime(),
}).meta({
  title: 'Finance Cube',
  description: 'Aggregated financial metrics by commodity and period',
});

// Cube Query Parameters Base Schema
export const CubeQueryBaseSchema = z.object({
  tenantId: z.string(),
  from: z.string().datetime().optional(),
  to: z.string().datetime().optional(),
  commodity: z.string().optional(),
  customerId: z.string().optional(),
  siteId: z.string().optional(),
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(1000).default(100),
}).meta({
  title: 'Cube Query Base Parameters',
  description: 'Base query parameters for cube operations',
});

// Contract Position Query Schema
export const ContractPositionQuerySchema = CubeQueryBaseSchema.extend({
  month: z.string().optional(), // YYYY-MM format
}).meta({
  title: 'Contract Position Query',
  description: 'Query parameters for contract position cube',
});

// Contract Position Response Schema
export const ContractPositionResponseSchema = z.object({
  data: z.array(ContractPositionCubeSchema),
  summary: z.object({
    totalShort: z.number(),
    totalLong: z.number(),
    netExposure: z.number(),
    avgHedgingRatio: z.number().optional(),
  }).optional(),
}).meta({
  title: 'Contract Position Response',
  description: 'Contract position cube data with summary',
});

// Weighing Volume Query Schema
export const WeighingVolumeQuerySchema = CubeQueryBaseSchema.extend({
  period: z.string().optional(), // YYYY-MM-DD or YYYY-MM
  groupBy: z.enum(['day', 'week', 'month']).default('month'),
}).meta({
  title: 'Weighing Volume Query',
  description: 'Query parameters for weighing volume cube',
});

// Weighing Volume Response Schema
export const WeighingVolumeResponseSchema = z.object({
  data: z.array(WeighingVolumeCubeSchema),
  summary: z.object({
    totalWeight: z.number(),
    totalTickets: z.number(),
    avgWeightPerTicket: z.number(),
    overallToleranceRate: z.number(),
  }).optional(),
}).meta({
  title: 'Weighing Volume Response',
  description: 'Weighing volume cube data with summary',
});

// Quality Query Schema
export const QualityQuerySchema = CubeQueryBaseSchema.extend({
  period: z.string().optional(), // YYYY-MM format
}).meta({
  title: 'Quality Query',
  description: 'Query parameters for quality cube',
});

// Quality Response Schema
export const QualityResponseSchema = z.object({
  data: z.array(QualityCubeSchema),
  summary: z.object({
    totalSamples: z.number(),
    overallPassRate: z.number(),
    avgMoisture: z.number().optional(),
    avgProtein: z.number().optional(),
  }).optional(),
}).meta({
  title: 'Quality Response',
  description: 'Quality cube data with summary',
});

// Regulatory Query Schema
export const RegulatoryQuerySchema = CubeQueryBaseSchema.extend({
  labelType: z.string().optional(),
  period: z.string().optional(), // YYYY-MM format
}).meta({
  title: 'Regulatory Query',
  description: 'Query parameters for regulatory cube',
});

// Regulatory Response Schema
export const RegulatoryResponseSchema = z.object({
  data: z.array(RegulatoryCubeSchema),
  summary: z.object({
    totalEligible: z.number(),
    totalIneligible: z.number(),
    overallEligibilityRate: z.number(),
  }).optional(),
}).meta({
  title: 'Regulatory Response',
  description: 'Regulatory cube data with summary',
});

// Finance Query Schema
export const FinanceQuerySchema = CubeQueryBaseSchema.extend({
  period: z.string().optional(), // YYYY-MM format
}).meta({
  title: 'Finance Query',
  description: 'Query parameters for finance cube',
});

// Finance Response Schema
export const FinanceResponseSchema = z.object({
  data: z.array(FinanceCubeSchema),
  summary: z.object({
    totalRevenue: z.number(),
    totalCost: z.number(),
    totalMargin: z.number(),
    avgMarginPercentage: z.number(),
    totalOutstanding: z.number(),
    totalOverdue: z.number(),
  }).optional(),
}).meta({
  title: 'Finance Response',
  description: 'Finance cube data with summary',
});

// Cube Refresh Request Schema
export const CubeRefreshRequestSchema = z.object({
  cubeNames: z.array(z.string()).optional(),
  force: z.boolean().default(false),
}).meta({
  title: 'Cube Refresh Request',
  description: 'Request to refresh materialized view cubes',
});

// Cube Refresh Result Schema
export const CubeRefreshResultSchema = z.object({
  cubeName: z.string(),
  success: z.boolean(),
  recordCount: z.number().optional(),
  executionTimeMs: z.number(),
  error: z.string().optional(),
  refreshedAt: z.string().datetime(),
}).meta({
  title: 'Cube Refresh Result',
  description: 'Result of a cube refresh operation',
});

// Bulk Cube Refresh Response Schema
export const BulkCubeRefreshResponseSchema = z.object({
  totalRequested: z.number(),
  successful: z.number(),
  failed: z.number(),
  results: z.array(CubeRefreshResultSchema),
  totalExecutionTimeMs: z.number(),
}).meta({
  title: 'Bulk Cube Refresh Response',
  description: 'Response for bulk cube refresh operation',
});