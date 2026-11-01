import type { ScreenSpecializedComponent } from '../schema'
import type { RenderPlan } from '../render-plan/types'
import { resolveSpecializedComponent } from './registry'

export function SpecializedComponentHost({
  specialized,
  plan,
  onAction,
}: {
  specialized?: ScreenSpecializedComponent
  plan?: RenderPlan
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
}): JSX.Element | null {
  if (!specialized) return null
  const Component = resolveSpecializedComponent(specialized.type)
  if (!Component) {
    return (
      <p role="alert" className="text-sm text-status-error">
        Unbekannte Spezialkomponente: {specialized.type}
      </p>
    )
  }
  return <Component contract={specialized} plan={plan} onAction={onAction} />
}
