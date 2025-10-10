/**
 * Form Validator
 * Baut Zod-Schema aus FormSchema und validiert Werte
 */

import { z } from "zod"
import type { FormSchema } from "./FormBuilder"

/**
 * Baut Zod-Schema aus FormSchema
 */
export function buildZodFromSchema(schema: FormSchema): z.ZodObject<z.ZodRawShape> {
  const shape: Record<string, z.ZodTypeAny> = {}

  for (const f of schema.fields) {
    let t: z.ZodTypeAny = z.any()

    // Type-Mapping
    if (
      f.type === "string" ||
      f.type === "text" ||
      f.type === "select" ||
      f.type === "lookup"
    ) {
      t = z.string()
    }
    if (f.type === "number") {
      t = z.number()
      if (f.min !== undefined) {
        t = t.min(f.min)
      }
      if (f.max !== undefined) {
        t = t.max(f.max)
      }
    }
    if (f.type === "date") {
      t = z.string().regex(/^\d{4}-\d{2}-\d{2}$/)
    }

    // Required/Optional
    t = f.required === true ? t : t.optional()

    shape[f.name] = t
  }

  // Lines (Positionen)
  if (schema.lines !== undefined) {
    const lineShape: Record<string, z.ZodTypeAny> = {}
    for (const c of schema.lines.columns) {
      let ct: z.ZodTypeAny = c.type === "number" ? z.number() : z.string()
      ct = c.required === true ? ct : ct.optional()
      lineShape[c.name] = ct
    }
    shape[schema.lines.name] = z.array(z.object(lineShape)).optional()
  }

  return z.object(shape)
}

/**
 * Validiert Werte gegen Zod-Schema
 */
export function validateValues(
  schema: z.ZodObject<z.ZodRawShape>,
  values: Record<string, unknown>
): {
  ok: boolean
  errs: Record<string, string>
  parsed: unknown
} {
  const res = schema.safeParse(values)

  if (!res.success) {
    const errs: Record<string, string> = {}
    for (const issue of res.error.issues) {
      const path = issue.path.join(".")
      errs[path] = issue.message
    }
    return { ok: false, errs, parsed: null }
  }

  return { ok: true, errs: {}, parsed: res.data }
}

