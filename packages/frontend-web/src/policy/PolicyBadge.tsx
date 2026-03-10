import { type Alert, decide } from "./engine"
import { buildDecisionView } from "./decision-view"

type Role = "admin" | "manager" | "operator"

type Props = {
  alert: Alert
  roles: Role[]
}

export function PolicyBadge({ alert, roles }: Props): JSX.Element {
  const decision = decide(roles, alert)
  const view = buildDecisionView(decision)

  if (view === null) {
    return (
      <div className="rounded-md border border-muted px-2 py-1.5 text-xs text-muted-foreground">
        Policy-Entscheidung konnte nicht dargestellt werden.
      </div>
    )
  }

  return (
    <div className={`rounded-md border px-2 py-1.5 ${view.statusClassName}`}>
      <div className="text-xs font-semibold">Policy: {view.statusLabel}</div>
      <div className="text-xs opacity-90">{view.summary}</div>
      <ul className="mt-1 list-disc pl-4 text-[11px] opacity-90">
        {view.details.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
    </div>
  )
}
