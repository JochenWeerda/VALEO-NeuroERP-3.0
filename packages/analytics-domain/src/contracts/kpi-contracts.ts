import { z } from 'zod';
import { extendZodWithOpenApi } from 'zod-openapi';

// Extend Zod with OpenAPI
extendZodWithOpenApi(z);

// KPI Context Schema
export const KpiContextSchema = z.object({
  commodity: z.string().optional(),
  contract: z.string().optional(),
  batch: z.string().optional(),
  site: z.string().optional(),
  customer: z.string().optional(),
  supplier: z.string().optional(),
  period: z.string().optional(),
}).openapi({
  title: 'KPI Context',
  description: 'Contextual information for KPI calculation',
});

// KPI Metadata Schema
export const KpiMetadataSchema = z.object({
  calculationMethod: z.string().optional(),
  dataSource: z.string().optional(),
  lastUpdated: z.date().optional(),
  confidence: z.number().min(0).max(1).optional(),
  unit: z.string().optional(),
}).openapi({
  title: 'KPI Metadata',
  description: 'Additional metadata for KPI',
});

// Create KPI Request Schema
export const CreateKpiRequestSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().min(1).max(500),
  value: z.union([z.number(), z.string(), z.boolean()]),
  unit: z.string().min(1).max(50),
  context: KpiContextSchema.optional(),
  metadata: KpiMetadataSchema.optional(),
}).openapi({
  title: 'Create KPI Request',
  description: 'Request payload for creating a new KPI',
});

// Update KPI Request Schema
export const UpdateKpiRequestSchema = z.object({
  value: z.union([z.number(), z.string(), z.boolean()]).optional(),
  context: KpiContextSchema.optional(),
  metadata: KpiMetadataSchema.optional(),
}).openapi({
  title: 'Update KPI Request',
  description: 'Request payload for updating an existing KPI',
});

// KPI Response Schema
export const KpiResponseSchema = z.object({
  id: z.string().uuid(),
  tenantId: z.string(),
  name: z.string(),
  description: z.string(),
  value: z.union([z.number(), z.string(), z.boolean()]),
  unit: z.string(),
  context: KpiContextSchema,
  calculatedAt: z.string().datetime(),
  metadata: KpiMetadataSchema.optional(),
  version: z.number(),
}).openapi({
  title: 'KPI Response',
  description: 'KPI data response',
});

// KPI Query Parameters Schema
export const KpiQuerySchema = z.object({
  name: z.string().optional(),
  from: z.string().datetime().optional(),
  to: z.string().datetime().optional(),
  commodity: z.string().optional(),
  customer: z.string().optional(),
  site: z.string().optional(),
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(100).default(20),
}).openapi({
  title: 'KPI Query Parameters',
  description: 'Query parameters for KPI filtering and pagination',
});

// KPI List Response Schema
export const KpiListResponseSchema = z.object({
  data: z.array(KpiResponseSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number(),
  }),
}).openapi({
  title: 'KPI List Response',
  description: 'Paginated list of KPIs',
});

// Recalculate KPIs Request Schema
export const RecalculateKpisRequestSchema = z.object({
  kpiNames: z.array(z.string()).optional(),
  force: z.boolean().default(false),
}).openapi({
  title: 'Recalculate KPIs Request',
  description: 'Request to recalculate KPIs',
});

// KPI Calculation Result Schema
export const KpiCalculationResultSchema = z.object({
  kpiId: z.string().uuid(),
  kpiName: z.string(),
  success: z.boolean(),
  value: z.union([z.number(), z.string(), z.boolean()]).optional(),
  error: z.string().optional(),
  executionTimeMs: z.number(),
}).openapi({
  title: 'KPI Calculation Result',
  description: 'Result of a KPI calculation operation',
});

// Bulk KPI Recalculation Response Schema
export const BulkKpiRecalculationResponseSchema = z.object({
  totalRequested: z.number(),
  successful: z.number(),
  failed: z.number(),
  results: z.array(KpiCalculationResultSchema),
  executionTimeMs: z.number(),
}).openapi({
  title: 'Bulk KPI Recalculation Response',
  description: 'Response for bulk KPI recalculation operation',
});