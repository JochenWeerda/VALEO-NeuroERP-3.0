import { describe, expect, it } from 'vitest'
import {
  ADAPTIVE_WORKSPACE_INBOX_SCREEN,
  INBOX_DELIVERY_NOTE_ROUTE,
  INBOX_OPEN_DOCUMENT_ACTION_LABEL,
  INBOX_OVERVIEW_ACTION_LABEL,
  INBOX_PREFILL_SCHEMA,
  INBOX_PREFILL_STORAGE_KEY,
  INBOX_PURCHASE_CREDIT_LIST_ROUTE,
  INBOX_SALES_CREDIT_LIST_ROUTE,
  INBOX_SUPPLIER_INVOICE_CREATE_ROUTE,
  INBOX_WEIGHING_DETAIL_ROUTE_PREFIX,
  INBOX_WEIGHING_LIST_ROUTE,
  assertInboxDoesNotBook,
  checkedInvoicePrefill,
  clearInboxPrefill,
  commandPrefillForMask,
  filterInboxQueue,
  inboxOpenDecision,
  inboxOpenHref,
  inboxPolicyRoute,
  inboxPrefillToCreationValues,
  inboxScreenIssues,
  prefillFromItem,
  sortInboxQueue,
} from '@/components/adaptive-workspace/inbox'
import type { InboxPrefillPayload, InboxQueueItem } from '@/components/adaptive-workspace/inbox'

function samplePrefill(overrides: Partial<InboxPrefillPayload> = {}): InboxPrefillPayload {
  return {
    schema: INBOX_PREFILL_SCHEMA,
    documentId: 'INBOX-1',
    documentNumber: 'RE-1',
    partner: { id: 'L-10', number: 'L-10', name: 'Nordkorn AG', role: 'supplier' },
    amounts: { total: '1280.50', tax: '204.29', currency: 'EUR' },
    source: { kind: 'dms_inbox', id: 'INBOX-1', dmsDocumentId: 44, classification: 'parsed-or-ocr-hint' },
    confidence: 0.82,
    confidenceBand: 'high',
    policyId: 'incoming-supplier-invoice',
    documentType: 'supplier_invoice',
    targetRoute: '/einkauf/rechnung-eingang-erfassung',
    booking: false,
    matchValues: { invoiceNumber: 'RE-1', supplierName: 'Nordkorn AG', supplierId: 'L-10' },
    storageKey: INBOX_PREFILL_STORAGE_KEY,
    maskConsumesPrefill: true,
    ...overrides,
  }
}

function item(overrides: Partial<InboxQueueItem> = {}): InboxQueueItem {
  return {
    id: 'INBOX-1',
    status: 'pending',
    parsed_fields: { invoice_number: 'RE-1' },
    match_values: { invoiceNumber: 'RE-1', supplierName: 'Nordkorn AG' },
    confidence: 0.82,
    confidence_band: 'high',
    source: 'parsed-or-ocr-hint',
    proposal: {
      policy_id: 'incoming-supplier-invoice',
      label: 'Rechnungseingang erfassen',
      document_type: 'supplier_invoice',
      direction: 'incoming',
      target_route: '/einkauf/rechnung-eingang-erfassung',
      reason: 'test',
    },
    duplicates: [],
    blockers: [],
    actions: [
      {
        key: 'open_mask',
        label: 'Beleg öffnen',
        kind: 'primary',
        href: '/einkauf/rechnung-eingang-erfassung?inbox=INBOX-1',
        booking: false,
      },
    ],
    command: {
      command: 'document.capture.open',
      executable: false,
      booking: false,
      reason: 'keine Buchung',
      policy_id: 'incoming-supplier-invoice',
      document_type: 'supplier_invoice',
      target_route: '/einkauf/rechnung-eingang-erfassung',
      prefill: samplePrefill(),
      confidence: 0.82,
      confidence_band: 'high',
      blockers: [],
      source: { kind: 'dms_inbox', id: 'INBOX-1' },
      gaps: [],
    },
    booking_allowed: false,
    ...overrides,
  }
}

