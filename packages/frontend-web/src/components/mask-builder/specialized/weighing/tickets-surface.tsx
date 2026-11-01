import type { RenderPlan } from '../../render-plan/types'
import { useTicketsController } from './tickets-controller'
import { TicketsRenderer } from './tickets-renderer'
export default function TicketsSurface({ plan }: { plan: RenderPlan }): JSX.Element {
  return <TicketsRenderer state={useTicketsController(plan)} />
}
