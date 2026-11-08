import type { SpecializedComponentType } from '../schema'
import { DispositionBoard } from './disposition-board'
import { Intake } from './intake/intake'
import { Weighing } from './weighing/weighing'
import { FinanceWorkbench } from './finance/finance-workbench'
import { AdminWorkbench } from './admin/admin-workbench'
import { FeedWorkbench } from './feed/feed-workbench'
import type { SpecializedComponentModule } from './types'

const REGISTRY: Record<SpecializedComponentType, SpecializedComponentModule> = {
  disposition_board: DispositionBoard,
  intake: Intake,
  weighing: Weighing,
  finance_workbench: FinanceWorkbench,
  admin_workbench: AdminWorkbench,
  feed_workbench: FeedWorkbench,
}

export function resolveSpecializedComponent(
  type: SpecializedComponentType,
): SpecializedComponentModule | undefined {
  return REGISTRY[type]
}

export function registeredSpecializedTypes(): SpecializedComponentType[] {
  return Object.keys(REGISTRY) as SpecializedComponentType[]
}