function withKind(kind: string | null): ReturnType<typeof item> {
  return item({
    proposal: {
      ...item().proposal,
      document_kind: kind,
      target_route: '/einkauf/rechnung-eingang-erfassung',
    },
    actions: [
      {
        key: 'open_mask',
        label: 'Beleg öffnen',
        kind: 'primary',
        href: '/einkauf/rechnung-eingang-erfassung?inbox=INBOX-1',
        enabled: true,
        booking: false,
      },
    ],
  })
}

describe('adaptive workspace inbox contract', () => {
  it('opens the purchase-invoice create host only for EINGANGSRECHNUNG', () => {
    expect(inboxPolicyRoute('incoming-supplier-invoice')).toBe(INBOX_SUPPLIER_INVOICE_CREATE_ROUTE)
    expect(inboxOpenHref(item())).toBe('')
    expect(inboxOpenDecision(item()).reason).toMatch(/nicht erkannt/)
    const invoice = inboxOpenDecision(withKind('EINGANGSRECHNUNG'))
    expect(invoice.href).toBe(`${INBOX_SUPPLIER_INVOICE_CREATE_ROUTE}?inbox=INBOX-1`)
    expect(invoice.mode).toBe('document')
    expect(invoice.actionLabel).toBe(INBOX_OPEN_DOCUMENT_ACTION_LABEL)
    expect(invoice.consumesPrefill).toBe(true)
    expect(invoice.actionLabel).not.toBe(INBOX_OVERVIEW_ACTION_LABEL)
  })

  it('routes LIEFERSCHEIN to overview without Prefill and keeps Beleg öffnen disabled', () => {
    const decision = inboxOpenDecision(withKind('LIEFERSCHEIN'))
    expect(decision.mode).toBe('overview')
    expect(decision.actionLabel).toBe(INBOX_OVERVIEW_ACTION_LABEL)
    expect(decision.href).toBe(`${INBOX_DELIVERY_NOTE_ROUTE}?inbox=INBOX-1`)
    expect(decision.consumesPrefill).toBe(false)
    expect(decision.href).not.toContain('rechnung-eingang')
    expect(decision.documentOpenEnabled).toBe(false)
    expect(decision.documentOpenReason).toMatch(/Beleg-ID/)

    const withId = withKind('LIEFERSCHEIN')
    withId.linked_document_id = 'LS-VERIFIED-1'
    const stillOverview = inboxOpenDecision(withId)
    expect(stillOverview.mode).toBe('overview')
    expect(stillOverview.actionLabel).toBe(INBOX_OVERVIEW_ACTION_LABEL)
    expect(stillOverview.documentOpenEnabled).toBe(false)
    expect(stillOverview.documentOpenReason).toMatch(/Detailroute/)
  })

  it('maps Gutschrift to direction-matched overview and keeps Beleg öffnen disabled without ID', () => {
    const incoming = withKind('GUTSCHRIFT')
    incoming.proposal = { ...incoming.proposal, direction: 'incoming' }
    const purchase = inboxOpenDecision(incoming)
    expect(purchase.mode).toBe('overview')
    expect(purchase.actionLabel).toBe(INBOX_OVERVIEW_ACTION_LABEL)
    expect(purchase.href).toBe(`${INBOX_PURCHASE_CREDIT_LIST_ROUTE}?inbox=INBOX-1`)
    expect(purchase.href).not.toContain('/sales/credit-notes')
    expect(purchase.consumesPrefill).toBe(false)
    expect(purchase.documentOpenEnabled).toBe(false)
    expect(purchase.documentOpenReason).toMatch(/Beleg-ID/)

    const outgoing = withKind('GUTSCHRIFT')
    outgoing.proposal = { ...outgoing.proposal, direction: 'outgoing' }
    const sales = inboxOpenDecision(outgoing)
    expect(sales.href).toBe(`${INBOX_SALES_CREDIT_LIST_ROUTE}?inbox=INBOX-1`)
    expect(sales.href).not.toContain('/einkauf/gutschriften')
    expect(sales.actionLabel).toBe(INBOX_OVERVIEW_ACTION_LABEL)
    expect(sales.documentOpenEnabled).toBe(false)
    expect(sales.documentOpenReason).toMatch(/Beleg-ID|Detailroute/)

    const withId = withKind('GUTSCHRIFT')
    withId.proposal = { ...withId.proposal, direction: 'outgoing' }
    withId.linked_document_id = 'CN-VERIFIED-1'
    const stillOverview = inboxOpenDecision(withId)
    expect(stillOverview.documentOpenEnabled).toBe(false)
    expect(stillOverview.documentOpenReason).toMatch(/Detailroute/)
    expect(stillOverview.actionLabel).not.toBe(INBOX_OPEN_DOCUMENT_ACTION_LABEL)
  })

  it('does not invent Zur Übersicht when Gutschrift has no direction', () => {
    for (const direction of [null, undefined, ''] as const) {
      const unclear = withKind('GUTSCHRIFT')
      unclear.proposal = { ...unclear.proposal, direction: direction as InboxQueueItem['proposal']['direction'] }
      const decision = inboxOpenDecision(unclear)
      expect(decision.mode).toBe('none')
      expect(decision.href).toBe('')
      expect(decision.actionLabel).toBe(INBOX_OPEN_DOCUMENT_ACTION_LABEL)
      expect(decision.actionLabel).not.toBe(INBOX_OVERVIEW_ACTION_LABEL)
      expect(decision.reason).toMatch(/Richtung/)
    }
  })

  it('opens Wiegeschein overview and enables Beleg öffnen only with verified Schein-ID', () => {
    const scale = inboxOpenDecision(withKind('WIEGESCHEIN'))
    expect(scale.mode).toBe('overview')
    expect(scale.actionLabel).toBe(INBOX_OVERVIEW_ACTION_LABEL)
    expect(scale.href).toBe(`${INBOX_WEIGHING_LIST_ROUTE}?inbox=INBOX-1`)
    expect(scale.documentOpenEnabled).toBe(false)
    expect(scale.documentOpenReason).toMatch(/Beleg-ID/)

    const withId = withKind('WIEGESCHEIN')
    withId.linked_document_id = 'WS-VERIFIED-9'
    const open = inboxOpenDecision(withId)
    expect(open.href).toBe(`${INBOX_WEIGHING_LIST_ROUTE}?inbox=INBOX-1`)
    expect(open.documentOpenEnabled).toBe(true)
    expect(open.documentOpenHref).toBe(`${INBOX_WEIGHING_DETAIL_ROUTE_PREFIX}/WS-VERIFIED-9`)
    expect(open.documentOpenReason).toBeNull()

    expect(inboxOpenHref(withKind('SONSTIGES'))).toBe('')
    expect(inboxOpenDecision(withKind(null)).href).toBe('')
    expect(inboxOpenDecision(withKind(null)).reason).toMatch(/nicht erkannt/)
  })

  it('keeps can_open mandatory even for a known kind', () => {
    const blocked = withKind('EINGANGSRECHNUNG')
    blocked.can_open = false
    expect(inboxOpenHref(blocked)).toBe('')
    expect(inboxOpenDecision(blocked).consumesPrefill).toBe(false)
  })

  it('enables Zur Übersicht for LIEFERSCHEIN only when can_open is true', () => {
    const blocked = withKind('LIEFERSCHEIN')
    blocked.can_open = false
    const blockedDecision = inboxOpenDecision(blocked)
    expect(blockedDecision.mode).toBe('none')
    expect(blockedDecision.actionLabel).not.toBe(INBOX_OVERVIEW_ACTION_LABEL)
    expect(blockedDecision.href).toBe('')

    const open = inboxOpenDecision(withKind('LIEFERSCHEIN'))
    expect(open.mode).toBe('overview')
    expect(open.actionLabel).toBe(INBOX_OVERVIEW_ACTION_LABEL)
    expect(open.href).toBe(`${INBOX_DELIVERY_NOTE_ROUTE}?inbox=INBOX-1`)
    expect(open.documentOpenEnabled).toBe(false)
  })

  it('maps prefill onto DocFlow-Create fields without booking', () => {
    expect(inboxPrefillToCreationValues(samplePrefill())).toEqual({
      doc_number: 'RE-1',
      supplier_id: 'L-10',
      currency: 'EUR',
      source_ref: 'RE-1',
    })
  })

  it('keeps only a pointer for navigation and clears legacy stored business data', () => {
    sessionStorage.clear()
    const payload = prefillFromItem(item())
    expect(payload.documentId).toBe('INBOX-1')
    expect(payload.partner.name).toBe('Nordkorn AG')
    expect(payload.amounts.total).toBe('1280.50')
    expect(payload.source.kind).toBe('dms_inbox')
    expect(payload.confidence).toBe(0.82)
    expect(payload.booking).toBe(false)
    expect(payload.maskConsumesPrefill).toBe(true)
    expect(commandPrefillForMask(item().command).supplierId).toBe('L-10')
    sessionStorage.setItem(INBOX_PREFILL_STORAGE_KEY, JSON.stringify(payload))
    clearInboxPrefill()
    expect(sessionStorage.getItem(INBOX_PREFILL_STORAGE_KEY)).toBeNull()
    const prepared = withKind('EINGANGSRECHNUNG')
    prepared.proposal.belegart = 'purchase_invoice'
    prepared.can_open = true
    expect(checkedInvoicePrefill({ ok: true, booking_allowed: false, item: prepared }, 'INBOX-1')).toMatchObject({ documentId: 'INBOX-1' })
    expect(() => checkedInvoicePrefill({ ok: true, booking_allowed: false, item: prepared }, 'OTHER')).toThrow()
    const oldSchema = structuredClone(prepared)
    oldSchema.command.prefill.schema = 'valeo.inbox.prefill.v0' as typeof INBOX_PREFILL_SCHEMA
    expect(() => checkedInvoicePrefill({ ok: true, booking_allowed: false, item: oldSchema }, 'INBOX-1')).toThrow(/Schema-Version/)
  })

  it('filters by confidence and sorts review first', () => {
    const queued = [
      item({ id: 'a', confidence: 0.9, confidence_band: 'high' }),
      item({ id: 'b', confidence: 0.1, confidence_band: 'review' }),
    ]
    expect(filterInboxQueue(queued, 0.5).map((entry) => entry.id)).toEqual(['a'])
    expect(sortInboxQueue(queued).map((entry) => entry.id)).toEqual(['b', 'a'])
  })

  it('rejects a booking command', () => {
    expect(() =>
      assertInboxDoesNotBook(
        item({
          command: {
            ...item().command,
            executable: true,
            booking: true,
          },
        }),
      ),
    ).toThrow(/nicht ausfuehrbar buchen/)
  })

  it('keeps master_data_proposals non-booking when present on the queue item', () => {
    const queued = item({
      master_data_proposals: {
        booking: false,
        executable: false,
        line_item_count: 0,
        supplier: {
          kind: 'supplier_create',
          status: 'propose',
          booking: false,
          executable: false,
          domain_api: 'POST /api/v1/einkauf/lieferanten',
          target_route: '/einkauf/lieferanten',
          reason: 'test',
          payload: { firmenname: 'Neue Muehle GmbH' },
        },
        articles: [
          {
            kind: 'article_create',
            status: 'blocked',
            booking: false,
            executable: false,
            code: 'keine_positionszeilen_im_extrakt',
            detail: 'keine Positionen',
          },
        ],
      },
    })
    assertInboxDoesNotBook(queued)
    expect(queued.master_data_proposals?.booking).toBe(false)
    expect(queued.master_data_proposals?.executable).toBe(false)
    expect(queued.master_data_proposals?.supplier?.payload.firmenname).toBe('Neue Muehle GmbH')
  })

  it('exposes a valid worklist ScreenDefinition without a booking command', () => {
    expect(inboxScreenIssues()).toEqual([])
    expect(ADAPTIVE_WORKSPACE_INBOX_SCREEN.layout?.floorplan).toBe('worklist')
    expect(ADAPTIVE_WORKSPACE_INBOX_SCREEN.agentContract?.forbiddenAgentTasks).toContain('Beleg buchen')
    expect(ADAPTIVE_WORKSPACE_INBOX_SCREEN.actions?.some((action) => action.key === 'open_mask')).toBe(true)
    expect(
      ADAPTIVE_WORKSPACE_INBOX_SCREEN.actions?.some((action) => action.commandBinding?.command === 'post'),
    ).toBe(false)
  })
})
