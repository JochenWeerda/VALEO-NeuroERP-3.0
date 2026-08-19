import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { RenderActionPlan } from '../render-plan/types'

function isDangerAction(action: RenderActionPlan): boolean {
  return action.kind === 'danger' || ['high', 'critical', 'destructive'].includes(action.dangerLevel ?? '')
}

function actionVariant(action: RenderActionPlan): 'default' | 'secondary' | 'outline' | 'destructive' {
  if (isDangerAction(action)) return 'destructive'
  if (action.zone === 'commit' || action.kind === 'primary') return 'default'
  if (action.kind === 'workflow') return 'secondary'
  return 'outline'
}

export function ActionFooterRenderer({
  actions,
  sticky,
  payload,
  onAction,
}: {
  actions: RenderActionPlan[]
  sticky: boolean
  payload: Record<string, unknown>
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
}): JSX.Element | null {
  if (actions.length === 0) return null
  const footer = actions.filter((action) => action.zone === 'footer')
  const commit = actions.filter((action) => action.zone === 'commit')

  const renderAction = (action: RenderActionPlan) => (
    <Button
      key={action.key}
      type="button"
      variant={actionVariant(action)}
      disabled={action.disabled}
      data-testid={`action-${action.key}`}
      data-action-kind={action.kind}
      data-action-zone={action.zone}
      data-danger-level={action.dangerLevel ?? 'safe'}
      data-requires-confirmation={action.requiresConfirmation ? 'true' : 'false'}
      title={action.keyboardShortcut ? `${action.label} (${action.keyboardShortcut})` : undefined}
      onClick={() => { void onAction?.(action.key, payload) }}
    >
      {action.label}
      {action.keyboardShortcut ? <span className="ml-2 text-xs opacity-70">{action.keyboardShortcut}</span> : null}
    </Button>
  )

  return (
    <div
      className={cn(
        'flex flex-wrap items-center justify-between gap-3 rounded-md border border-border bg-card px-4 py-3 shadow-sm',
        sticky && 'sticky bottom-0 z-20',
      )}
      role="toolbar"
      aria-label="Maskenaktionen"
      data-testid="meridian-footer-actions"
      data-sticky={sticky ? 'true' : 'false'}
    >
      {footer.length > 0 ? <div className="flex flex-wrap gap-2">{footer.map(renderAction)}</div> : <span />}
      {commit.length > 0 ? <div className="flex flex-wrap gap-2 border-l border-border pl-3">{commit.map(renderAction)}</div> : null}
    </div>
  )
}
