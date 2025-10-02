"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BusinessDaysSchema = exports.CalendarListResponseSchema = exports.CalendarResponseSchema = exports.CalendarQuerySchema = exports.UpdateCalendarInputSchema = exports.CreateCalendarInputSchema = void 0;
const zod_1 = require("zod");
const BusinessDaysSchema = zod_1.z.object({
    mon: zod_1.z.boolean().default(true),
    tue: zod_1.z.boolean().default(true),
    wed: zod_1.z.boolean().default(true),
    thu: zod_1.z.boolean().default(true),
    fri: zod_1.z.boolean().default(true),
    sat: zod_1.z.boolean().default(false),
    sun: zod_1.z.boolean().default(false),
});
exports.BusinessDaysSchema = BusinessDaysSchema;
const CreateCalendarInputSchema = zod_1.z.object({
    key: zod_1.z.string().min(1, 'Calendar key is required'),
    name: zod_1.z.string().min(1, 'Calendar name is required'),
    holidays: zod_1.z.array(zod_1.z.string().datetime()).default([]),
    businessDays: BusinessDaysSchema.default({}),
});
exports.CreateCalendarInputSchema = CreateCalendarInputSchema;
const UpdateCalendarInputSchema = zod_1.z.object({
    name: zod_1.z.string().min(1).optional(),
    holidays: zod_1.z.array(zod_1.z.string().datetime()).optional(),
    businessDays: BusinessDaysSchema.optional(),
});
exports.UpdateCalendarInputSchema = UpdateCalendarInputSchema;
const CalendarQuerySchema = zod_1.z.object({
    key: zod_1.z.string().optional(),
    name: zod_1.z.string().optional(),
    page: zod_1.z.string().transform(val => parseInt(val)).default('1'),
    pageSize: zod_1.z.string().transform(val => Math.min(parseInt(val), 100)).default('20'),
});
exports.CalendarQuerySchema = CalendarQuerySchema;
const CalendarResponseSchema = zod_1.z.object({
    id: zod_1.z.string(),
    tenantId: zod_1.z.string().nullable(),
    key: zod_1.z.string(),
    name: zod_1.z.string(),
    holidays: zod_1.z.array(zod_1.z.string().datetime()),
    businessDays: BusinessDaysSchema,
    createdAt: zod_1.z.string().datetime(),
    updatedAt: zod_1.z.string().datetime(),
    version: zod_1.z.number(),
});
exports.CalendarResponseSchema = CalendarResponseSchema;
const CalendarListResponseSchema = zod_1.z.object({
    data: zod_1.z.array(CalendarResponseSchema),
    pagination: zod_1.z.object({
        page: zod_1.z.number(),
        pageSize: zod_1.z.number(),
        total: zod_1.z.number(),
        totalPages: zod_1.z.number(),
    }),
});
exports.CalendarListResponseSchema = CalendarListResponseSchema;
//# sourceMappingURL=calendar-contracts.js.map