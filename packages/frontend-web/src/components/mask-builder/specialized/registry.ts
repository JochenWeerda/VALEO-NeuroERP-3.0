import type { SpecializedComponentType } from '../schema'
import { DispositionBoard } from './disposition-board'
import type { SpecializedComponentModule } from './types'

const REGISTRY: Record<SpecializedComponentType, SpecializedComponentModule> = {
  disposition_board: DispositionBoard,
}

export function resolveSpecializedComponent(
  type: SpecializedComponentType,
): SpecializedComponentModule | undefined {
  return REGISTRY[type]
}

export function registeredSpecializedTypes(): SpecializedComponentType[] {
  return Object.keys(REGISTRY) as SpecializedComponentType[]
}
