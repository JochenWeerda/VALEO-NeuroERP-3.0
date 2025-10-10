import { z } from "zod"

export const StockSchema = z.object({
  sku: z.string().min(1),
  name: z.string().min(1),
  qty: z.number().nonnegative(),
  uom: z.string().min(1),
  location: z.string().optional()
})
export type Stock = z.infer<typeof StockSchema>

export const AdjustSchema = z.object({
  sku: z.string().min(1),
  delta: z.number().refine(v => v !== 0, { message: "Delta darf nicht 0 sein" }),
  reason: z.enum(["counting", "damage", "shrinkage", "other"])
})
export type AdjustInput = z.infer<typeof AdjustSchema>

export const PutawaySchema = z.object({
  sku: z.string().min(1),
  qty: z.number().positive(),
  fromLocation: z.string().min(1),
  toLocation: z.string().min(1)
})
export type PutawayInput = z.infer<typeof PutawaySchema>
