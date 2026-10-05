import type { ScreenColumnNavigation, ScreenFloorplan, ScreenMode } from '../schema'

/**
 * Abgeleitetes Vokabular. Gespeichert wird weiter floorplan + mode + columnNavigation.
 * LIST, FORM und listReport sind keine eigenen Felder.
 */
export type DerivedScreenType =
  | 'WORKLIST'
  | 'DETAIL'
  | 'MASTER_DETAIL'
  | 'DASHBOARD'
  | 'PROCESS'
  | 'REPORT'

const REJECTED_KEYS = ['screenType', 'listReport', 'form'] as const

export function derivedScreenType(
  floorplan: ScreenFloorplan | undefined,
  mode: ScreenMode | undefined,
  columnNavigation?: ScreenColumnNavigation,
): DerivedScreenType | null {
  if (columnNavigation === 'listDetail' || columnNavigation === 'listDetailDetail') {
    if (floorplan === 'worklist' || floorplan === 'objectPage') return 'MASTER_DETAIL'
  }
  if (floorplan === 'worklist') return 'WORKLIST'
  if (floorplan === 'objectPage') return 'DETAIL'
  if (floorplan === 'transaction' || floorplan === 'wizard') return 'PROCESS'
  if (floorplan === 'cockpit') return 'DASHBOARD'
  if (floorplan === 'analyticalList') return 'REPORT'
  if (mode === 'list') return 'WORKLIST'
  return null
}

export function rejectedScreenTypeKeys(definition: object): string[] {
  return REJECTED_KEYS.filter((key) => Object.prototype.hasOwnProperty.call(definition, key))
}
