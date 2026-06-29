import type { ScreenWorkflowDefinition } from '../schema'
import type { WorkflowState } from '../runtime/WorkflowRuntime'

const TONE_CLASSES: Record<string, string> = {
  neutral: 'border-border bg-muted/20 text-muted-foreground',
  success: 'border-green-500/40 bg-green-50 text-green-800',
  warning: 'border-yellow-500/40 bg-yellow-50 text-yellow-800',
  danger: 'border-destructive/40 bg-red-50 text-red-800',
  info: 'border-blue-500/40 bg-blue-50 text-blue-800',
}

export function WorkflowPanelRenderer({
  workflow,
  workflowState,
}: {
  workflow?: ScreenWorkflowDefinition
  workflowState?: WorkflowState
}): JSX.Element | null {
  // Rich workflow state (Phase 027)
  if (workflowState && workflowState.status.currentStatus !== 'unknown') {
    const { status, nextAllowedActions, blockingReasons, policyHints } = workflowState
    const toneClass = TONE_CLASSES[status.tone] ?? TONE_CLASSES['neutral']
    return (
      <div
        className={`rounded-md border p-4 ${toneClass}`}
        data-testid="workflow-panel"
        data-status={status.currentStatus}
        data-blocked={workflowState.isBlocked}
      >
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">{status.statusLabel}</span>
          {workflowState.isTerminal && (
            <span className="text-xs opacity-70">Abgeschlossen</span>
          )}
        </div>

        {blockingReasons.filter((r) => r.blocking).length > 0 && (
          <ul className="mt-2 space-y-1" aria-label="Blockierende Gründe">
            {blockingReasons.filter((r) => r.blocking).map((r) => (
              <li key={r.code} className="text-xs text-destructive" data-block-code={r.code}>
                ⚠ {r.message}
              </li>
            ))}
          </ul>
        )}

        {nextAllowedActions.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1" aria-label="Nächste Aktionen">
            {nextAllowedActions.map((a) => (
              <span
                key={a.actionKey}
                className="rounded bg-background/60 px-2 py-0.5 text-xs"
                data-next-action={a.actionKey}
              >
                {a.label}
              </span>
            ))}
          </div>
        )}

        {policyHints.filter((h) => h.severity !== 'info').length > 0 && (
          <ul className="mt-2 space-y-1" aria-label="Hinweise">
            {policyHints.filter((h) => h.severity !== 'info').map((h) => (
              <li key={h.ruleId} className="text-xs opacity-80">
                {h.message}
              </li>
            ))}
          </ul>
        )}
      </div>
    )
  }

  // Legacy fallback (ScreenWorkflowDefinition)
  if (!workflow?.processKey) return null
  return (
    <div
      className="rounded-md border border-dashed border-border bg-muted/20 p-4 text-sm text-muted-foreground"
      data-testid="workflow-panel-placeholder"
    >
      Workflow: {workflow.processKey}
      {workflow.status ? ` — Status: ${workflow.status}` : ''}
    </div>
  )
}
