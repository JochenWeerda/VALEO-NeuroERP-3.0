import { z } from 'zod';

// Base schemas
const RunMetricsSchema = z.object({
  latencyMs: z.number().optional(),
  durationMs: z.number().optional(),
});

// Input schemas
const RunQuerySchema = z.object({
  status: z.enum(['Pending', 'Running', 'Succeeded', 'Failed', 'Missed', 'Dead']).optional(),
  scheduleId: z.string().optional(),
  jobId: z.string().optional(),
  workerId: z.string().optional(),
  from: z.string().datetime().optional(),
  to: z.string().datetime().optional(),
  page: z.string().transform(val => parseInt(val)).default('1'),
  pageSize: z.string().transform(val => Math.min(parseInt(val), 100)).default('20'),
});

// Response schemas
const RunResponseSchema = z.object({
  id: z.string(),
  tenantId: z.string(),
  scheduleId: z.string().nullable(),
  jobId: z.string().nullable(),
  dedupeKey: z.string().nullable(),
  status: z.enum(['Pending', 'Running', 'Succeeded', 'Failed', 'Missed', 'Dead']),
  startedAt: z.string().datetime().nullable(),
  finishedAt: z.string().datetime().nullable(),
  attempt: z.number(),
  error: z.string().nullable(),
  metrics: z.object({
    latencyMs: z.number().nullable(),
    durationMs: z.number().nullable(),
  }).nullable(),
  workerId: z.string().nullable(),
  payload: z.record(z.string(), z.any()).nullable(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

const RunListResponseSchema = z.object({
  data: z.array(RunResponseSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number(),
  }),
});

// Action schemas
const RetryRunInputSchema = z.object({
  reason: z.string().optional(),
});

const CancelRunInputSchema = z.object({
  reason: z.string().optional(),
});

// Exports
export {
  RunQuerySchema,
  RunResponseSchema,
  RunListResponseSchema,
  RetryRunInputSchema,
  CancelRunInputSchema,
  RunMetricsSchema,
};