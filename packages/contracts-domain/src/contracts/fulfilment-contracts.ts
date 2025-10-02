import { z } from 'zod';
import { extendZodWithOpenApi } from 'zod-openapi';

extendZodWithOpenApi(z);

export const FulfilmentResponseSchema = z.object({
  contractId: z.string().uuid(),
  tenantId: z.string(),
  deliveredQty: z.number(),
  pricedQty: z.number(),
  invoicedQty: z.number(),
  openQty: z.number(),
  avgPrice: z.number().optional(),
  timeline: z.array(z.object({
    event: z.string(),
    timestamp: z.string().datetime(),
    qty: z.number().optional(),
    price: z.number().optional(),
    notes: z.string().optional(),
  })),
  lastUpdated: z.string().datetime(),
});

export const PricingFixingSchema = z.object({
  kind: z.enum(['BASIS', 'FUTURES', 'MIN_PRICE_DECISION']),
  value: z.number(),
  futuresMonth: z.string().optional(),
  notes: z.string().optional(),
});

export type FulfilmentResponse = z.infer<typeof FulfilmentResponseSchema>;
export type PricingFixing = z.infer<typeof PricingFixingSchema>;