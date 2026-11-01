import type { RenderPlan } from '../../render-plan/types'
import { useScaleCreateController } from './scale-create-controller'
import { ScaleCreateRenderer } from './scale-create-renderer'

export default function ScaleCreateSurface({ plan }: { plan: RenderPlan }): JSX.Element {
  const action = plan.actions.find(item => item.key === 'create')
  const enabled = Boolean(action && !action.disabled && !action.enabledWhen && ['standort', 'typ', 'max_kapazitaet'].every(key => plan.fieldsByKey[key]?.visible && !plan.fieldsByKey[key]?.readOnly))
  const state = useScaleCreateController(enabled, plan)
  return <ScaleCreateRenderer plan={plan} state={state} />
}
