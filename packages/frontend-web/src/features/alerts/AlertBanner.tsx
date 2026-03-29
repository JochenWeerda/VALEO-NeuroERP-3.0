import type { Alert } from "./rules"
import { AlertActions } from "./AlertActions"
import { PolicyBadge } from "@/policy/PolicyBadge"
import { useAuth } from "@/hooks/useAuth"

type AlertBannerProps = {
  items: Alert[]
}

type AlertListProps = {
  items: Alert[]
}

/**
 * Alert-Banner Komponente
 * Zeigt den wichtigsten Alert prominent an
 */
export function AlertBanner({ items }: AlertBannerProps): JSX.Element | null {
  if (items.length === 0) {
    return null
  }

  const topAlert = items[0]
  if (topAlert === undefined) {
    return null
  }

  const bgClass =
    topAlert.severity === "crit"
      ? "bg-red-50 border-red-300 text-red-800"
      : topAlert.severity === "warn"
        ? "bg-amber-50 border-amber-300 text-amber-800"
        : "bg-emerald-50 border-emerald-300 text-emerald-800"

  return (
    <div
      className={`animate-in fade-in-0 border rounded-xl p-3 duration-200 ${bgClass}`}
    >
      <div className="font-semibold">{topAlert.title}</div>
      <div className="text-sm">{topAlert.message}</div>
    </div>
  )
}

/**
 * Alert-Liste Komponente mit Action-Buttons und Policy-Badges
 * Zeigt alle Alerts als Liste mit Workflow-Buttons an
 */
export function AlertList({ items }: AlertListProps): JSX.Element {
  const { hasRole } = useAuth()
  const userRoles: Array<"admin" | "manager" | "operator"> = [
    ...(hasRole("admin") ? ["admin" as const] : []),
    ...(hasRole("manager") ? ["manager" as const] : []),
    ...(hasRole("operator") ? ["operator" as const] : []),
  ]

  if (items.length === 0) {
    return <p className="text-sm opacity-70">Keine aktiven Alerts.</p>
  }

  return (
    <ul className="space-y-3">
      {items.map((alert): JSX.Element => {
        const severityClass =
          alert.severity === "crit"
            ? "text-red-700 font-medium"
            : alert.severity === "warn"
              ? "text-amber-700 font-medium"
              : "text-emerald-700 font-medium"

        return (
          <li key={alert.id} className="text-sm border rounded-lg p-3">
            <div className="mb-2">
              <span className={severityClass}>
                [{alert.severity.toUpperCase()}]
              </span>{" "}
              <span className="font-medium">{alert.title}</span> — {alert.message}
            </div>
            <div className="mb-2">
              <PolicyBadge alert={alert} roles={userRoles} />
            </div>
            <AlertActions alert={alert} />
          </li>
        )
      })}
    </ul>
  )
}
