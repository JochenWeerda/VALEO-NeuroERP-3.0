import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { ScreenActionDefinition } from '../schema'

export function ActionBarRenderer({
  domain,
  mode,
  title,
  subtitle,
  actions,
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
  headerClassName: string
  touchTargetClass: string
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
  payload: Record<string, unknown>
}): JSX.Element {
  return (
    <div className={headerClassName}>
      <div>
        <p className="text-xs font-medium uppercase tracking-normal text-muted-foreground">
          {domain} / {mode}
        </p>
        <h1 className="text-xl font-bold tracking-normal text-foreground">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      <div className="flex flex-wrap gap-2">
        {actions.map((action) => (
          <Button
            key={action.key}
            className={cn(touchTargetClass)}
            variant={action.kind === 'primary' ? 'default' : action.kind === 'danger' ? 'destructive' : 'outline'}
            disabled={action.disabled}
            onClick={() => { void onAction?.(action.key, payload) }}
          >
            {action.label}
          </Button>
        ))}
      </div>
    </div>
  )
}
