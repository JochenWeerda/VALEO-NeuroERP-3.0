import { z } from 'zod';

// Base schemas
const TriggerSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('CRON'),
    cron: z.string().min(1, 'CRON expression is required'),
  }),
  z.object({
    type: z.literal('RRULE'),
    rrule: z.string().min(1, 'RRULE is required'),
  }),
  z.object({
    type: z.literal('FIXED_DELAY'),
    delaySec: z.number().int().positive('Delay must be positive'),
  }),
  z.object({
    type: z.literal('ONE_SHOT'),
    startAt: z.string().datetime('Invalid datetime format'),
  }),
]);

const TargetSchema = z.discriminatedUnion('kind', [
  z.object({
    kind: z.literal('EVENT'),
    eventTopic: z.string().min(1, 'Event topic is required'),
  }),
  z.object({
    kind: z.literal('HTTP'),
    http: z.object({
      url: z.string().url('Invalid URL'),
      method: z.enum(['GET', 'POST', 'PUT', 'PATCH', 'DELETE']).default('POST'),
      headers: z.record(z.string(), z.string()).optional(),
      hmacKeyRef: z.string().optional(),
    }),
  }),
  z.object({
    kind: z.literal('QUEUE'),
    queue: z.object({
      topic: z.string().min(1, 'Queue topic is required'),
    }),
  }),
]);

const CalendarConfigSchema = z.object({
  holidaysCode: z.string().optional(),
  businessDaysOnly: z.boolean().default(false),
});

// Input schemas
const CreateScheduleInputSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  description: z.string().optional(),
  tz: z.string().default('Europe/Berlin'),
  trigger: TriggerSchema,
  target: TargetSchema,
  payload: z.record(z.string(), z.any()).optional(),
  calendar: CalendarConfigSchema.optional(),
  enabled: z.boolean().default(true),
});

const UpdateScheduleInputSchema = z.object({
  name: z.string().min(1).optional(),
  description: z.string().nullable().optional(),
  tz: z.string().optional(),
  trigger: TriggerSchema.optional(),
  target: TargetSchema.optional(),
  payload: z.record(z.string(), z.any()).optional(),
  calendar: CalendarConfigSchema.optional(),
  enabled: z.boolean().optional(),
});

const ScheduleQuerySchema = z.object({
  enabled: z.string().transform(val => val === 'true').optional(),
  name: z.string().optional(),
  tz: z.string().optional(),
  page: z.string().transform(val => parseInt(val)).default('1'),
  pageSize: z.string().transform(val => Math.min(parseInt(val), 100)).default('20'),
});

// Response schemas
const ScheduleResponseSchema = z.object({
  id: z.string(),
  tenantId: z.string(),
  name: z.string(),
  description: z.string().nullable(),
  tz: z.string(),
  trigger: TriggerSchema,
  target: TargetSchema,
  payload: z.record(z.string(), z.any()).nullable(),
  calendar: CalendarConfigSchema.nullable(),
  enabled: z.boolean(),
  nextFireAt: z.string().datetime().nullable(),
  lastFireAt: z.string().datetime().nullable(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  version: z.number(),
});

const ScheduleListResponseSchema = z.object({
  data: z.array(ScheduleResponseSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number(),
  }),
});

// Trigger schemas
const ManualTriggerInputSchema = z.object({
  fireTime: z.string().datetime().optional(),
  payload: z.record(z.string(), z.any()).optional(),
});

const BackfillInputSchema = z.object({
  from: z.string().datetime(),
  to: z.string().datetime(),
  step: z.string().regex(/^P(\d+Y)?(\d+M)?(\d+D)?T?(\d+H)?(\d+M)?(\d+S)?$/, 'Invalid ISO 8601 duration'),
  maxRuns: z.number().int().positive().max(1000).optional(),
});

// OpenAPI metadata will be added when integrating with Fastify

// Exports
export {
  CreateScheduleInputSchema,
  UpdateScheduleInputSchema,
  ScheduleQuerySchema,
  ScheduleResponseSchema,
  ScheduleListResponseSchema,
  ManualTriggerInputSchema,
  BackfillInputSchema,
  TriggerSchema,
  TargetSchema,
  CalendarConfigSchema,
};