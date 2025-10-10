import * as React from "react"
import { type Alert, decide } from "./engine"

type Role = "admin" | "manager" | "operator"

type Props = {
  alert: Alert
  roles: Role[]
}

/**
 * Policy-Badge Komponente
 * Zeigt den Policy-Status für einen Alert an
 */
export function PolicyBadge({ alert, roles }: Props): JSX.Element {
  const decision = decide(roles, alert)

  if (decision.type === "deny") {
    return (
      <span className="text-xs text-amber-700">
        Policy: {decision.reason}
      </span>
    )
  }

  if (decision.needsApproval && !decision.execute) {
    return (
      <span className="text-xs text-blue-700">Policy: Freigabe nötig</span>
    )
  }

  if (decision.execute) {
    return (
      <span className="text-xs text-emerald-700">Policy: Auto-Execute</span>
    )
  }

  return <span className="text-xs text-gray-600">Policy: erlaubt</span>
}
