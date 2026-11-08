import {
  getDocumentEntryPolicy,
  type DocumentEntryPolicyId,
} from '@/lib/workflow/document-entry-policy'
import {
  INBOX_PREFILL_SCHEMA,
  INBOX_PREFILL_STORAGE_KEY,
  type InboxAction,
  type InboxCommand,
  type InboxPrefillPayload,
  type InboxQueueItem,
} from './types'

const BAND_RANK: Record<InboxQueueItem['confidence_band'], number> = {
  review: 0,
  low: 1,
  medium: 2,
  high: 3,
}

/** Listen-Host der Eingangsrechnung bleibt unverändert; nur diese Art öffnet die Create-Route. */
export const INBOX_SUPPLIER_INVOICE_LIST_ROUTE = '/einkauf/rechnung-eingang-erfassung'
export const INBOX_SUPPLIER_INVOICE_CREATE_ROUTE = '/belege/purchase_invoice/neu'
/** Einkaufs-Lieferschein-Übersicht. Kein Prefill, kein Einzelbeleg ohne Detailroute. */
export const INBOX_DELIVERY_NOTE_ROUTE = '/einkauf/lieferschein-erfassung'
/** Verkaufs-Gutschriften-Übersicht (outgoing). Kein Einzelbeleg. */
export const INBOX_SALES_CREDIT_LIST_ROUTE = '/sales/credit-notes'
/** Einkaufs-Gutschriften/Belastungen-Übersicht (incoming). Kein Einzelbeleg. */
export const INBOX_PURCHASE_CREDIT_LIST_ROUTE = '/einkauf/gutschriften-belastungen'
/** Wiegeschein-Übersicht unter /weighing (ohne :id). */
export const INBOX_WEIGHING_LIST_ROUTE = '/weighing'
/** Detailroute nur mit verifizierter Schein-ID — kein Raten. */
export const INBOX_WEIGHING_DETAIL_ROUTE_PREFIX = '/waage/wiegeschein'

export const INBOX_OVERVIEW_ACTION_LABEL = 'Zur Übersicht'
export const INBOX_OPEN_DOCUMENT_ACTION_LABEL = 'Beleg öffnen'

/** @deprecated Alias — nutze INBOX_SALES_CREDIT_LIST_ROUTE / Richtung. */
export const INBOX_CREDIT_NOTE_LIST_ROUTE = INBOX_SALES_CREDIT_LIST_ROUTE

export type InboxOpenMode = 'document' | 'overview' | 'none'

export type InboxOpenDecision = {
  href: string
  reason: string | null
  consumesPrefill: boolean
  mode: InboxOpenMode
  /** Primärer Button: „Beleg öffnen“ oder „Zur Übersicht“. */
  actionLabel: string
  /** Separater Einzelbeleg-Pfad; nur mit verifizierter `linked_document_id`. */
  documentOpenHref: string
  documentOpenEnabled: boolean
  documentOpenReason: string | null
}

const OPEN_REASON_UNKNOWN_KIND = 'Dokumentart nicht erkannt. Ohne Art wird keine Maske geraten.'
const OPEN_REASON_NO_PERMISSION = 'Keine Berechtigung fuer die Zielmaske.'
const OPEN_REASON_ACTION_DISABLED = 'Beleg öffnen ist fuer diesen Vorschlag gesperrt.'
const OPEN_REASON_NO_BELEG_ID = 'Beleg öffnen braucht eine verifizierte Beleg-ID.'
const OPEN_REASON_CREDIT_NO_DETAIL =
  'Keine Detailroute fuer Gutschrift mit Beleg-ID. Nur die Uebersicht ist verfuegbar.'
const OPEN_REASON_DELIVERY_NO_DETAIL =
  'Keine Detailroute fuer Lieferschein mit Beleg-ID. Nur die Uebersicht ist verfuegbar.'
const OPEN_REASON_CREDIT_DIRECTION =
  'Gutschrift-Richtung unklar. Ohne incoming/outgoing wird keine Liste geraten.'

export function rewriteInboxTargetHref(href: string): string {
  const [path, query] = href.split('?')
  if (path !== INBOX_SUPPLIER_INVOICE_LIST_ROUTE) return href
  return query ? `${INBOX_SUPPLIER_INVOICE_CREATE_ROUTE}?${query}` : INBOX_SUPPLIER_INVOICE_CREATE_ROUTE
}

function withInboxPointer(route: string, itemId: string): string {
  const glue = route.includes('?') ? '&' : '?'
  return `${route}${glue}inbox=${encodeURIComponent(itemId)}`
}

