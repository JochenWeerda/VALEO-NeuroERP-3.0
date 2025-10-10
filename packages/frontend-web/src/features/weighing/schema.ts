import { z } from "zod"

export const TicketSchema = z.object({
  id: z.string().min(1),
  vehicle: z.string().min(1),
  gross: z.number().nonnegative(),
  tare: z.number().nonnegative(),
  net: z.number().nonnegative(),
  material: z.string().min(1),
  ts: z.string().min(1)
})
export type Ticket = z.infer<typeof TicketSchema>
