"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BulkCubeRefreshResponseSchema = exports.CubeRefreshResultSchema = exports.CubeRefreshRequestSchema = exports.FinanceResponseSchema = exports.FinanceQuerySchema = exports.RegulatoryResponseSchema = exports.RegulatoryQuerySchema = exports.QualityResponseSchema = exports.QualityQuerySchema = exports.WeighingVolumeResponseSchema = exports.WeighingVolumeQuerySchema = exports.ContractPositionResponseSchema = exports.ContractPositionQuerySchema = exports.CubeQueryBaseSchema = exports.FinanceCubeSchema = exports.RegulatoryCubeSchema = exports.QualityCubeSchema = exports.WeighingVolumeCubeSchema = exports.ContractPositionCubeSchema = void 0;
const zod_1 = require("zod");
const zod_openapi_1 = require("zod-openapi");
(0, zod_openapi_1.extendZodWithOpenApi)(zod_1.z);
exports.ContractPositionCubeSchema = zod_1.z.object({
    tenantId: zod_1.z.string(),
    commodity: zod_1.z.string(),
    month: zod_1.z.string(),
    shortPosition: zod_1.z.number(),
    longPosition: zod_1.z.number(),
    netPosition: zod_1.z.number(),
    hedgingRatio: zod_1.z.number().optional(),
    lastUpdated: zod_1.z.string().datetime(),
}).openapi({
    title: 'Contract Position Cube',
    description: 'Aggregated contract positions by commodity and month',
});
exports.WeighingVolumeCubeSchema = zod_1.z.object({
    tenantId: zod_1.z.string(),
    commodity: zod_1.z.string(),
    customerId: zod_1.z.string().optional(),
    siteId: zod_1.z.string().optional(),
    period: zod_1.z.string(),
    totalWeight: zod_1.z.number(),
    totalTickets: zod_1.z.number(),
    avgWeight: zod_1.z.number(),
    withinTolerance: zod_1.z.number(),
    outsideTolerance: zod_1.z.number(),
    lastUpdated: zod_1.z.string().datetime(),
}).openapi({
    title: 'Weighing Volume Cube',
    description: 'Aggregated weighing volumes by various dimensions',
});
exports.QualityCubeSchema = zod_1.z.object({
    tenantId: zod_1.z.string(),
    commodity: zod_1.z.string(),
    period: zod_1.z.string(),
    totalSamples: zod_1.z.number(),
    passedSamples: zod_1.z.number(),
    failedSamples: zod_1.z.number(),
    passRate: zod_1.z.number(),
    failureRate: zod_1.z.number(),
    avgMoisture: zod_1.z.number().optional(),
    avgProtein: zod_1.z.number().optional(),
    lastUpdated: zod_1.z.string().datetime(),
}).openapi({
    title: 'Quality Cube',
    description: 'Aggregated quality metrics by commodity and period',
});
exports.RegulatoryCubeSchema = zod_1.z.object({
    tenantId: zod_1.z.string(),
    commodity: zod_1.z.string(),
    labelType: zod_1.z.string(),
    period: zod_1.z.string(),
    totalEligible: zod_1.z.number(),
    totalIneligible: zod_1.z.number(),
    eligibilityRate: zod_1.z.number(),
    ineligibilityRate: zod_1.z.number(),
    lastUpdated: zod_1.z.string().datetime(),
}).openapi({
    title: 'Regulatory Cube',
    description: 'Aggregated regulatory compliance metrics',
});
exports.FinanceCubeSchema = zod_1.z.object({
    tenantId: zod_1.z.string(),
    commodity: zod_1.z.string(),
    customerId: zod_1.z.string().optional(),
    period: zod_1.z.string(),
    totalRevenue: zod_1.z.number(),
    totalCost: zod_1.z.number(),
    grossMargin: zod_1.z.number(),
    marginPercentage: zod_1.z.number(),
    outstandingInvoices: zod_1.z.number(),
    overdueInvoices: zod_1.z.number(),
    lastUpdated: zod_1.z.string().datetime(),
}).openapi({
    title: 'Finance Cube',
    description: 'Aggregated financial metrics by commodity and period',
});
exports.CubeQueryBaseSchema = zod_1.z.object({
    tenantId: zod_1.z.string(),
    from: zod_1.z.string().datetime().optional(),
    to: zod_1.z.string().datetime().optional(),
    commodity: zod_1.z.string().optional(),
    customerId: zod_1.z.string().optional(),
    siteId: zod_1.z.string().optional(),
    page: zod_1.z.coerce.number().int().min(1).default(1),
    pageSize: zod_1.z.coerce.number().int().min(1).max(1000).default(100),
}).openapi({
    title: 'Cube Query Base Parameters',
    description: 'Base query parameters for cube operations',
});
exports.ContractPositionQuerySchema = exports.CubeQueryBaseSchema.extend({
    month: zod_1.z.string().optional(),
}).openapi({
    title: 'Contract Position Query',
    description: 'Query parameters for contract position cube',
});
exports.ContractPositionResponseSchema = zod_1.z.object({
    data: zod_1.z.array(exports.ContractPositionCubeSchema),
    summary: zod_1.z.object({
        totalShort: zod_1.z.number(),
        totalLong: zod_1.z.number(),
        netExposure: zod_1.z.number(),
        avgHedgingRatio: zod_1.z.number().optional(),
    }).optional(),
}).openapi({
    title: 'Contract Position Response',
    description: 'Contract position cube data with summary',
});
exports.WeighingVolumeQuerySchema = exports.CubeQueryBaseSchema.extend({
    period: zod_1.z.string().optional(),
    groupBy: zod_1.z.enum(['day', 'week', 'month']).default('month'),
}).openapi({
    title: 'Weighing Volume Query',
    description: 'Query parameters for weighing volume cube',
});
exports.WeighingVolumeResponseSchema = zod_1.z.object({
    data: zod_1.z.array(exports.WeighingVolumeCubeSchema),
    summary: zod_1.z.object({
        totalWeight: zod_1.z.number(),
        totalTickets: zod_1.z.number(),
        avgWeightPerTicket: zod_1.z.number(),
        overallToleranceRate: zod_1.z.number(),
    }).optional(),
}).openapi({
    title: 'Weighing Volume Response',
    description: 'Weighing volume cube data with summary',
});
exports.QualityQuerySchema = exports.CubeQueryBaseSchema.extend({
    period: zod_1.z.string().optional(),
}).openapi({
    title: 'Quality Query',
    description: 'Query parameters for quality cube',
});
exports.QualityResponseSchema = zod_1.z.object({
    data: zod_1.z.array(exports.QualityCubeSchema),
    summary: zod_1.z.object({
        totalSamples: zod_1.z.number(),
        overallPassRate: zod_1.z.number(),
        avgMoisture: zod_1.z.number().optional(),
        avgProtein: zod_1.z.number().optional(),
    }).optional(),
}).openapi({
    title: 'Quality Response',
    description: 'Quality cube data with summary',
});
exports.RegulatoryQuerySchema = exports.CubeQueryBaseSchema.extend({
    labelType: zod_1.z.string().optional(),
    period: zod_1.z.string().optional(),
}).openapi({
    title: 'Regulatory Query',
    description: 'Query parameters for regulatory cube',
});
exports.RegulatoryResponseSchema = zod_1.z.object({
    data: zod_1.z.array(exports.RegulatoryCubeSchema),
    summary: zod_1.z.object({
        totalEligible: zod_1.z.number(),
        totalIneligible: zod_1.z.number(),
        overallEligibilityRate: zod_1.z.number(),
    }).optional(),
}).openapi({
    title: 'Regulatory Response',
    description: 'Regulatory cube data with summary',
});
exports.FinanceQuerySchema = exports.CubeQueryBaseSchema.extend({
    period: zod_1.z.string().optional(),
}).openapi({
    title: 'Finance Query',
    description: 'Query parameters for finance cube',
});
exports.FinanceResponseSchema = zod_1.z.object({
    data: zod_1.z.array(exports.FinanceCubeSchema),
    summary: zod_1.z.object({
        totalRevenue: zod_1.z.number(),
        totalCost: zod_1.z.number(),
        totalMargin: zod_1.z.number(),
        avgMarginPercentage: zod_1.z.number(),
        totalOutstanding: zod_1.z.number(),
        totalOverdue: zod_1.z.number(),
    }).optional(),
}).openapi({
    title: 'Finance Response',
    description: 'Finance cube data with summary',
});
exports.CubeRefreshRequestSchema = zod_1.z.object({
    cubeNames: zod_1.z.array(zod_1.z.string()).optional(),
    force: zod_1.z.boolean().default(false),
}).openapi({
    title: 'Cube Refresh Request',
    description: 'Request to refresh materialized view cubes',
});
exports.CubeRefreshResultSchema = zod_1.z.object({
    cubeName: zod_1.z.string(),
    success: zod_1.z.boolean(),
    recordCount: zod_1.z.number().optional(),
    executionTimeMs: zod_1.z.number(),
    error: zod_1.z.string().optional(),
    refreshedAt: zod_1.z.string().datetime(),
}).openapi({
    title: 'Cube Refresh Result',
    description: 'Result of a cube refresh operation',
});
exports.BulkCubeRefreshResponseSchema = zod_1.z.object({
    totalRequested: zod_1.z.number(),
    successful: zod_1.z.number(),
    failed: zod_1.z.number(),
    results: zod_1.z.array(exports.CubeRefreshResultSchema),
    totalExecutionTimeMs: zod_1.z.number(),
}).openapi({
    title: 'Bulk Cube Refresh Response',
    description: 'Response for bulk cube refresh operation',
});
//# sourceMappingURL=cube-contracts.js.map