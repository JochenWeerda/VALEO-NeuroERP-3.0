import type { RenderPlan } from '../../render-plan/types'
import { useQualityController } from './quality-controller'
import { QualityRenderer } from './quality-renderer'
export default function QualitySurface({ plan }: { plan: RenderPlan }): JSX.Element {
  return <QualityRenderer state={useQualityController(plan)} />
}
