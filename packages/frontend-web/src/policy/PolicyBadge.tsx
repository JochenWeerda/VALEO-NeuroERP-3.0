import { type Alert, decide } from "./engine"
import { CompactDecisionCard } from "@/components/workflow/CompactDecisionCard"
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
    <CompactDecisionCard view={view} title="Policy" />
  )
}
