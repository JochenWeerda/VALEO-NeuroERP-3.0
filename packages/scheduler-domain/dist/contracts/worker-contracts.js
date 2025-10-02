"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WorkerCapabilitiesSchema = exports.WorkerListResponseSchema = exports.WorkerResponseSchema = exports.WorkerQuerySchema = exports.WorkerHeartbeatInputSchema = exports.RegisterWorkerInputSchema = void 0;
const zod_1 = require("zod");
const WorkerCapabilitiesSchema = zod_1.z.object({
    queues: zod_1.z.array(zod_1.z.string()).default(['default']),
    jobKeys: zod_1.z.array(zod_1.z.string()).default([]),
});
exports.WorkerCapabilitiesSchema = WorkerCapabilitiesSchema;
const RegisterWorkerInputSchema = zod_1.z.object({
    name: zod_1.z.string().min(1, 'Worker name is required'),
    capabilities: WorkerCapabilitiesSchema,
    maxParallel: zod_1.z.number().int().min(1).default(10),
});
exports.RegisterWorkerInputSchema = RegisterWorkerInputSchema;
const WorkerHeartbeatInputSchema = zod_1.z.object({
    status: zod_1.z.enum(['Online', 'Offline', 'Maintenance']).optional(),
});
exports.WorkerHeartbeatInputSchema = WorkerHeartbeatInputSchema;
const WorkerQuerySchema = zod_1.z.object({
    status: zod_1.z.enum(['Online', 'Offline', 'Maintenance']).optional(),
    name: zod_1.z.string().optional(),
    page: zod_1.z.string().transform(val => parseInt(val)).default('1'),
    pageSize: zod_1.z.string().transform(val => Math.min(parseInt(val), 100)).default('20'),
});
exports.WorkerQuerySchema = WorkerQuerySchema;
const WorkerResponseSchema = zod_1.z.object({
    id: zod_1.z.string(),
    tenantId: zod_1.z.string().nullable(),
    name: zod_1.z.string(),
    capabilities: WorkerCapabilitiesSchema,
    heartbeatAt: zod_1.z.string().datetime(),
    status: zod_1.z.enum(['Online', 'Offline', 'Maintenance']),
    maxParallel: zod_1.z.number(),
    currentJobs: zod_1.z.number(),
    version: zod_1.z.number(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
});
exports.WorkerResponseSchema = WorkerResponseSchema;
const WorkerListResponseSchema = zod_1.z.object({
    data: zod_1.z.array(WorkerResponseSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number(),
    }),
});
exports.WorkerListResponseSchema = WorkerListResponseSchema;
//# sourceMappingURL=worker-contracts.js.map