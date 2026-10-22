/**
 * Nutzer-Overlays (UIX-071) — Personalisierung ohne Fork.
 *
 * `applyOverlay(plan, overlay)` wird NACH dem Compile und VOR dem Render-Cache
 * angewendet. Eine harte Allowlist schuetzt Sicherheits-/Vertragsfelder: alles
 * ausserhalb (actions, permissions, dangerLevel, confirmation, fields,
 * tableProfile, floorplan, contextRailSections) wird verworfen und als
 * OverlayViolation gemeldet — Overlays koennen Gates niemals aufweichen.
 * Drift (Overlay-Keys ohne Plan-Entsprechung) landet in invalidPaths → Rail-
 * Hinweis "Anpassung pruefen"; nie ein Fehler.
 */
import type { RenderPlan, RenderTableColumnPlan, RenderTableVariant } from './types'
import type { ScreenDensity } from '../schema'

export interface ScreenTableOverlay {
  visibleColumns?: string[]
  columnWidths?: Record<string, number>
  activeVariant?: string
  customVariants?: RenderTableVariant[]
}

export interface ScreenOverlay {
  tables?: Record<string, ScreenTableOverlay>
  density?: ScreenDensity
  tileOrder?: string[]
  collapsedSections?: string[]
  /** Von der Overlay-Quelle mitgeliefert; Mismatch degradiert sanft. */
  schemaVersion?: number
}

/** Overlaybare Top-Level-Keys — alles andere ist eine Verletzung. */
export const OVERLAYABLE_KEYS = new Set([
  'tables',
  'density',
  'tileOrder',
  'collapsedSections',
  'schemaVersion',
])

/** Innerhalb von tables[<key>] overlaybare Keys. */
export const OVERLAYABLE_TABLE_KEYS = new Set([
  'visibleColumns',
  'columnWidths',
  'activeVariant',
  'customVariants',
])

/** Explizit nicht overlaybar — Sicherheits-/Vertragsfelder (Doku + Test). */
export const NON_OVERLAYABLE_KEYS = [
  'actions',
  'permissions',
  'dangerLevel',
  'confirmation',
  'contextRailSections',
  'fields',
  'tableProfile',
  'floorplan',
]

const VALID_DENSITIES: ReadonlySet<string> = new Set(['comfortable', 'compact', 'expertDense'])

export interface ApplyOverlayResult {
  plan: RenderPlan
  /** Overlay-Keys, die im Plan nicht existieren (Drift). */
  invalidPaths: string[]
  /** Verworfene, nicht overlaybare Keys (Sicherheit). */
  violations: string[]
}

/**
 * Wendet ein validiertes Overlay auf einen RenderPlan an. Rein & immutabel:
 * gibt einen neuen Plan zurueck; der Eingabe-Plan bleibt unveraendert.
 */
export function applyOverlay(plan: RenderPlan, overlay: ScreenOverlay | null | undefined): ApplyOverlayResult {
  const invalidPaths: string[] = []
  const violations: string[] = []
  if (!overlay || typeof overlay !== 'object') {
    return { plan, invalidPaths, violations }
  }

  // Sicherheits-Allowlist: unbekannte Top-Level-Keys verwerfen + melden.
  for (const key of Object.keys(overlay)) {
    if (!OVERLAYABLE_KEYS.has(key)) violations.push(key)
  }

  const next: RenderPlan = { ...plan, shell: { ...plan.shell }, tablesByKey: { ...plan.tablesByKey } }

  // density
  if (overlay.density !== undefined) {
    if (VALID_DENSITIES.has(overlay.density)) next.shell = { ...next.shell, density: overlay.density }
    else invalidPaths.push(`density:${overlay.density}`)
  }

  // tables
  if (overlay.tables) {
    for (const [tableKey, tableOverlay] of Object.entries(overlay.tables)) {
      const base = next.tablesByKey[tableKey]
      if (!base) {
        invalidPaths.push(`tables.${tableKey}`)
        continue
      }
      for (const k of Object.keys(tableOverlay)) {
        if (!OVERLAYABLE_TABLE_KEYS.has(k)) violations.push(`tables.${tableKey}.${k}`)
      }
      let columns: RenderTableColumnPlan[] = base.columns
      const availableColumns = base.availableColumns ?? base.columns
      if (tableOverlay.visibleColumns) {
        const byKey = new Map(availableColumns.map((c) => [c.key, c]))
        const picked: RenderTableColumnPlan[] = []
        for (const colKey of tableOverlay.visibleColumns) {
          const col = byKey.get(colKey)
          if (col) picked.push(col)
          else invalidPaths.push(`tables.${tableKey}.visibleColumns.${colKey}`)
        }
        // Nur uebernehmen, wenn mindestens eine gueltige Spalte bleibt.
        if (picked.length > 0) columns = picked
      }
      if (tableOverlay.columnWidths) {
        columns = columns.map((c) =>
          tableOverlay.columnWidths && c.key in tableOverlay.columnWidths
            ? { ...c, width: tableOverlay.columnWidths[c.key] }
            : c,
        )
        for (const widthKey of Object.keys(tableOverlay.columnWidths)) {
          if (!availableColumns.some((c) => c.key === widthKey)) {
            invalidPaths.push(`tables.${tableKey}.columnWidths.${widthKey}`)
          }
        }
      }
      next.tablesByKey[tableKey] = {
        ...base,
        columns,
        availableColumns,
        activeVariant: tableOverlay.activeVariant ?? base.activeVariant,
        customVariants: tableOverlay.customVariants ?? base.customVariants,
      }
    }
  }

  // tileOrder — reine Umsortierung; unbekannte Keys → Drift, fehlende bleiben hinten.
  if (overlay.tileOrder && next.tiles.length > 0) {
    const rank = new Map(overlay.tileOrder.map((k, i) => [k, i]))
    for (const key of overlay.tileOrder) {
      if (!next.tiles.some((t) => t.key === key)) invalidPaths.push(`tileOrder.${key}`)
    }
    next.tiles = [...next.tiles].sort(
      (a, b) => (rank.get(a.key) ?? Number.MAX_SAFE_INTEGER) - (rank.get(b.key) ?? Number.MAX_SAFE_INTEGER),
    )
  }

  // collapsedSections — reine Annotation.
  if (overlay.collapsedSections) {
    next.collapsedSections = [...overlay.collapsedSections]
  }

  if (invalidPaths.length > 0) next.overlayInvalidPaths = invalidPaths

  return { plan: next, invalidPaths, violations }
}

/** Stabiler Hash eines Overlays fuer den Render-Plan-Cache-Key (UIX-071). */
export function hashOverlay(overlay: ScreenOverlay | null | undefined): string {
  if (!overlay) return 'no-overlay'
  const stable = (value: unknown): unknown => {
    if (Array.isArray(value)) return value.map(stable)
    if (value && typeof value === 'object') {
      return Object.keys(value as Record<string, unknown>)
        .sort()
        .reduce<Record<string, unknown>>((acc, k) => {
          acc[k] = stable((value as Record<string, unknown>)[k])
          return acc
        }, {})
    }
    return value
  }
  return JSON.stringify(stable(overlay))
}
