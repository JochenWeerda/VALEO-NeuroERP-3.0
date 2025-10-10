/**
 * Audit-Logging für Policy-Actions
 * Protokolliert alle Entscheidungen und Ausführungen
 */

export type AuditEntry = {
  ts: string
  user: string
  roles: string[]
  action: string
  params: Record<string, unknown>
  ruleId: string
  approval?: {
    by?: string
    at?: string
  }
  result: "executed" | "denied" | "requested-approval"
  reason?: string
}

/**
 * Sendet Audit-Entry an Backend
 */
export async function audit(entry: AuditEntry): Promise<void> {
  try {
    await fetch("/api/mcp/audit/log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(entry),
    })
  } catch {
    // Silent fail - Audit sollte nicht die Action blockieren
  }
}

