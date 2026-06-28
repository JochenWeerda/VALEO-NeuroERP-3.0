import type { ScreenWorkflowDefinition } from '../schema'

/** Platzhalter fuer Workflow-Panels aus screen.workflow (Wave 28). */
export function WorkflowPanelRenderer({ workflow }: { workflow?: ScreenWorkflowDefinition }): JSX.Element | null {
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
