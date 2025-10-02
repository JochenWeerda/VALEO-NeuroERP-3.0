import { z } from 'zod';

export const CallOffStatusEnum = z.enum(['Planned', 'Scheduled', 'Delivered', 'Invoiced', 'Cancelled']);

export const CreateCallOffSchema = z.object({
  qty: z.number().positive(),
  window: z.object({
    from: z.string().datetime(),
    to: z.string().datetime(),
  }),
  site: z.string().optional(),
  silo: z.string().optional(),
  customerYard: z.string().optional(),
  notes: z.string().optional(),
}).openapi('CreateCallOff');

export const UpdateCallOffSchema = z.object({
  qty: z.number().positive().optional(),
  window: z.object({
    from: z.string().datetime(),
    to: z.string().datetime(),
  }).optional(),
  site: z.string().optional(),
  silo: z.string().optional(),
  customerYard: z.string().optional(),
  notes: z.string().optional(),
}).openapi('UpdateCallOff');

export const CallOffResponseSchema = z.object({
  id: z.string().uuid(),
  contractId: z.string().uuid(),
  tenantId: z.string(),
  qty: z.number(),
  window: z.object({
    from: z.string().datetime(),
    to: z.string().datetime(),
  }),
  site: z.string().optional(),
  silo: z.string().optional(),
  customerYard: z.string().optional(),
  status: CallOffStatusEnum,
  notes: z.string().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  version: z.number(),
}).openapi('CallOff');

export const MarkDeliveredSchema = z.object({
  actualQty: z.number().positive().optional(),
  notes: z.string().optional(),
}).openapi('MarkDelivered');

export type CreateCallOff = z.infer<typeof CreateCallOffSchema>;
export type UpdateCallOff = z.infer<typeof UpdateCallOffSchema>;
export type CallOffResponse = z.infer<typeof CallOffResponseSchema>;
export type MarkDelivered = z.infer<typeof MarkDeliveredSchema>;