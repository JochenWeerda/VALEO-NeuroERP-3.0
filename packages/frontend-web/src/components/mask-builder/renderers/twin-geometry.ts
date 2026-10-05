/**
 * Twin-Panel Geometrie + Metrik-Farblogik (UIX-081) — rein & testbar.
 *
 * Wandelt Plan-Geometrie (rect/polygon) in SVG-Pfade und Metrik-Werte in
 * deterministische Darstellungs-Hinweise (Fuellfarbe, Warnkontur, Sperr-
 * Schraffur, Status-Chip). Kein React, keine Seiteneffekte.
 */

export type TwinShape =
  | { kind: 'rect'; x: number; y: number; w: number; h: number }
  | { kind: 'polygon'; points: [number, number][] }

export interface TwinCellDef {
  id: string
  label?: string
  shape: TwinShape
}

export interface TwinPlan {
  plan_id: string
  canvas: { width: number; height: number }
  background?: string
  cells: TwinCellDef[]
}

export type TwinMetricKind = 'percent' | 'number' | 'flag' | 'status'

export interface TwinMetricDef {
  key: string
  label: string
  kind: TwinMetricKind
  warnAbove?: number
}

export interface ParseResult {
  plan: TwinPlan | null
  errors: string[]
}

function isFiniteNumber(v: unknown): v is number {
  return typeof v === 'number' && Number.isFinite(v)
}

function validateShape(shape: unknown, path: string, errors: string[]): TwinShape | null {
  if (!shape || typeof shape !== 'object') {
    errors.push(`${path}: shape fehlt`)
    return null
  }
  const s = shape as Record<string, unknown>
  if (s.kind === 'rect') {
    if ([s.x, s.y, s.w, s.h].every(isFiniteNumber) && (s.w as number) > 0 && (s.h as number) > 0) {
      return { kind: 'rect', x: s.x as number, y: s.y as number, w: s.w as number, h: s.h as number }
    }
    errors.push(`${path}: rect braucht endliche x/y/w/h (w,h>0)`)
    return null
  }
  if (s.kind === 'polygon') {
    const pts = s.points
    if (
      Array.isArray(pts) &&
      pts.length >= 3 &&
      pts.every((p) => Array.isArray(p) && p.length === 2 && p.every(isFiniteNumber))
    ) {
      return { kind: 'polygon', points: pts.map((p) => [p[0], p[1]] as [number, number]) }
    }
    errors.push(`${path}: polygon braucht >=3 [x,y]-Punkte`)
    return null
  }
  errors.push(`${path}: unbekannte shape.kind '${String(s.kind)}'`)
  return null
}

/** Validiert ein rohes Plan-Objekt (aus YAML). Fehlerhafte Zellen werden
 * verworfen und gemeldet — nie ein harter Fehler, solange Canvas/plan_id ok. */
export function parseTwinPlan(raw: unknown): ParseResult {
  const errors: string[] = []
  if (!raw || typeof raw !== 'object') return { plan: null, errors: ['plan ist kein Objekt'] }
  const r = raw as Record<string, unknown>
  const canvas = r.canvas as Record<string, unknown> | undefined
  if (!r.plan_id || typeof r.plan_id !== 'string') errors.push('plan_id fehlt')
  if (!canvas || !isFiniteNumber(canvas.width) || !isFiniteNumber(canvas.height)) {
    errors.push('canvas.width/height fehlt')
  }
  if (errors.length > 0) return { plan: null, errors }
  const cv = canvas as { width: number; height: number }

  const cells: TwinCellDef[] = []
  const seen = new Set<string>()
  for (const [i, rawCell] of ((r.cells as unknown[]) ?? []).entries()) {
    const c = rawCell as Record<string, unknown>
    const id = typeof c?.id === 'string' ? c.id : ''
    if (!id) {
      errors.push(`cells[${i}]: id fehlt`)
      continue
    }
    if (seen.has(id)) {
      errors.push(`cells[${i}]: doppelte id '${id}'`)
      continue
    }
    const shape = validateShape(c.shape, `cells[${i}]`, errors)
    if (!shape) continue
    seen.add(id)
    cells.push({ id, label: typeof c.label === 'string' ? c.label : undefined, shape })
  }

  return {
    plan: {
      plan_id: r.plan_id as string,
      canvas: { width: cv.width, height: cv.height },
      background: typeof r.background === 'string' ? r.background : undefined,
      cells,
    },
    errors,
  }
}

/** Erzeugt den SVG-Pfad ('d') einer Zellen-Geometrie. */
export function shapeToPath(shape: TwinShape): string {
  if (shape.kind === 'rect') {
    const { x, y, w, h } = shape
    return `M ${x} ${y} h ${w} v ${h} h ${-w} Z`
  }
  const [first, ...rest] = shape.points
  const lines = rest.map(([px, py]) => `L ${px} ${py}`).join(' ')
  return `M ${first[0]} ${first[1]} ${lines} Z`
}

export interface CellStyle {
  /** Fuellfarbe (Gold-Verlauf nach Fuellstand) */
  fill: string
  /** Warnkontur bei Grenzwert-Ueberschreitung */
  stroke: string
  strokeWidth: number
  /** Sperr-Schraffur aktiv */
  hatched: boolean
}

/** Interpoliert einen Gold-Verlauf (hell→satt) nach Fuellstand 0..100. */
function goldFill(pct: number): string {
  const p = Math.max(0, Math.min(100, pct)) / 100
  // hell (#fdf6e3) → sattes Gold (#c8860a)
  const lerp = (a: number, b: number) => Math.round(a + (b - a) * p)
  return `rgb(${lerp(253, 200)}, ${lerp(246, 134)}, ${lerp(227, 10)})`
}

/**
 * Deterministische Darstellungs-Hinweise einer Zelle aus ihren Metrikwerten.
 * warnAbove-Ueberschreitung → danger-Kontur; locked → Schraffur.
 */
export function cellStyle(
  metrics: TwinMetricDef[],
  values: Record<string, unknown>,
): CellStyle {
  let fill = '#e5e7eb' // neutral, wenn kein Fuellstand
  let stroke = '#94a3b8'
  let strokeWidth = 1
  let hatched = false

  for (const metric of metrics) {
    const value = values[metric.key]
    if (metric.kind === 'percent' && isFiniteNumber(value)) {
      fill = goldFill(value)
    }
    if (metric.warnAbove !== undefined && isFiniteNumber(value) && value > metric.warnAbove) {
      stroke = '#dc2626' // danger
      strokeWidth = 2.5
    }
    if (metric.kind === 'flag' && value === true) {
      hatched = true
    }
  }
  return { fill, stroke, strokeWidth, hatched }
}

/** Reihenfolge fuer Tab-Navigation: stabile Sortierung nach Zellen-id. */
export function keyboardOrder(cells: TwinCellDef[]): string[] {
  return [...cells].map((c) => c.id).sort()
}
