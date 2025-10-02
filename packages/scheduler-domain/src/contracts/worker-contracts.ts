import { z } from 'zod';

// Base schemas
const WorkerCapabilitiesSchema = z.object({
  queues: z.array(z.string()).default(['default']),
  jobKeys: z.array(z.string()).default([]),
});

// Input schemas
const RegisterWorkerInputSchema = z.object({
  name: z.string().min(1, 'Worker name is required'),
  capabilities: WorkerCapabilitiesSchema,
  maxParallel: z.number().int().min(1).default(10),
});

const WorkerHeartbeatInputSchema = z.object({
  status: z.enum(['Online', 'Offline', 'Maintenance']).optional(),
});

const WorkerQuerySchema = z.object({
  status: z.enum(['Online', 'Offline', 'Maintenance']).optional(),
  name: z.string().optional(),
  page: z.string().transform(val => parseInt(val)).default('1'),
  pageSize: z.string().transform(val => Math.min(parseInt(val), 100)).default('20'),
});

// Response schemas
const WorkerResponseSchema = z.object({
  id: z.string(),
  tenantId: z.string().nullable(),
  name: z.string(),
  capabilities: WorkerCapabilitiesSchema,
  heartbeatAt: z.string().datetime(),
  status: z.enum(['Online', 'Offline', 'Maintenance']),
  maxParallel: z.number(),
  currentJobs: z.number(),
  version: z.number(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

const WorkerListResponseSchema = z.object({
  data: z.array(WorkerResponseSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number(),
  }),
});

// Exports
export {
  RegisterWorkerInputSchema,
  WorkerHeartbeatInputSchema,
  WorkerQuerySchema,
  WorkerResponseSchema,
  WorkerListResponseSchema,
  WorkerCapabilitiesSchema,
};