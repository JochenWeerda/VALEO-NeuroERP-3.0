import { z } from 'zod';
import { extendZodWithOpenApi } from 'zod-openapi';

extendZodWithOpenApi(z);

export const AmendmentTypeEnum = z.enum(['QtyChange', 'WindowChange', 'PriceRuleChange', 'CounterpartyChange', 'DeliveryTermsChange', 'Other']);
export const AmendmentStatusEnum = z.enum(['Pending', 'Approved', 'Rejected', 'Cancelled']);

export const CreateAmendmentSchema = z.object({
  type: AmendmentTypeEnum,
  reason: z.string(),
  changes: z.record(z.any()),
  notes: z.string().optional(),
});

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
});

export const ApproveAmendmentSchema = z.object({
  notes: z.string().optional(),
});

export const RejectAmendmentSchema = z.object({
  reason: z.string(),
  notes: z.string().optional(),
});

export type CreateAmendment = z.infer<typeof CreateAmendmentSchema>;
export type AmendmentResponse = z.infer<typeof AmendmentResponseSchema>;
export type ApproveAmendment = z.infer<typeof ApproveAmendmentSchema>;
export type RejectAmendment = z.infer<typeof RejectAmendmentSchema>;