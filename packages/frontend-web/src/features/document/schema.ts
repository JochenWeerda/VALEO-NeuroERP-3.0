import { z } from "zod"

export const DocSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  type: z.string().min(1),
  sizeKB: z.number().nonnegative(),
  ts: z.string().min(1)
})

export type Doc = z.infer<typeof DocSchema>
