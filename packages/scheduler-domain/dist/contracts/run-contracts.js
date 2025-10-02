"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RunMetricsSchema = exports.CancelRunInputSchema = exports.RetryRunInputSchema = exports.RunListResponseSchema = exports.RunResponseSchema = exports.RunQuerySchema = void 0;
const zod_1 = require("zod");
const RunMetricsSchema = zod_1.z.object({
    latencyMs: zod_1.z.number().optional(),
    durationMs: zod_1.z.number().optional(),
});
exports.RunMetricsSchema = RunMetricsSchema;
const RunQuerySchema = zod_1.z.object({
    status: zod_1.z.enum(['Pending', 'Running', 'Succeeded', 'Failed', 'Missed', 'Dead']).optional(),
    scheduleId: zod_1.z.string().optional(),
    jobId: zod_1.z.string().optional(),
    workerId: zod_1.z.string().optional(),
    from: zod_1.z.string().datetime().optional(),
    to: zod_1.z.string().datetime().optional(),
    page: zod_1.z.string().transform(val => parseInt(val)).default('1'),
    pageSize: zod_1.z.string().transform(val => Math.min(parseInt(val), 100)).default('20'),
});
exports.RunQuerySchema = RunQuerySchema;
const RunResponseSchema = zod_1.z.object({
    id: zod_1.z.string(),
    tenantId: zod_1.z.string(),
    scheduleId: zod_1.z.string().nullable(),
    jobId: zod_1.z.string().nullable(),
    dedupeKey: zod_1.z.string().nullable(),
    status: zod_1.z.enum(['Pending', 'Running', 'Succeeded', 'Failed', 'Missed', 'Dead']),
    startedAt: zod_1.z.string().datetime().nullable(),
    finishedAt: zod_1.z.string().datetime().nullable(),
    attempt: zod_1.z.number(),
    error: zod_1.z.string().nullable(),
    metrics: zod_1.z.object({
        latencyMs: zod_1.z.number().nullable(),
        durationMs: zod_1.z.number().nullable(),
    }).nullable(),
    workerId: zod_1.z.string().nullable(),
    payload: zod_1.z.record(zod_1.z.string(), zod_1.z.any()).nullable(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
});
exports.RunResponseSchema = RunResponseSchema;
const RunListResponseSchema = zod_1.z.object({
    data: zod_1.z.array(RunResponseSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number(),
    }),
});
exports.RunListResponseSchema = RunListResponseSchema;
const RetryRunInputSchema = zod_1.z.object({
    reason: zod_1.z.string().optional(),
});
exports.RetryRunInputSchema = RetryRunInputSchema;
const CancelRunInputSchema = zod_1.z.object({
    reason: zod_1.z.string().optional(),
});
exports.CancelRunInputSchema = CancelRunInputSchema;
//# sourceMappingURL=run-contracts.js.map