import { z } from 'zod';

// Base schemas
const BusinessDaysSchema = z.object({
  mon: z.boolean().default(true),
  tue: z.boolean().default(true),
  wed: z.boolean().default(true),
  thu: z.boolean().default(true),
  fri: z.boolean().default(true),
  sat: z.boolean().default(false),
  sun: z.boolean().default(false),
});

// Input schemas
const CreateCalendarInputSchema = z.object({
  key: z.string().min(1, 'Calendar key is required'),
  name: z.string().min(1, 'Calendar name is required'),
  holidays: z.array(z.string().datetime()).default([]),
  businessDays: BusinessDaysSchema.default({}),
});

const UpdateCalendarInputSchema = z.object({
  name: z.string().min(1).optional(),
  holidays: z.array(z.string().datetime()).optional(),
  businessDays: BusinessDaysSchema.optional(),
});

const CalendarQuerySchema = z.object({
  key: z.string().optional(),
  name: z.string().optional(),
  page: z.string().transform(val => parseInt(val)).default('1'),
  pageSize: z.string().transform(val => Math.min(parseInt(val), 100)).default('20'),
});

// Response schemas
const CalendarResponseSchema = z.object({
  id: z.string(),
  tenantId: z.string().nullable(),
  key: z.string(),
  name: z.string(),
  holidays: z.array(z.string().datetime()),
  businessDays: BusinessDaysSchema,
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  version: z.number(),
});

const CalendarListResponseSchema = z.object({
  data: z.array(CalendarResponseSchema),
  pagination: z.object({
    page: z.number(),
    pageSize: z.number(),
    total: z.number(),
    totalPages: z.number(),
  }),
});

// Exports
export {
  CreateCalendarInputSchema,
  UpdateCalendarInputSchema,
  CalendarQuerySchema,
  CalendarResponseSchema,
  CalendarListResponseSchema,
  BusinessDaysSchema,
};