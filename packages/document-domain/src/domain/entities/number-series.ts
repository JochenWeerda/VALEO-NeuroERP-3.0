import { z } from 'zod';

export const NumberSeriesSchema = z.object({
  id: z.string().uuid().optional(),
  tenantId: z.string().min(1),
  scope: z.string().min(1), // "invoice", "delivery_note", "weighing_ticket"
  pattern: z.string().min(1), // "INV-{YYYY}-{seq5}"
  nextSeq: z.number().int().default(1),
  resetPolicy: z.enum(['Yearly', 'Never']).default('Yearly'),
  lastResetAt: z.string().datetime().optional(),
  createdAt: z.string().datetime().optional(),
});

export type NumberSeries = z.infer<typeof NumberSeriesSchema>;

export const CreateNumberSeriesSchema = NumberSeriesSchema.omit({ id: true, createdAt: true });
export type CreateNumberSeries = z.infer<typeof CreateNumberSeriesSchema>;