function verifiedBelegId(item: InboxQueueItem): string | null {
  const raw = item.linked_document_id
  if (typeof raw !== 'string') return null
  const id = raw.trim()
  return id.length > 0 ? id : null
}

function noneDecision(reason: string): InboxOpenDecision {
  return {
    href: '',
    reason,
    consumesPrefill: false,
    mode: 'none',
    actionLabel: INBOX_OPEN_DOCUMENT_ACTION_LABEL,
    documentOpenHref: '',
    documentOpenEnabled: false,
    documentOpenReason: reason,
  }
}

function documentDecision(
  href: string,
  consumesPrefill: boolean,
): InboxOpenDecision {
  return {
    href,
    reason: null,
    consumesPrefill,
    mode: 'document',
    actionLabel: INBOX_OPEN_DOCUMENT_ACTION_LABEL,
    documentOpenHref: href,
    documentOpenEnabled: true,
    documentOpenReason: null,
  }
}

function overviewDecision(
  listRoute: string,
  itemId: string,
  documentOpen: { href: string; enabled: boolean; reason: string | null },
): InboxOpenDecision {
  return {
    href: withInboxPointer(listRoute, itemId),
    reason: null,
    consumesPrefill: false,
    mode: 'overview',
    actionLabel: INBOX_OVERVIEW_ACTION_LABEL,
    documentOpenHref: documentOpen.href,
    documentOpenEnabled: documentOpen.enabled,
    documentOpenReason: documentOpen.reason,
  }
}

function creditListRoute(direction: InboxQueueItem['proposal']['direction']): string | null {
  if (direction === 'outgoing') return INBOX_SALES_CREDIT_LIST_ROUTE
  if (direction === 'incoming') return INBOX_PURCHASE_CREDIT_LIST_ROUTE
  return null
}

/**
 * Öffnet nur nach `proposal.document_kind`.
 * EINGANGSRECHNUNG → native Beleganlage (`/belege/purchase_invoice/neu?inbox=…`).
 * LIEFERSCHEIN → Listen-Übersicht ohne Prefill („Zur Übersicht“); Beleg öffnen
 * nur mit verifizierter ID und Detailroute (derzeit keine Detailroute).
 * GUTSCHRIFT / WIEGESCHEIN → Listen-Übersicht; Beleg öffnen nur mit
 * verifizierter `linked_document_id` und vorhandener Detailroute.
 * GUTSCHRIFT ohne incoming/outgoing → mode none (kein erratenes „Zur Übersicht“).
 */
export function inboxOpenDecision(item: InboxQueueItem): InboxOpenDecision {
  if (item.can_open === false) {
    const detail = item.uncertainties?.find((hint) => hint.code === 'keine_berechtigung_maske')?.detail
    return noneDecision(detail || OPEN_REASON_NO_PERMISSION)
  }
  const openAction = item.actions.find((action) => action.key === 'open_mask')
  if (openAction?.enabled === false) {
    return noneDecision(OPEN_REASON_ACTION_DISABLED)
  }
  const kind = item.proposal.document_kind
  if (kind == null || kind === '') {
    return noneDecision(OPEN_REASON_UNKNOWN_KIND)
  }
  if (kind === 'EINGANGSRECHNUNG') {
    // Die Create-Maske lädt den Vorschlag anhand der Inbox-ID erneut vom Server.
    return documentDecision(
      withInboxPointer(INBOX_SUPPLIER_INVOICE_CREATE_ROUTE, item.id),
      true,
    )
  }
  if (kind === 'LIEFERSCHEIN') {
    const belegId = verifiedBelegId(item)
    return overviewDecision(INBOX_DELIVERY_NOTE_ROUTE, item.id, {
      href: '',
      enabled: false,
      reason: belegId ? OPEN_REASON_DELIVERY_NO_DETAIL : OPEN_REASON_NO_BELEG_ID,
    })
  }
  if (kind === 'GUTSCHRIFT') {
    const listRoute = creditListRoute(item.proposal.direction)
    if (!listRoute) {
      return noneDecision(OPEN_REASON_CREDIT_DIRECTION)
    }
    const belegId = verifiedBelegId(item)
    return overviewDecision(listRoute, item.id, {
      href: '',
      enabled: false,
      reason: belegId ? OPEN_REASON_CREDIT_NO_DETAIL : OPEN_REASON_NO_BELEG_ID,
    })
  }
  if (kind === 'WIEGESCHEIN') {
    const belegId = verifiedBelegId(item)
    return overviewDecision(INBOX_WEIGHING_LIST_ROUTE, item.id, {
      href: belegId
        ? `${INBOX_WEIGHING_DETAIL_ROUTE_PREFIX}/${encodeURIComponent(belegId)}`
        : '',
      enabled: Boolean(belegId),
      reason: belegId ? null : OPEN_REASON_NO_BELEG_ID,
    })
  }
  return noneDecision(`Keine Maske fuer Dokumentart ${kind}.`)
}

