import { z } from "zod"

// Severity Schema
export const SeveritySchema = z.enum(["ok", "warn", "crit"])

// Role Schema
export const RoleSchema = z.enum(["admin", "manager", "operator"])

// When Condition Schema
const WhenSchema = z.object({
  kpiId: z.string().min(1),
  severity: z.array(SeveritySchema),
})

const MAX_WEEKDAY = 6

// Window Schema
const WindowSchema = z.object({
  days: z.array(z.number().min(0).max(MAX_WEEKDAY)),
  start: z.string().regex(/^\d{2}:\d{2}$/),
  end: z.string().regex(/^\d{2}:\d{2}$/),
})

// Approval Schema
const ApprovalSchema = z.object({
  required: z.boolean(),
  roles: z.array(RoleSchema).optional(),
  bypassIfSeverity: SeveritySchema.optional(),
})

// Rule Schema
export const RuleSchema = z.object({
  id: z.string().min(1),
  when: WhenSchema,
  action: z.enum(["pricing.adjust", "inventory.reorder", "sales.notify"]),
  params: z.record(z.unknown()).optional(),
  limits: z.record(z.number()).optional(),
  window: WindowSchema.optional(),
  approval: ApprovalSchema.optional(),
  autoExecute: z.boolean().optional(),
  autoSuggest: z.boolean().optional(),
})

export type Rule = z.infer<typeof RuleSchema>

// Alert Input Schema (für Simulator)
export const AlertInputSchema = z.object({
  id: z.string(),
  kpiId: z.string().optional(),
  title: z.string(),
  message: z.string(),
  severity: SeveritySchema,
  delta: z.number().optional(),
})

export type AlertInput = z.infer<typeof AlertInputSchema>

