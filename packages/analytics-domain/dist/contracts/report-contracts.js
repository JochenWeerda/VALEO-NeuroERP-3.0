"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ReportGenerationResultSchema = exports.ReportGenerationStatusSchema = exports.ReportContentResponseSchema = exports.ReportListResponseSchema = exports.ReportQuerySchema = exports.ReportResponseSchema = exports.GenerateReportRequestSchema = exports.ReportMetadataSchema = exports.ReportParametersSchema = exports.ReportFormatSchema = exports.ReportTypeSchema = void 0;
const zod_1 = require("zod");
const zod_openapi_1 = require("zod-openapi");
(0, zod_openapi_1.extendZodWithOpenApi)(zod_1.z);
exports.ReportTypeSchema = zod_1.z.enum([
    'Contracts',
    'Inventory',
    'Weighing',
    'Finance',
    'Quality',
    'Production',
    'Regulatory',
    'Custom'
]).openapi({
    title: 'Report Type',
    description: 'Type of report to generate',
});
exports.ReportFormatSchema = zod_1.z.enum([
    'json',
    'csv',
    'excel',
    'pdf'
]).openapi({
    title: 'Report Format',
    description: 'Output format for the report',
});
exports.ReportParametersSchema = zod_1.z.object({
    tenantId: zod_1.z.string(),
    dateFrom: zod_1.z.string().datetime().optional(),
    dateTo: zod_1.z.string().datetime().optional(),
    commodity: zod_1.z.string().optional(),
    customerId: zod_1.z.string().optional(),
    supplierId: zod_1.z.string().optional(),
    siteId: zod_1.z.string().optional(),
    status: zod_1.z.string().optional(),
    filters: zod_1.z.record(zod_1.z.any()).optional(),
}).openapi({
    title: 'Report Parameters',
    description: 'Parameters for report generation',
});
exports.ReportMetadataSchema = zod_1.z.object({
    totalRecords: zod_1.z.number().optional(),
    executionTimeMs: zod_1.z.number().optional(),
    dataSource: zod_1.z.string().optional(),
    generatedBy: zod_1.z.string().optional(),
    checksum: zod_1.z.string().optional(),
}).openapi({
    title: 'Report Metadata',
    description: 'Metadata about report generation',
});
exports.GenerateReportRequestSchema = zod_1.z.object({
    type: exports.ReportTypeSchema,
    parameters: exports.ReportParametersSchema,
    format: exports.ReportFormatSchema.default('json'),
}).openapi({
    title: 'Generate Report Request',
    description: 'Request payload for generating a report',
});
exports.ReportResponseSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string(),
    type: exports.ReportTypeSchema,
    parameters: exports.ReportParametersSchema,
    generatedAt: zod_1.z.string().datetime(),
    uri: zod_1.z.string().optional(),
    format: exports.ReportFormatSchema,
    metadata: exports.ReportMetadataSchema.optional(),
    version: zod_1.z.number(),
}).openapi({
    title: 'Report Response',
    description: 'Report data response',
});
exports.ReportQuerySchema = zod_1.z.object({
    type: exports.ReportTypeSchema.optional(),
    from: zod_1.z.string().datetime().optional(),
    to: zod_1.z.string().datetime().optional(),
    format: exports.ReportFormatSchema.optional(),
    page: zod_1.z.coerce.number().int().min(1).default(1),
    pageSize: zod_1.z.coerce.number().int().min(1).max(100).default(20),
}).openapi({
    title: 'Report Query Parameters',
    description: 'Query parameters for report filtering and pagination',
});
exports.ReportListResponseSchema = zod_1.z.object({
    data: zod_1.z.array(exports.ReportResponseSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number(),
    }),
}).openapi({
    title: 'Report List Response',
    description: 'Paginated list of reports',
});
exports.ReportContentResponseSchema = zod_1.z.object({
    report: exports.ReportResponseSchema,
    content: zod_1.z.any(),
    contentType: zod_1.z.string(),
    contentLength: zod_1.z.number(),
}).openapi({
    title: 'Report Content Response',
    description: 'Report with its content data',
});
exports.ReportGenerationStatusSchema = zod_1.z.enum([
    'pending',
    'processing',
    'completed',
    'failed'
]).openapi({
    title: 'Report Generation Status',
    description: 'Status of report generation process',
});
exports.ReportGenerationResultSchema = zod_1.z.object({
    reportId: zod_1.z.string().uuid(),
    status: exports.ReportGenerationStatusSchema,
    progress: zod_1.z.number().min(0).max(100).optional(),
    message: zod_1.z.string().optional(),
    uri: zod_1.z.string().optional(),
    error: zod_1.z.string().optional(),
    executionTimeMs: zod_1.z.number().optional(),
}).openapi({
    title: 'Report Generation Result',
    description: 'Result of report generation operation',
});
//# sourceMappingURL=report-contracts.js.map