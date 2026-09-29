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
  condensed = false,
  identity,
}: {
  domain: string
  mode: string
  title: string
  subtitle?: string
  /** Name of the concrete document (e.g. invoice number); becomes the h1, `title` the kicker above it. */
  identity?: string
  actions: ScreenActionDefinition[]
  floorplan?: string
  density?: string
  contextRail?: string
  headerClassName: string
  touchTargetClass: string
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
  payload: Record<string, unknown>
  /** One-line header while the page is scrolled; identity and actions stay reachable. */
  condensed?: boolean
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
        data-action-zone={action.zone ?? 'header'}
        data-testid={`action-${action.key}`}
        title={action.keyboardShortcut ? `${action.label} (${action.keyboardShortcut})` : undefined}
        onClick={() => { void onAction?.(action.key, payload) }}
      >
        {action.label}
      </Button>
    )
  }

  return (
    <div
      className={cn(headerClassName, condensed && 'py-2 md:flex-row md:items-center')}
      data-floorplan={floorplan}
      data-mode={mode}
      data-domain={domain}
      data-density={density}
      data-context-rail={contextRail}
      data-condensed={condensed ? 'true' : 'false'}
    >
      <div className={cn('min-w-0', identity && condensed && 'flex items-baseline gap-2')}>
        {identity ? (
          <p className="text-2xs font-medium uppercase tracking-wide text-muted-foreground" data-testid="mask-kicker">
            {title}
          </p>
        ) : null}
        <h1 className={cn('font-bold tracking-normal text-foreground', condensed ? 'truncate text-base' : 'text-xl')}>
          {identity ?? title}
        </h1>
        {subtitle && !condensed && <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>}
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
