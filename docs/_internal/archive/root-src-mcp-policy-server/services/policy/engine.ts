import { z } from "zod"
import type { Rule } from "./store-sqlite"

const MINUTES_PER_HOUR = 60

export const SeverityEnum = z.enum(["ok", "warn", "crit"])
export const RoleEnum = z.enum(["admin", "manager", "operator"])

export const AlertSchema = z.object({
  id: z.string().min(1),
  kpiId: z.string().min(1),
  title: z.string().min(1),
  message: z.string().min(1),
  severity: SeverityEnum,
  delta: z.number().optional(),
})
export type Alert = z.infer<typeof AlertSchema>

export type Decision =
  | { type: "deny"; reason: string }
  | {
      type: "allow"
      execute: boolean
      needsApproval: boolean
      approverRoles?: string[]
      ruleId: string
      resolvedParams: Record<string, unknown>
    }

/**
 * Prüft ob die aktuelle Zeit innerhalb des definierten Zeitfensters liegt
 */
function withinWindow(
  win?: { days: number[]; start: string; end: string },
  now = new Date()
): boolean {
  if (win === undefined) {
    return true
  }
  const day = now.getDay() // 0..6 (0=Sunday)
  if (!win.days.includes(day)) {
    return false
  }
  const [sh, sm] = win.start.split(":").map(Number)
  const [eh, em] = win.end.split(":").map(Number)
  const t = now.getHours() * MINUTES_PER_HOUR + now.getMinutes()
  const s = sh * MINUTES_PER_HOUR + sm
  const e = eh * MINUTES_PER_HOUR + em
  return t >= s && t <= e
}

/**
 * Löst Parameter-Platzhalter auf (severity-abhängig oder mit delta)
 */
function resolveParams(
  rule: Rule,
  sev: "ok" | "warn" | "crit",
  alert?: Alert
): Record<string, unknown> {
  const p = rule.params ?? {}
  const out: Record<string, unknown> = {}
  for (const [k, v] of Object.entries(p)) {
    if (
      v !== null &&
      typeof v === "object" &&
      "warn" in v &&
      "crit" in v
    ) {
      const obj = v as { warn?: unknown; crit?: unknown }
      out[k] = obj[sev] ?? obj.warn
    } else if (
      typeof v === "string" &&
      alert?.delta !== undefined &&
      v.includes("{delta}")
    ) {
      out[k] = v.replace("{delta}", String(alert.delta))
    } else {
      out[k] = v
    }
  }
  return out
}

/**
 * Policy-Entscheidungs-Engine
 * Matched Alert gegen Regeln und gibt Entscheidung zurück
 */
export function decide(userRoles: string[], alert: Alert, rules: Rule[]): Decision {
  const rule = rules.find(
    (r) => r.when.kpiId === alert.kpiId && r.when.severity.includes(alert.severity)
  )
  if (rule === undefined) {
    return { type: "deny", reason: "No matching rule" }
  }
  if (!withinWindow(rule.window)) {
    return { type: "deny", reason: "Outside window" }
  }

  const params = resolveParams(rule, alert.severity, alert)

  const appr = rule.approval
  const needsApproval =
    appr?.required === true &&
    !(appr.bypassIfSeverity !== undefined && alert.severity === appr.bypassIfSeverity)

  const approverRoles = appr?.roles

  const roleOk =
    !needsApproval || userRoles.some((r) => approverRoles?.includes(r as "admin" | "manager" | "operator"))

  const execute = rule.autoExecute === true && (!needsApproval || roleOk)

  return {
    type: "allow",
    execute,
    needsApproval,
    approverRoles,
    ruleId: rule.id,
    resolvedParams: params,
  }
}

