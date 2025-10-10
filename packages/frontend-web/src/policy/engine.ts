/**
 * Policy-Engine für Alert-Actions
 * Entscheidet über Ausführung, Approval-Bedarf und Limits
 */

import policies from "./policies.json"

const MINUTES_PER_HOUR = 60
const ISO_DATE_LENGTH = 10

type Severity = "ok" | "warn" | "crit"
type Role = "admin" | "manager" | "operator"

type When = {
  kpiId: string
  severity: Severity[]
}

type Window = {
  days: number[]
  start: string
  end: string
}

type Approval = {
  required: boolean
  roles?: Role[]
  bypassIfSeverity?: Severity
}

type Rule = {
  id: string
  when: When
  action: "pricing.adjust" | "inventory.reorder" | "sales.notify"
  params?: Record<string, unknown>
  limits?: Record<string, number>
  window?: Window
  approval?: Approval
  autoExecute?: boolean
  autoSuggest?: boolean
}

export type Alert = {
  id: string
  kpiId?: string
  title: string
  message: string
  severity: Severity
  delta?: number
}

export type Decision =
  | { type: "deny"; reason: string }
  | {
      type: "allow"
      execute: boolean
      needsApproval: boolean
      approverRoles?: Role[]
      ruleId: string
      resolvedParams: Record<string, unknown>
    }

type Counter = {
  day: string
  dailyPct?: number
  dailyQty?: number
  weeklyPct?: number
}

// Einfache Tages/Wochen-Limits (Client-seitig; Server muss hart prüfen)
const counters: Record<string, Counter> = {}

/**
 * Prüft ob aktuelle Zeit im definierten Zeitfenster liegt
 */
function withinWindow(win: Window | undefined, now = new Date()): boolean {
  if (win === undefined) {
    return true
  }

  // Europe/Berlin: Client läuft in Berlin, daher lokale Uhrzeit ok
  const day = now.getDay() // 0=So..6=Sa
  if (!win.days.includes(day)) {
    return false
  }

  const startParts = win.start.split(":")
  const endParts = win.end.split(":")
  const startHour = Number(startParts[0])
  const startMin = Number(startParts[1])
  const endHour = Number(endParts[0])
  const endMin = Number(endParts[1])

  const currentMinutes = now.getHours() * MINUTES_PER_HOUR + now.getMinutes()
  const startMinutes = startHour * MINUTES_PER_HOUR + startMin
  const endMinutes = endHour * MINUTES_PER_HOUR + endMin

  return currentMinutes >= startMinutes && currentMinutes <= endMinutes
}

/**
 * Prüft ob Limits eingehalten werden
 */
function canPassLimits(rule: Rule, params: Record<string, unknown>): boolean {
  const today = new Date().toISOString().slice(0, ISO_DATE_LENGTH)
  const key = rule.id

  if (counters[key] === undefined) {
    counters[key] = { day: today, dailyPct: 0, dailyQty: 0, weeklyPct: 0 }
  }

  const counter = counters[key]
  if (counter === undefined) {
    return true
  }

  if (counter.day !== today) {
    counters[key] = {
      day: today,
      dailyPct: 0,
      dailyQty: 0,
      weeklyPct: counter.weeklyPct,
    }
  }

  const limits = rule.limits ?? {}

  if (typeof params.deltaPct === "number") {
    const nextPct = (counter.dailyPct ?? 0) + Math.abs(params.deltaPct)
    if (
      typeof limits.maxDailyPct === "number" &&
      nextPct > limits.maxDailyPct
    ) {
      return false
    }
  }

  if (typeof params.qty === "number") {
    const nextQty = (counter.dailyQty ?? 0) + params.qty
    if (typeof limits.maxDailyQty === "number" && nextQty > limits.maxDailyQty) {
      return false
    }
  }

  return true
}

/**
 * Löst Parameter-Templates auf (z.B. {delta})
 */
function resolveParams(
  rule: Rule,
  severity: Severity,
  alert: Alert | undefined
): Record<string, unknown> {
  const ruleParams = rule.params ?? {}
  const output: Record<string, unknown> = {}

  for (const [key, value] of Object.entries(ruleParams)) {
    if (
      value !== null &&
      typeof value === "object" &&
      "warn" in value &&
      "crit" in value
    ) {
      const severityMap = value as Record<string, unknown>
      output[key] = severityMap[severity] ?? severityMap.warn
    } else if (
      typeof value === "string" &&
      value.includes("{delta}") &&
      alert?.delta !== undefined
    ) {
      output[key] = value.replace("{delta}", String(alert.delta))
    } else {
      output[key] = value
    }
  }

  return output
}

/**
 * Entscheidet ob eine Action ausgeführt werden darf
 */
export function decide(userRoles: Role[], alert: Alert): Decision {
  const rules = policies.rules as Rule[]
  const rule = rules.find(
    (r) =>
      r.when.kpiId === alert.kpiId && r.when.severity.includes(alert.severity)
  )

  if (rule === undefined) {
    return { type: "deny", reason: "No matching rule" }
  }

  if (!withinWindow(rule.window)) {
    return { type: "deny", reason: "Outside window" }
  }

  const params = resolveParams(rule, alert.severity, alert)

  if (!canPassLimits(rule, params)) {
    return { type: "deny", reason: "Limit exceeded" }
  }

  const approval = rule.approval
  const needsApproval =
    approval?.required === true &&
    !(
      approval.bypassIfSeverity !== undefined &&
      alert.severity === approval.bypassIfSeverity
    )

  const approverRoles = approval?.roles

  const roleOk =
    !needsApproval ||
    userRoles.some((r) => approverRoles?.includes(r as Role) === true)

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

/**
 * Aktualisiert Counter nach erfolgreicher Ausführung
 */
export function updateCounters(ruleId: string, params: Record<string, unknown>): void {
  const counter = counters[ruleId]
  if (counter === undefined) {
    return
  }

  if (typeof params.deltaPct === "number") {
    counter.dailyPct = (counter.dailyPct ?? 0) + Math.abs(params.deltaPct)
    counter.weeklyPct = (counter.weeklyPct ?? 0) + Math.abs(params.deltaPct)
  }

  if (typeof params.qty === "number") {
    counter.dailyQty = (counter.dailyQty ?? 0) + params.qty
  }
}

