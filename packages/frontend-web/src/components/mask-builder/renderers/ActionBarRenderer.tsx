import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { ScreenActionDefinition } from '../schema'

function isDangerAction(action: Pick<ScreenActionDefinition, 'kind' | 'dangerLevel'>): boolean {
  return action.kind === 'danger' || action.dangerLevel === 'high' || action.dangerLevel === 'critical' || action.dangerLevel === 'destructive'
}

export function ActionBarRenderer({
  domain,
  mode,
  title,
  subtitle,
  actions,
  floorplan,
  density,
  contextRail,
  headerClassName,
  touchTargetClass,
  onAction,
  payload,
}: {
  domain: string
  mode: string
  title: string
  subtitle?: string
  actions: ScreenActionDefinition[]
  floorplan?: string
  density?: string
  contextRail?: string
  headerClassName: string
  touchTargetClass: string
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
  payload: Record<string, unknown>
}): JSX.Element {
  const primaryActions = actions.filter((action) => action.kind === 'primary').slice(0, 1)
  const primaryKeys = new Set(primaryActions.map((action) => action.key))
  const secondaryActions = actions.filter((action) => !primaryKeys.has(action.key) && !isDangerAction(action))
  const dangerActions = actions.filter((action) => !primaryKeys.has(action.key) && isDangerAction(action))

  function renderAction(action: ScreenActionDefinition) {
    const danger = isDangerAction(action)
    const variant = action.kind === 'primary' && !danger ? 'default' : danger ? 'destructive' : action.kind === 'workflow' ? 'secondary' : 'outline'
    return (
      <Button
        key={action.key}
        className={cn(touchTargetClass)}
        variant={variant}
        disabled={action.disabled}
        data-action-kind={action.kind ?? 'secondary'}
        data-danger-level={action.dangerLevel ?? 'safe'}
        data-requires-confirmation={action.requiresConfirmation ? 'true' : 'false'}
        onClick={() => { void onAction?.(action.key, payload) }}
      >
        {action.label}
      </Button>
    )
  }

  return (
    <div className={headerClassName} data-floorplan={floorplan} data-density={density} data-context-rail={contextRail}>
      <div>
        <p className="text-xs font-medium uppercase tracking-normal text-muted-foreground">
          {domain} / {floorplan ?? mode}
        </p>
        <h1 className="text-xl font-bold tracking-normal text-foreground">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      <div className="flex flex-wrap items-center justify-end gap-2" data-testid="meridian-action-bar">
        {primaryActions.map(renderAction)}
        {secondaryActions.map(renderAction)}
        {dangerActions.length > 0 && (
          <div className="ml-1 flex flex-wrap gap-2 border-l border-border pl-2" data-testid="meridian-danger-actions">
            {dangerActions.map(renderAction)}
          </div>
        )}
      </div>
    </div>
  )
}
