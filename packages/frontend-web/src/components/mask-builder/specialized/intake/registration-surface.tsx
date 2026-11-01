import type { RenderPlan } from '../../render-plan/types'
import { useRegistrationController } from './registration-controller'
import { RegistrationRenderer } from './registration-renderer'
export default function RegistrationSurface({ plan }: { plan: RenderPlan }): JSX.Element {
  return <RegistrationRenderer state={useRegistrationController(plan)} />
}
