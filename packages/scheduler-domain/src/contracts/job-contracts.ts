import { z } from 'zod';

// Base schemas
const BackoffConfigSchema = z.object({
  strategy: z.enum(['FIXED', 'EXPONENTIAL']).default('EXPONENTIAL'),
  baseSec: z.number().int().positive().default(60),
  maxSec: z.number().int().positive().optional(),
});

// Input schemas
const CreateJobInputSchema = z.object({
  key: z.string().min(1, 'Job key is required'),
  queue: z.string().default('default'),
  priority: z.number().int().min(1).max(9).default(5),
  maxAttempts: z.number().int().min(1).default(3),
  backoff: BackoffConfigSchema.default({ strategy: 'EXPONENTIAL', baseSec: 60 }),
  timeoutSec: z.number().int().min(1).default(300),
  concurrencyLimit: z.number().int().min(1).optional(),
  slaSec: z.number().int().min(1).optional(),
  enabled: z.boolean().default(true),
});

const UpdateJobInputSchema = z.object({
  queue: z.string().optional(),
  priority: z.number().int().min(1).max(9).optional(),
  maxAttempts: z.number().int().min(1).optional(),
  backoff: BackoffConfigSchema.optional(),
  timeoutSec: z.number().int().min(1).optional(),
  concurrencyLimit: z.number().int().min(1).nullable().optional(),
  slaSec: z.number().int().min(1).nullable().optional(),
  enabled: z.boolean().optional(),
});

const JobQuerySchema = z.object({
  enabled: z.string().transform(val => val === 'true').optional(),
  queue: z.string().optional(),
  key: z.string().optional(),
  page: z.string().transform(val => parseInt(val)).default('1'),
  pageSize: z.string().transform(val => Math.min(parseInt(val), 100)).default('20'),
});

// Response schemas
const JobResponseSchema = z.object({
  id: z.string(),
  tenantId: z.string(),
  key: z.string(),
  queue: z.string(),
  priority: z.number(),
  maxAttempts: z.number(),
  backoff: BackoffConfigSchema,
  timeoutSec: z.number(),
  concurrencyLimit: z.number().nullable(),
  slaSec: z.number().nullable(),
  enabled: z.boolean(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  version: z.number(),
});

const JobListResponseSchema = z.object({
  data: z.array(JobResponseSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number(),
  }),
});

// Exports
export {
  CreateJobInputSchema,
  UpdateJobInputSchema,
  JobQuerySchema,
  JobResponseSchema,
  JobListResponseSchema,
  BackoffConfigSchema,
};