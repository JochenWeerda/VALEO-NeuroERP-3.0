import { z } from 'zod';

export const AmendmentTypeEnum = z.enum(['QtyChange', 'WindowChange', 'PriceRuleChange', 'CounterpartyChange', 'DeliveryTermsChange', 'Other']);
export const AmendmentStatusEnum = z.enum(['Pending', 'Approved', 'Rejected', 'Cancelled']);

export const CreateAmendmentSchema = z.object({
  type: AmendmentTypeEnum,
  reason: z.string(),
  changes: z.record(z.any()),
  notes: z.string().optional(),
}).openapi('CreateAmendment');

export const AmendmentResponseSchema = z.object({
  id: z.string().uuid(),
  contractId: z.string().uuid(),
  tenantId: z.string(),
  type: AmendmentTypeEnum,
  reason: z.string(),
  changes: z.record(z.any()),
  approvedBy: z.string().optional(),
  approvedAt: z.string().datetime().optional(),
  status: AmendmentStatusEnum,
  effectiveAt: z.string().datetime().optional(),
  notes: z.string().optional(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
  version: z.number(),
}).openapi('Amendment');

export const ApproveAmendmentSchema = z.object({
  notes: z.string().optional(),
}).openapi('ApproveAmendment');

export const RejectAmendmentSchema = z.object({
  reason: z.string(),
  notes: z.string().optional(),
}).openapi('RejectAmendment');

export type CreateAmendment = z.infer<typeof CreateAmendmentSchema>;
export type AmendmentResponse = z.infer<typeof AmendmentResponseSchema>;
export type ApproveAmendment = z.infer<typeof ApproveAmendmentSchema>;
export type RejectAmendment = z.infer<typeof RejectAmendmentSchema>;