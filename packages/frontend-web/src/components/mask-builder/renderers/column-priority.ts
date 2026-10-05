import type { RenderColumnPriority } from '../render-plan/types'

/** Unter 720 px nur primary, darunter 1024 px ohne tertiary. Fehlende Priorität bleibt sichtbar. */
export function columnsForWidth<T extends { priority?: RenderColumnPriority }>(columns: T[], width: number): T[] {
  return columns.filter((column) => {
    const priority = column.priority ?? 'primary'
    if (priority === 'tertiary') return width >= 1024
    if (priority === 'secondary') return width >= 720
    return true
  })
}
