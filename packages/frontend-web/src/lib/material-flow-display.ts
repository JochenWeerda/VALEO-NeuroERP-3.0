/**
 * Anzeige-Helfer für Agrar-Materialfluss / Silo-QS (WM-AGRI-SILO-001).
 * Werte entsprechen Backend-Checks (silo_cells.qs_status, material_flow_nodes.status).
 */

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
