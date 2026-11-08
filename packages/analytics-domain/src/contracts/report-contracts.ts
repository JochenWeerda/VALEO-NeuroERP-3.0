import { z } from 'zod';

// Report Type Enum
export const ReportTypeSchema = z.enum([
  'Contracts',
  'Inventory',
  'Weighing',
  'Finance',
  'Quality',
  'Production',
  'Regulatory',
  'Custom'
]).meta({
  title: 'Report Type',
  description: 'Type of report to generate',
});

// Report Format Enum
export const ReportFormatSchema = z.enum([
  'json',
  'csv',
  'excel',
  'pdf'
]).meta({
  title: 'Report Format',
  description: 'Output format for the report',
});

// Report Parameters Schema
export const ReportParametersSchema = z.object({
  tenantId: z.string(),
  dateFrom: z.string().datetime().optional(),
  dateTo: z.string().datetime().optional(),
  commodity: z.string().optional(),
  customerId: z.string().optional(),
  supplierId: z.string().optional(),
  siteId: z.string().optional(),
  status: z.string().optional(),
  filters: z.record(z.string(), z.any()).optional(),
}).meta({
  title: 'Report Parameters',
  description: 'Parameters for report generation',
});

// Report Metadata Schema
export const ReportMetadataSchema = z.object({
  totalRecords: z.number().optional(),
  executionTimeMs: z.number().optional(),
  dataSource: z.string().optional(),
  generatedBy: z.string().optional(),
  checksum: z.string().optional(),
}).meta({
  title: 'Report Metadata',
  description: 'Metadata about report generation',
});

// Generate Report Request Schema
export const GenerateReportRequestSchema = z.object({
  type: ReportTypeSchema,
  parameters: ReportParametersSchema,
  format: ReportFormatSchema.default('json'),
}).meta({
  title: 'Generate Report Request',
  description: 'Request payload for generating a report',
});

// Report Response Schema
export const ReportResponseSchema = z.object({
  id: z.string().guid(),
  tenantId: z.string(),
  type: ReportTypeSchema,
  parameters: ReportParametersSchema,
  generatedAt: z.string().datetime(),
  uri: z.string().optional(),
  format: ReportFormatSchema,
  metadata: ReportMetadataSchema.optional(),
  version: z.number(),
}).meta({
  title: 'Report Response',
  description: 'Report data response',
});

// Report Query Parameters Schema
export const ReportQuerySchema = z.object({
  type: ReportTypeSchema.optional(),
  from: z.string().datetime().optional(),
  to: z.string().datetime().optional(),
  format: ReportFormatSchema.optional(),
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(100).default(20),
}).meta({
  title: 'Report Query Parameters',
  description: 'Query parameters for report filtering and pagination',
});

// Report List Response Schema
export const ReportListResponseSchema = z.object({
  data: z.array(ReportResponseSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number(),
  }),
}).meta({
  title: 'Report List Response',
  description: 'Paginated list of reports',
});

// Report Content Response Schema
export const ReportContentResponseSchema = z.object({
  report: ReportResponseSchema,
  content: z.any(), // The actual report data/content
  contentType: z.string(),
  contentLength: z.number(),
}).meta({
  title: 'Report Content Response',
  description: 'Report with its content data',
});

// Report Generation Status Schema
export const ReportGenerationStatusSchema = z.enum([
  'pending',
  'processing',
  'completed',
  'failed'
]).meta({
  title: 'Report Generation Status',
  description: 'Status of report generation process',
});

// Report Generation Result Schema
export const ReportGenerationResultSchema = z.object({
  reportId: z.string().guid(),
  status: ReportGenerationStatusSchema,
  progress: z.number().min(0).max(100).optional(),
  message: z.string().optional(),
  uri: z.string().optional(),
  error: z.string().optional(),
  executionTimeMs: z.number().optional(),
}).meta({
  title: 'Report Generation Result',
  description: 'Result of report generation operation',
});