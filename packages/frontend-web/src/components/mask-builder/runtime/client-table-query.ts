import type { FilterValue, TableQueryState } from './types'

type Row = Record<string, unknown>

function text(value: unknown): string {
  return value == null ? '' : String(value).toLowerCase()
}

function compare(left: unknown, right: unknown): number {
  if (typeof left === 'number' && typeof right === 'number') return left - right
  return text(left).localeCompare(text(right), 'de', { numeric: true })
}

function matches(value: unknown, filter: FilterValue): boolean {
  const wanted = filter.value
  switch (filter.op) {
    case 'eq': return text(value) === text(wanted)
    case 'neq': return text(value) !== text(wanted)
    case 'lt': return compare(value, wanted) < 0
    case 'lte': return compare(value, wanted) <= 0
    case 'gt': return compare(value, wanted) > 0
    case 'gte': return compare(value, wanted) >= 0
    case 'in': return Array.isArray(wanted) && wanted.some((entry) => text(entry) === text(value))
    case 'between': {
      const [from, to] = Array.isArray(wanted) ? wanted : []
      return compare(value, from) >= 0 && compare(value, to) <= 0
    }
    default: return text(value).includes(text(wanted))
  }
}

/**
 * Suche, Filter, Sortierung und Seite im Browser fuer Tabellen ohne Serverblaetterung (MASK-STUDIO-ROLLOUT).
 *
 * Vorher schickte die Laufzeit `page`/`limit`/`q` auch an Dienste, die das nicht auswerten: Die Suche lief ins Leere,
 * und der Renderer zeigte nur die erste Seite ohne Blaettern.
 */
export function applyClientTableQuery(rows: Row[], state: TableQueryState): { rows: Row[]; total: number } {
  const suche = text(state.q).trim()
  let result = suche ? rows.filter((row) => Object.values(row).some((value) => text(value).includes(suche))) : rows
  for (const [key, filter] of Object.entries(state.filterPlan ?? {})) {
    result = result.filter((row) => matches(row[key], filter))
  }
  if (state.sort) {
    const key = state.sort
    const richtung = state.sortDir === 'desc' ? -1 : 1
    result = [...result].sort((left, right) => richtung * compare(left[key], right[key]))
  }
  const start = (Math.max(1, state.page) - 1) * state.pageSize
  return { rows: result.slice(start, start + state.pageSize), total: result.length }
}
