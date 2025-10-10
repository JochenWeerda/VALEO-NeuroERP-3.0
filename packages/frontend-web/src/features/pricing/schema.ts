import { z } from "zod"

export const PriceTierSchema = z.object({
  minQty: z.number().nonnegative(),
  net: z.number().nonnegative(),
})

export const PriceItemSchema = z.object({
  sku: z.string().min(1),
  name: z.string().min(1),
  currency: z.string().min(1),
  unit: z.string().min(1),
  baseNet: z.number().nonnegative(),
  tiers: z.array(PriceTierSchema).default([]),
})

export type PriceTier = z.infer<typeof PriceTierSchema>
export type PriceItem = z.infer<typeof PriceItemSchema>
