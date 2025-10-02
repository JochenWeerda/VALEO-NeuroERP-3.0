"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BackoffConfigSchema = exports.JobListResponseSchema = exports.JobResponseSchema = exports.JobQuerySchema = exports.UpdateJobInputSchema = exports.CreateJobInputSchema = void 0;
const zod_1 = require("zod");
const BackoffConfigSchema = zod_1.z.object({
    strategy: zod_1.z.enum(['FIXED', 'EXPONENTIAL']).default('EXPONENTIAL'),
    baseSec: zod_1.z.number().int().positive().default(60),
    maxSec: zod_1.z.number().int().positive().optional(),
});
exports.BackoffConfigSchema = BackoffConfigSchema;
const CreateJobInputSchema = zod_1.z.object({
    key: zod_1.z.string().min(1, 'Job key is required'),
    queue: zod_1.z.string().default('default'),
    priority: zod_1.z.number().int().min(1).max(9).default(5),
    maxAttempts: zod_1.z.number().int().min(1).default(3),
    backoff: BackoffConfigSchema.default({ strategy: 'EXPONENTIAL', baseSec: 60 }),
    timeoutSec: zod_1.z.number().int().min(1).default(300),
    concurrencyLimit: zod_1.z.number().int().min(1).optional(),
    slaSec: zod_1.z.number().int().min(1).optional(),
    enabled: zod_1.z.boolean().default(true),
});
exports.CreateJobInputSchema = CreateJobInputSchema;
const UpdateJobInputSchema = zod_1.z.object({
    queue: zod_1.z.string().optional(),
    priority: zod_1.z.number().int().min(1).max(9).optional(),
    maxAttempts: zod_1.z.number().int().min(1).optional(),
    backoff: BackoffConfigSchema.optional(),
    timeoutSec: zod_1.z.number().int().min(1).optional(),
    concurrencyLimit: zod_1.z.number().int().min(1).nullable().optional(),
    slaSec: zod_1.z.number().int().min(1).nullable().optional(),
    enabled: zod_1.z.boolean().optional(),
});
exports.UpdateJobInputSchema = UpdateJobInputSchema;
const JobQuerySchema = zod_1.z.object({
    enabled: zod_1.z.string().transform(val => val === 'true').optional(),
    queue: zod_1.z.string().optional(),
    key: zod_1.z.string().optional(),
    page: zod_1.z.string().transform(val => parseInt(val)).default('1'),
    pageSize: zod_1.z.string().transform(val => Math.min(parseInt(val), 100)).default('20'),
});
exports.JobQuerySchema = JobQuerySchema;
const JobResponseSchema = zod_1.z.object({
    id: zod_1.z.string(),
    tenantId: zod_1.z.string(),
    key: zod_1.z.string(),
    queue: zod_1.z.string(),
    priority: zod_1.z.number(),
    maxAttempts: zod_1.z.number(),
    backoff: BackoffConfigSchema,
    timeoutSec: zod_1.z.number(),
    concurrencyLimit: zod_1.z.number().nullable(),
    slaSec: zod_1.z.number().nullable(),
    enabled: zod_1.z.boolean(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    version: zod_1.z.number(),
});
exports.JobResponseSchema = JobResponseSchema;
const JobListResponseSchema = zod_1.z.object({
    data: zod_1.z.array(JobResponseSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number(),
    }),
});
exports.JobListResponseSchema = JobListResponseSchema;
//# sourceMappingURL=job-contracts.js.map