/**
 * Anzeige-Helfer für Agrar-Materialfluss / Silo-QS (WM-AGRI-SILO-001).
 * Werte entsprechen Backend-Checks (silo_cells.qs_status, material_flow_nodes.status).
 */

import type { Edge, Node } from '@xyflow/react'

/** API-Zeilen (GET /lager/wms/agri/material-flow/nodes) → React-Flow-Knoten. */
export type AgriFlowLike = Record<string, unknown>

function agriPickStr(row: AgriFlowLike, key: string): string {
  const v = row[key]
  return v == null ? '' : String(v)
}

function parseLayoutCoord(v: unknown): number | null {
  if (v == null || v === '') return null
  const n = typeof v === 'number' ? v : Number(v)
  return Number.isFinite(n) ? n : null
}

/**
 * Mappt Stammdaten-Knoten auf React-Flow.
 * Nutzt `layout_x` / `layout_y` sofern gesetzt; sonst deterministisches Raster (keine Zufallsposition).
 */
export function agriMaterialFlowApiToReactFlowNodes(rows: AgriFlowLike[]): Node[] {
  const sorted = [...rows].sort((a, b) => agriPickStr(a, 'code').localeCompare(agriPickStr(b, 'code')))
  return sorted.map((row, i) => {
    const id = agriPickStr(row, 'id')
    const lx = parseLayoutCoord(row.layout_x)
    const ly = parseLayoutCoord(row.layout_y)
    const col = i % 5
    const rowIdx = Math.floor(i / 5)
    const position =
      lx != null && ly != null ? { x: lx, y: ly } : { x: col * 220, y: rowIdx * 140 }
    const code = agriPickStr(row, 'code')
    const ntype = agriPickStr(row, 'node_type')
    const name = agriPickStr(row, 'name')
    const status = agriPickStr(row, 'status') || 'active'
    return {
      id: id || `row-${i}`,
      type: 'mfProcess',
      position,
      data: {
        label: code ? `${code} (${ntype || '?'})` : ntype || 'Knoten',
        sub: name || undefined,
        status,
      },
    } satisfies Node
  })
}

/**
 * Kanten nur wenn beide Endpunkt-IDs in `nodeIds` vorkommen (verhindert hängende Kanten nach Teildaten).
 */
export function agriMaterialFlowApiToReactFlowEdges(rows: AgriFlowLike[], nodeIds: Set<string>): Edge[] {
  const out: Edge[] = []
  for (const row of rows) {
    const id = agriPickStr(row, 'id')
    const src = agriPickStr(row, 'from_node_id')
    const tgt = agriPickStr(row, 'to_node_id')
    if (!src || !tgt || !nodeIds.has(src) || !nodeIds.has(tgt)) continue
    const st = (agriPickStr(row, 'status') || 'open').toLowerCase()
    out.push({
      id: id || `${src}->${tgt}`,
      source: src,
      target: tgt,
      animated: st === 'open',
      label: st !== 'open' ? flowEdgeStatusGermanLabel(st) : undefined,
    })
  }
  return out
}

export function qsStatusToBadgeVariant(qs: string | null | undefined): 'default' | 'secondary' | 'destructive' | 'outline' {
  const k = (qs ?? 'frei').toLowerCase()
  if (k === 'frei') return 'secondary'
  if (k === 'gesperrt') return 'destructive'
  if (k === 'in_pruefung') return 'outline'
  if (k === 'reinigung') return 'outline'
  if (k === 'reserviert') return 'outline'
  return 'outline'
}

export function qsStatusGermanLabel(qs: string | null | undefined): string {
  const k = (qs ?? 'frei').toLowerCase()
  const map: Record<string, string> = {
    frei: 'frei',
    gesperrt: 'gesperrt',
    in_pruefung: 'in Prüfung',
    reinigung: 'Reinigung',
    reserviert: 'reserviert',
  }
  return map[k] ?? qs ?? '—'
}

export function flowNodeStatusGermanLabel(st: string | null | undefined): string {
  const k = (st ?? 'active').toLowerCase()
  const map: Record<string, string> = {
    active: 'aktiv',
    blocked: 'gesperrt',
    maintenance: 'Wartung',
    cleaning: 'Reinigung',
  }
  return map[k] ?? st ?? '—'
}

/** CSS-Rahmenfarbe für React-Flow-Knoten (Tailwind-Klassen). */
export function flowNodeStatusBorderClass(st: string | null | undefined): string {
  const k = (st ?? 'active').toLowerCase()
  if (k === 'active') return 'border-emerald-600/80 bg-emerald-50/90 dark:bg-emerald-950/40'
  if (k === 'blocked') return 'border-red-600/90 bg-red-50/90 dark:bg-red-950/40'
  if (k === 'maintenance') return 'border-amber-600/90 bg-amber-50/90 dark:bg-amber-950/40'
  if (k === 'cleaning') return 'border-sky-600/90 bg-sky-50/90 dark:bg-sky-950/40'
  return 'border-muted-foreground/50 bg-card'
}

export function flowEdgeStatusGermanLabel(st: string | null | undefined): string {
  const k = (st ?? 'open').toLowerCase()
  const map: Record<string, string> = {
    open: 'offen',
    blocked: 'gesperrt',
    maintenance: 'Wartung',
    cleaning: 'Reinigung',
  }
  return map[k] ?? st ?? '—'
}
