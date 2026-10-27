import type { ScreenSpecializedComponent } from '../schema'

export type SpecializedComponentType = ScreenSpecializedComponent['type']

export const DISPOSITION_BOARD_EVENTS = {
  assignmentConfirmed: 'logistik.tour.created',
  quantityPosted: 'logistics.tour.quantity_posted',
  dropProposed: 'disposition.board.drop_proposed',
} as const

export interface SpecializedComponentProps {
  contract: ScreenSpecializedComponent
  onAction?: (_actionKey: string, _payload: Record<string, unknown>) => void | Promise<void>
}

export type SpecializedComponentModule = (props: SpecializedComponentProps) => JSX.Element
