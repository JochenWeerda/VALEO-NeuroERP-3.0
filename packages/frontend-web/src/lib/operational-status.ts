export type OperationalStatus =
  | 'offen'
  | 'in_pruefung'
  | 'blockiert'
  | 'teilweise'
  | 'wartet_auf_extern'
  | 'wartet_auf_mensch'
  | 'abgeschlossen'
  | 'eskaliert'

export function normalizeOperationalStatus(value: string | null | undefined): OperationalStatus {
  const raw = String(value ?? '').trim().toLowerCase()

  if ([
    'offen',
    'entwurf',
    'erfasst',
    'recorded',
    'draft',
    'unallocated',
    'neu',
  ].includes(raw)) {
    return 'offen'
  }

  if ([
    'in_pruefung',
    'geprueft',
    'reviewed',
    'angebotsphase',
    'pending_review',
  ].includes(raw)) {
    return 'in_pruefung'
  }

  if ([
    'blockiert',
    'gesperrt',
    'rejected',
    'abgelehnt',
    'storniert',
    'cancelled',
    'cancelled_with_reason',
  ].includes(raw)) {
    return 'blockiert'
  }

  if ([
    'teilweise',
    'teilgeliefert',
    'partially_allocated',
    'teilweise_anerkannt',
    'partial',
  ].includes(raw)) {
    return 'teilweise'
  }

  if ([
    'wartet_auf_extern',
    'bestellt',
    'in_bestellung',
    'sent',
    'portal',
    'email',
    'posted',
  ].includes(raw)) {
    return 'wartet_auf_extern'
  }

  if ([
    'wartet_auf_mensch',
    'freigegeben',
    'genehmigt',
    'approved',
    'pending_approval',
  ].includes(raw)) {
    return 'wartet_auf_mensch'
  }

  if ([
    'abgeschlossen',
    'geschlossen',
    'geliefert',
    'vollgeliefert',
    'allocated',
    'completed',
    'anerkannt',
    'done',
  ].includes(raw)) {
    return 'abgeschlossen'
  }

  if ([
    'eskaliert',
    'ueberfaellig',
    'overdue',
    'urgent',
  ].includes(raw)) {
    return 'eskaliert'
  }

  return 'offen'
}

export function operationalStatusLabel(status: OperationalStatus): string {
  switch (status) {
    case 'offen':
      return 'Offen'
    case 'in_pruefung':
      return 'In Pruefung'
    case 'blockiert':
      return 'Blockiert'
    case 'teilweise':
      return 'Teilweise'
    case 'wartet_auf_extern':
      return 'Wartet auf extern'
    case 'wartet_auf_mensch':
      return 'Wartet auf Mensch'
    case 'abgeschlossen':
      return 'Abgeschlossen'
    case 'eskaliert':
      return 'Eskaliert'
  }
}

export function operationalStatusVariant(status: OperationalStatus): 'default' | 'secondary' | 'outline' | 'destructive' {
  switch (status) {
    case 'abgeschlossen':
      return 'outline'
    case 'wartet_auf_mensch':
    case 'in_pruefung':
      return 'default'
    case 'teilweise':
    case 'wartet_auf_extern':
    case 'offen':
      return 'secondary'
    case 'blockiert':
    case 'eskaliert':
      return 'destructive'
  }
}
