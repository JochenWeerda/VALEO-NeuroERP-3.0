type PolicyDecisionDeny = {
  type: "deny"
  reason: string
}

type PolicyDecisionAllow = {
  type: "allow"
  execute?: boolean
  needsApproval?: boolean
  approverRoles?: string[]
  ruleId?: string
}

export type DecisionView = {
  statusLabel: string
  statusClassName: string
  summary: string
  details: string[]
  requiresApproval?: boolean
  context?: {
    pageDomain?: string
  }
}

const denyReasonLabel: Record<string, string> = {
  "No matching rule": "Keine passende Policy-Regel",
  "Outside window": "Außerhalb des erlaubten Zeitfensters",
  "Limit exceeded": "Policy-Limit überschritten",
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object"
}

function isPolicyDecisionDeny(value: unknown): value is PolicyDecisionDeny {
  return isRecord(value) && value.type === "deny" && typeof value.reason === "string"
}

function isPolicyDecisionAllow(value: unknown): value is PolicyDecisionAllow {
  return isRecord(value) && value.type === "allow"
}

export function buildDecisionView(decision: unknown): DecisionView | null {
  if (isPolicyDecisionDeny(decision)) {
    const readableReason = denyReasonLabel[decision.reason] ?? decision.reason
    return {
      statusLabel: "Blockiert",
      statusClassName: "bg-red-50 text-red-800 border-red-300",
      summary: "Aktion durch Policy blockiert.",
      details: [`Grund: ${readableReason}`],
      requiresApproval: false,
    }
  }

  if (!isPolicyDecisionAllow(decision)) {
    return null
  }

  const detailLines: string[] = []
  if (typeof decision.ruleId === "string" && decision.ruleId.length > 0) {
    detailLines.push(`Regel: ${decision.ruleId}`)
  }

  if (decision.needsApproval === true) {
    const roles =
      Array.isArray(decision.approverRoles) && decision.approverRoles.length > 0
        ? decision.approverRoles.join(", ")
        : "nicht spezifiziert"
    detailLines.push(`Freigabe erforderlich: ${roles}`)
  } else {
    detailLines.push("Keine zusätzliche Freigabe erforderlich")
  }

  if (decision.execute === true) {
    return {
      statusLabel: "Freigegeben (Auto-Execute)",
      statusClassName: "bg-emerald-50 text-emerald-800 border-emerald-300",
      summary: "Aktion wird automatisch ausgeführt.",
      details: detailLines,
      requiresApproval: decision.needsApproval === true,
    }
  }

  return {
    statusLabel: "Freigegeben",
    statusClassName: "bg-blue-50 text-blue-800 border-blue-300",
    summary:
      decision.needsApproval === true
        ? "Aktion ist zulässig, wartet aber auf Freigabe."
        : "Aktion ist zulässig.",
    details: detailLines,
    requiresApproval: decision.needsApproval === true,
  }
}
