import type { RenderPlan } from '../../render-plan/types'
import { useRohwareController } from './rohware-controller'
import { RohwareRenderer } from './rohware-renderer'

export default function RohwareSurface({ plan }: { plan: RenderPlan }): JSX.Element {
  return <RohwareRenderer state={useRohwareController(plan)} />
}