export function filterInboxQueue(
  items: readonly InboxQueueItem[],
  confidenceMin = 0,
): InboxQueueItem[] {
  return items.filter((item) => item.confidence >= confidenceMin)
}

export function inboxOpenHref(item: InboxQueueItem): string {
  return inboxOpenDecision(item).href
}

export function inboxPolicyRoute(policyId: string): string | null {
  try {
    return rewriteInboxTargetHref(getDocumentEntryPolicy(policyId as DocumentEntryPolicyId).targetRoute)
  } catch {
    return null
  }
}

export function assertInboxDoesNotBook(item: InboxQueueItem): void {
  if (item.booking_allowed) {
    throw new Error('Inbox darf keine Buchung erlauben.')
  }
  if (item.command.executable || item.command.booking || item.command.prefill.booking) {
    throw new Error('Inbox-Command darf nicht ausfuehrbar buchen.')
  }
  if (item.actions.some((action) => action.booking)) {
    throw new Error('Inbox-Aktion darf nicht buchen.')
  }
}

export function primaryInboxAction(item: InboxQueueItem): InboxAction | undefined {
  return item.actions.find((action) => action.kind === 'primary') ?? item.actions[0]
}

export function sortInboxQueue(items: readonly InboxQueueItem[]): InboxQueueItem[] {
  return [...items].sort((left, right) => {
    const band = BAND_RANK[left.confidence_band] - BAND_RANK[right.confidence_band]
    if (band !== 0) return band
    return left.confidence - right.confidence
  })
}

export function commandPrefillForMask(command: InboxCommand): Record<string, string> {
  return { ...command.prefill.matchValues }
}

export function prefillFromItem(item: InboxQueueItem): InboxPrefillPayload {
  return {
    ...item.command.prefill,
    schema: INBOX_PREFILL_SCHEMA,
    storageKey: INBOX_PREFILL_STORAGE_KEY,
    booking: false,
    maskConsumesPrefill: true,
  }
}

/** Clears pre-migration business data; navigation carries only the Inbox ID. */
export function clearInboxPrefill(): void {
  sessionStorage.removeItem(INBOX_PREFILL_STORAGE_KEY)
}

/** Only a freshly authorized prepare response may be used by the Create mask. */
export function checkedInvoicePrefill(response: { ok?: boolean; booking_allowed?: boolean; item?: InboxQueueItem }, itemId: string): InboxPrefillPayload {
  const item = response.item
  if (response.ok !== true || response.booking_allowed !== false || !item || item.id !== itemId ||
    item.proposal?.document_kind !== 'EINGANGSRECHNUNG' || item.proposal?.belegart !== 'purchase_invoice' ||
    item.can_open !== true || !item.actions?.some(action => action.key === 'open_mask' && action.enabled === true)) {
    throw new Error('Der vorbereitete Vorschlag passt nicht zur Eingangsrechnung oder darf nicht geöffnet werden.')
  }
  if (item.command?.prefill?.schema !== INBOX_PREFILL_SCHEMA) {
    throw new Error('Der Inbox-Vorschlag hat eine unbekannte Schema-Version.')
  }
  assertInboxDoesNotBook(item)
  const prefill = prefillFromItem(item)
  if (prefill.schema !== INBOX_PREFILL_SCHEMA || prefill.documentId !== itemId || prefill.source?.id !== itemId ||
    prefill.booking !== false) {
    throw new Error('Der Inbox-Vorschlag gehört nicht zum ausgewählten Dokument.')
  }
  return prefill
}

/** Maps inbox extraction onto DocFlow-Create fields of `beleg/purchase-invoice`. */
export function inboxPrefillToCreationValues(payload: InboxPrefillPayload): Record<string, unknown> {
  const values: Record<string, unknown> = {}
  const docNumber = payload.documentNumber || payload.matchValues.invoiceNumber
  if (docNumber) values.doc_number = docNumber
  const supplierId = payload.partner.id || payload.partner.number || payload.matchValues.supplierId
  if (supplierId) values.supplier_id = supplierId
  if (payload.matchValues.date) values.document_date = payload.matchValues.date
  if (payload.amounts.currency) values.currency = payload.amounts.currency
  const sourceRef = payload.documentNumber || payload.source.id
  if (sourceRef) values.source_ref = sourceRef
  return values
}
