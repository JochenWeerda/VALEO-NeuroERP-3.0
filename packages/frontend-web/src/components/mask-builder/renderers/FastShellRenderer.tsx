import { memo } from 'react'
import { ActionBarRenderer } from './ActionBarRenderer'
import { layoutClasses } from './render-utils'
import type { RenderPlan } from '../render-plan/types'

export const FastShellRenderer = memo(function FastShellRenderer({
  plan,
  onAction,
  payload,
}: {
  plan: RenderPlan
  payload: Record<string, unknown>
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
}): JSX.Element {
  const classes = layoutClasses(plan.shell.layoutMode)

  return (
    <div
      className={classes.root}
      data-screen-definition={plan.screenId}
      data-testid={`screen-${plan.screenId}`}
      data-layout-mode={plan.shell.layoutMode}
      data-mobile-layout={plan.shell.mobileMode}
      data-render-plan-cache-key={plan.cacheKey}
    >
      <ActionBarRenderer
        domain={plan.shell.domain}
        mode={plan.shell.mode}
        title={plan.shell.title}
        subtitle={plan.shell.subtitle}
        actions={plan.actions}
        headerClassName={classes.header}
        touchTargetClass={classes.touchTarget}
        onAction={onAction}
        payload={payload}
      />
    </div>
  )
})
