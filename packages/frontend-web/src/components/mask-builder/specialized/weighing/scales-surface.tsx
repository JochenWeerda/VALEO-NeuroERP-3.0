import type { RenderPlan } from '../../render-plan/types'
import { useScalesController } from './scales-controller'
import { ScalesRenderer } from './scales-renderer'
export default function ScalesSurface({ plan }: { plan: RenderPlan }): JSX.Element {
  return <ScalesRenderer state={useScalesController(plan)} />
}
