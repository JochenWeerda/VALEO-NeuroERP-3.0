"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.CalendarConfigSchema = exports.TargetSchema = exports.TriggerSchema = exports.BackfillInputSchema = exports.ManualTriggerInputSchema = exports.ScheduleListResponseSchema = exports.ScheduleResponseSchema = exports.ScheduleQuerySchema = exports.UpdateScheduleInputSchema = exports.CreateScheduleInputSchema = void 0;
const zod_1 = require("zod");
const TriggerSchema = zod_1.z.discriminatedUnion('type', [
    zod_1.z.object({
        type: zod_1.z.literal('CRON'),
        cron: zod_1.z.string().min(1, 'CRON expression is required'),
    }),
    zod_1.z.object({
        type: zod_1.z.literal('RRULE'),
        rrule: zod_1.z.string().min(1, 'RRULE is required'),
    }),
    zod_1.z.object({
        type: zod_1.z.literal('FIXED_DELAY'),
        delaySec: zod_1.z.number().int().positive('Delay must be positive'),
    }),
    zod_1.z.object({
        type: zod_1.z.literal('ONE_SHOT'),
        startAt: zod_1.z.string().datetime('Invalid datetime format'),
    }),
]);
exports.TriggerSchema = TriggerSchema;
const TargetSchema = zod_1.z.discriminatedUnion('kind', [
    zod_1.z.object({
        kind: zod_1.z.literal('EVENT'),
        eventTopic: zod_1.z.string().min(1, 'Event topic is required'),
    }),
    zod_1.z.object({
        kind: zod_1.z.literal('HTTP'),
        http: zod_1.z.object({
            url: zod_1.z.string().url('Invalid URL'),
            method: zod_1.z.enum(['GET', 'POST', 'PUT', 'PATCH', 'DELETE']).default('POST'),
            headers: zod_1.z.record(zod_1.z.string(), zod_1.z.string()).optional(),
            hmacKeyRef: zod_1.z.string().optional(),
        }),
    }),
    zod_1.z.object({
        kind: zod_1.z.literal('QUEUE'),
        queue: zod_1.z.object({
            topic: zod_1.z.string().min(1, 'Queue topic is required'),
        }),
    }),
]);
exports.TargetSchema = TargetSchema;
const CalendarConfigSchema = zod_1.z.object({
    holidaysCode: zod_1.z.string().optional(),
    businessDaysOnly: zod_1.z.boolean().default(false),
});
exports.CalendarConfigSchema = CalendarConfigSchema;
const CreateScheduleInputSchema = zod_1.z.object({
    name: zod_1.z.string().min(1, 'Name is required'),
    description: zod_1.z.string().optional(),
    tz: zod_1.z.string().default('Europe/Berlin'),
    trigger: TriggerSchema,
    target: TargetSchema,
    payload: zod_1.z.record(zod_1.z.string(), zod_1.z.any()).optional(),
    calendar: CalendarConfigSchema.optional(),
    enabled: zod_1.z.boolean().default(true),
});
exports.CreateScheduleInputSchema = CreateScheduleInputSchema;
const UpdateScheduleInputSchema = zod_1.z.object({
    name: zod_1.z.string().min(1).optional(),
    description: zod_1.z.string().nullable().optional(),
    tz: zod_1.z.string().optional(),
    trigger: TriggerSchema.optional(),
    target: TargetSchema.optional(),
    payload: zod_1.z.record(zod_1.z.string(), zod_1.z.any()).optional(),
    calendar: CalendarConfigSchema.optional(),
    enabled: zod_1.z.boolean().optional(),
});
exports.UpdateScheduleInputSchema = UpdateScheduleInputSchema;
const ScheduleQuerySchema = zod_1.z.object({
    enabled: zod_1.z.string().transform(val => val === 'true').optional(),
    name: zod_1.z.string().optional(),
    tz: zod_1.z.string().optional(),
    page: zod_1.z.string().transform(val => parseInt(val)).default('1'),
    pageSize: zod_1.z.string().transform(val => Math.min(parseInt(val), 100)).default('20'),
});
exports.ScheduleQuerySchema = ScheduleQuerySchema;
const ScheduleResponseSchema = zod_1.z.object({
    id: zod_1.z.string(),
    tenantId: zod_1.z.string(),
    name: zod_1.z.string(),
    description: zod_1.z.string().nullable(),
    tz: zod_1.z.string(),
    trigger: TriggerSchema,
    target: TargetSchema,
    payload: zod_1.z.record(zod_1.z.string(), zod_1.z.any()).nullable(),
    calendar: CalendarConfigSchema.nullable(),
    enabled: zod_1.z.boolean(),
    nextFireAt: zod_1.z.string().datetime().nullable(),
    lastFireAt: zod_1.z.string().datetime().nullable(),
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    version: zod_1.z.number(),
});
exports.ScheduleResponseSchema = ScheduleResponseSchema;
const ScheduleListResponseSchema = zod_1.z.object({
    data: zod_1.z.array(ScheduleResponseSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number(),
    }),
});
exports.ScheduleListResponseSchema = ScheduleListResponseSchema;
const ManualTriggerInputSchema = zod_1.z.object({
    fireTime: zod_1.z.string().datetime().optional(),
    payload: zod_1.z.record(zod_1.z.string(), zod_1.z.any()).optional(),
});
exports.ManualTriggerInputSchema = ManualTriggerInputSchema;
const BackfillInputSchema = zod_1.z.object({
    from: zod_1.z.string().datetime(),
    to: zod_1.z.string().datetime(),
    step: zod_1.z.string().regex(/^P(\d+Y)?(\d+M)?(\d+D)?T?(\d+H)?(\d+M)?(\d+S)?$/, 'Invalid ISO 8601 duration'),
    maxRuns: zod_1.z.number().int().positive().max(1000).optional(),
});
exports.BackfillInputSchema = BackfillInputSchema;
//# sourceMappingURL=schedule-contracts.js.map