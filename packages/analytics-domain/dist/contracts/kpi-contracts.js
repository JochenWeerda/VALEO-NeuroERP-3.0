"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BulkKpiRecalculationResponseSchema = exports.KpiCalculationResultSchema = exports.RecalculateKpisRequestSchema = exports.KpiListResponseSchema = exports.KpiQuerySchema = exports.KpiResponseSchema = exports.UpdateKpiRequestSchema = exports.CreateKpiRequestSchema = exports.KpiMetadataSchema = exports.KpiContextSchema = void 0;
const zod_1 = require("zod");
const zod_openapi_1 = require("zod-openapi");
(0, zod_openapi_1.extendZodWithOpenApi)(zod_1.z);
exports.KpiContextSchema = zod_1.z.object({
    commodity: zod_1.z.string().optional(),
    contract: zod_1.z.string().optional(),
    batch: zod_1.z.string().optional(),
    site: zod_1.z.string().optional(),
    customer: zod_1.z.string().optional(),
    supplier: zod_1.z.string().optional(),
    period: zod_1.z.string().optional(),
}).openapi({
    title: 'KPI Context',
    description: 'Contextual information for KPI calculation',
});
exports.KpiMetadataSchema = zod_1.z.object({
    calculationMethod: zod_1.z.string().optional(),
    dataSource: zod_1.z.string().optional(),
    lastUpdated: zod_1.z.date().optional(),
    confidence: zod_1.z.number().min(0).max(1).optional(),
    unit: zod_1.z.string().optional(),
}).openapi({
    title: 'KPI Metadata',
    description: 'Additional metadata for KPI',
});
exports.CreateKpiRequestSchema = zod_1.z.object({
    name: zod_1.z.string().min(1).max(100),
    description: zod_1.z.string().min(1).max(500),
    value: zod_1.z.union([zod_1.z.number(), zod_1.z.string(), zod_1.z.boolean()]),
    unit: zod_1.z.string().min(1).max(50),
    context: exports.KpiContextSchema.optional(),
    metadata: exports.KpiMetadataSchema.optional(),
}).openapi({
    title: 'Create KPI Request',
    description: 'Request payload for creating a new KPI',
});
exports.UpdateKpiRequestSchema = zod_1.z.object({
    value: zod_1.z.union([zod_1.z.number(), zod_1.z.string(), zod_1.z.boolean()]).optional(),
    context: exports.KpiContextSchema.optional(),
    metadata: exports.KpiMetadataSchema.optional(),
}).openapi({
    title: 'Update KPI Request',
    description: 'Request payload for updating an existing KPI',
});
exports.KpiResponseSchema = zod_1.z.object({
    id: zod_1.z.string().uuid(),
    tenantId: zod_1.z.string(),
    name: zod_1.z.string(),
    description: zod_1.z.string(),
    value: zod_1.z.union([zod_1.z.number(), zod_1.z.string(), zod_1.z.boolean()]),
    unit: zod_1.z.string(),
    context: exports.KpiContextSchema,
    calculatedAt: zod_1.z.string().datetime(),
    metadata: exports.KpiMetadataSchema.optional(),
    version: zod_1.z.number(),
}).openapi({
    title: 'KPI Response',
    description: 'KPI data response',
});
exports.KpiQuerySchema = zod_1.z.object({
    name: zod_1.z.string().optional(),
    from: zod_1.z.string().datetime().optional(),
    to: zod_1.z.string().datetime().optional(),
    commodity: zod_1.z.string().optional(),
    customer: zod_1.z.string().optional(),
    site: zod_1.z.string().optional(),
    page: zod_1.z.coerce.number().int().min(1).default(1),
    pageSize: zod_1.z.coerce.number().int().min(1).max(100).default(20),
}).openapi({
    title: 'KPI Query Parameters',
    description: 'Query parameters for KPI filtering and pagination',
});
exports.KpiListResponseSchema = zod_1.z.object({
    data: zod_1.z.array(exports.KpiResponseSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number(),
    }),
}).openapi({
    title: 'KPI List Response',
    description: 'Paginated list of KPIs',
});
exports.RecalculateKpisRequestSchema = zod_1.z.object({
    kpiNames: zod_1.z.array(zod_1.z.string()).optional(),
    force: zod_1.z.boolean().default(false),
}).openapi({
    title: 'Recalculate KPIs Request',
    description: 'Request to recalculate KPIs',
});
exports.KpiCalculationResultSchema = zod_1.z.object({
    kpiId: zod_1.z.string().uuid(),
    kpiName: zod_1.z.string(),
    success: zod_1.z.boolean(),
    value: zod_1.z.union([zod_1.z.number(), zod_1.z.string(), zod_1.z.boolean()]).optional(),
    error: zod_1.z.string().optional(),
    executionTimeMs: zod_1.z.number(),
}).openapi({
    title: 'KPI Calculation Result',
    description: 'Result of a KPI calculation operation',
});
exports.BulkKpiRecalculationResponseSchema = zod_1.z.object({
    totalRequested: zod_1.z.number(),
    successful: zod_1.z.number(),
    failed: zod_1.z.number(),
    results: zod_1.z.array(exports.KpiCalculationResultSchema),
    executionTimeMs: zod_1.z.number(),
}).openapi({
    title: 'Bulk KPI Recalculation Response',
    description: 'Response for bulk KPI recalculation operation',
});
//# sourceMappingURL=kpi-contracts.js.map