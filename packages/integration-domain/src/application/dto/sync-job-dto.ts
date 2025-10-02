/**
 * Sync Job DTOs and Validation Schemas
 */

import { z } from 'zod';

// Base schemas
const SyncJobStatusSchema = z.enum(['pending', 'running', 'completed', 'failed', 'cancelled']);
const SourceTypeSchema = z.enum(['database', 'api', 'file', 'message-queue']);
const TargetTypeSchema = z.enum(['database', 'api', 'file', 'message-queue']);

// Request DTOs
export const CreateSyncJobRequestSchema = z.object({
  name: z.string().min(1).max(255),
  integrationId: z.string().uuid(),
  config: z.object({
    source: z.object({
      type: SourceTypeSchema,
      connection: z.record(z.unknown()),
      query: z.string().optional(),
      filters: z.record(z.unknown()).optional()
    }),
    target: z.object({
      type: TargetTypeSchema,
      connection: z.record(z.unknown()),
      mapping: z.record(z.string()).optional(),
      batchSize: z.number().min(1).max(10000).default(100)
    }),
    schedule: z.object({
      cron: z.string().optional(),
      interval: z.number().min(60).optional(), // minimum 60 seconds
      timezone: z.string().optional()
    }).optional(),
    retryPolicy: z.object({
      maxRetries: z.number().min(0).max(10),
      backoffMs: z.number().min(100).max(60000)
    }).optional()
  }),
  description: z.string().optional(),
  tags: z.array(z.string()).default([])
});

export const UpdateSyncJobRequestSchema = z.object({
  name: z.string().min(1).max(255).optional(),
  config: z.object({
    source: z.object({
      type: SourceTypeSchema,
      connection: z.record(z.unknown()),
      query: z.string().optional(),
      filters: z.record(z.unknown()).optional()
    }),
    target: z.object({
      type: TargetTypeSchema,
      connection: z.record(z.unknown()),
      mapping: z.record(z.string()).optional(),
      batchSize: z.number().min(1).max(10000).default(100)
    }),
    schedule: z.object({
      cron: z.string().optional(),
      interval: z.number().min(60).optional(),
      timezone: z.string().optional()
    }).optional(),
    retryPolicy: z.object({
      maxRetries: z.number().min(0).max(10),
      backoffMs: z.number().min(100).max(60000)
    }).optional()
  }).optional(),
  description: z.string().optional(),
  tags: z.array(z.string()).optional(),
  status: SyncJobStatusSchema.optional(),
  isActive: z.boolean().optional()
});

export const ExecuteSyncJobRequestSchema = z.object({
  force: z.boolean().default(false),
  batchSize: z.number().min(1).max(10000).optional()
});

export const SyncJobQuerySchema = z.object({
  page: z.number().min(1).default(1),
  limit: z.number().min(1).max(100).default(10),
  sortBy: z.string().optional(),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
  integrationId: z.string().uuid().optional(),
  status: SyncJobStatusSchema.optional(),
  isActive: z.boolean().optional()
});

// Response DTOs
export const SyncJobResponseSchema = z.object({
  id: z.string(),
  name: z.string(),
  integrationId: z.string(),
  config: z.record(z.unknown()),
  status: SyncJobStatusSchema,
  lastRun: z.string().nullable(),
  nextRun: z.string().nullable(),
  recordsProcessed: z.number(),
  errorMessage: z.string().nullable(),
  isActive: z.boolean(),
  description: z.string().nullable(),
  tags: z.array(z.string()),
  createdAt: z.string(),
  updatedAt: z.string(),
  createdBy: z.string(),
  updatedBy: z.string()
});

export const SyncJobListResponseSchema = z.object({
  data: z.array(SyncJobResponseSchema),
  pagination: z.object({
    page: z.number(),
    limit: z.number(),
    total: z.number(),
    totalPages: z.number(),
    hasNext: z.boolean(),
    hasPrev: z.boolean()
  })
});

export const SyncJobExecutionResponseSchema = z.object({
  success: z.boolean(),
  recordsProcessed: z.number(),
  duration: z.number(),
  error: z.string().optional(),
  nextRun: z.string().optional()
});

// Type exports
export type CreateSyncJobRequest = z.infer<typeof CreateSyncJobRequestSchema>;
export type UpdateSyncJobRequest = z.infer<typeof UpdateSyncJobRequestSchema>;
export type ExecuteSyncJobRequest = z.infer<typeof ExecuteSyncJobRequestSchema>;
export type SyncJobQuery = z.infer<typeof SyncJobQuerySchema>;
export type SyncJobResponse = z.infer<typeof SyncJobResponseSchema>;
export type SyncJobListResponse = z.infer<typeof SyncJobListResponseSchema>;
export type SyncJobExecutionResponse = z.infer<typeof SyncJobExecutionResponseSchema>;

// Validation functions
export function validateCreateSyncJobRequest(data: unknown): CreateSyncJobRequest {
  return CreateSyncJobRequestSchema.parse(data);
}

export function validateUpdateSyncJobRequest(data: unknown): UpdateSyncJobRequest {
  return UpdateSyncJobRequestSchema.parse(data);
}

export function validateExecuteSyncJobRequest(data: unknown): ExecuteSyncJobRequest {
  return ExecuteSyncJobRequestSchema.parse(data);
}

export function validateSyncJobQuery(data: unknown): SyncJobQuery {
  return SyncJobQuerySchema.parse(data);
}
