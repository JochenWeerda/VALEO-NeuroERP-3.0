import type { RenderPlan } from '../../render-plan/types'
import { useQueueController } from './queue-controller'
import { QueueRenderer } from './queue-renderer'
export default function QueueSurface({ plan }: { plan: RenderPlan }): JSX.Element {
  return <QueueRenderer state={useQueueController(plan)} />
}
