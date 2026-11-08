import { describe, expect, it } from 'vitest'
import {
  inboxOpenDecision,
  situationalItemsFromInboxQueue,
  type InboxQueueItem,
  type InboxQueueSnapshot,
} from '@/components/adaptive-workspace/inbox'
import {
  WORKSPACE_FACHAKTIONEN,
  emptyUserContext,
  rankWorkspaceItems,
  signalFromIstEvent,
  signalsFromQueueCounts,
} from '@/workspace'
import { defaultHomeSignals } from '@/workspace/home-signals'
import type { WorkspaceSignal } from '@/workspace/types'

function item(overrides: Partial<InboxQueueItem> = {}): InboxQueueItem {
  const base = {
    id: 'INBOX-9',
    status: 'pending',
    parsed_fields: {},
    match_values: {},
    confidence: 0.4,
    confidence_band: 'low',
    source: 'test',
    proposal: {
      policy_id: 'incoming-supplier-invoice',
      label: 'Rechnungseingang erfassen',
      document_type: 'supplier_invoice',
      document_kind: 'EINGANGSRECHNUNG',
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
        enabled: true,
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
      prefill: { booking: false },
      confidence: 0.4,
      confidence_band: 'low',
      blockers: [],
      source: { kind: 'dms_inbox', id: 'INBOX-9' },
      gaps: [],
    },
    can_open: true,
    booking_allowed: false,
  }
  return { ...base, ...overrides, proposal: { ...base.proposal, ...overrides.proposal } } as InboxQueueItem
}

function ready(items: InboxQueueItem[]): InboxQueueSnapshot {
  return { status: 'ready', items }
}

describe('situative Inbox-Signale', () => {
  const invoice = item()
  const delivery = item({
    id: 'INBOX-LS',
    proposal: {
      policy_id: 'incoming-delivery-note',
      label: 'Lieferschein oeffnen',
      document_type: 'delivery_note',
      document_kind: 'LIEFERSCHEIN',
      direction: 'incoming',
      target_route: '/einkauf/rechnung-eingang-erfassung',
      reason: 'lieferschein',
    },
  })
  const credit = item({
    id: 'INBOX-G',
    proposal: {
      ...item().proposal,
      document_kind: 'GUTSCHRIFT',
      direction: 'outgoing',
      label: 'Gutschrift',
    },
  })
  const scale = item({
    id: 'INBOX-W',
    proposal: { ...item().proposal, document_kind: 'WIEGESCHEIN', label: 'Wiegeschein' },
  })
  const unknown = item({
    id: 'INBOX-0',
    proposal: { ...item().proposal, document_kind: null, label: 'Ohne Art' },
  })
  const blocked = item({
    id: 'INBOX-X',
    can_open: false,
    proposal: { ...item().proposal, label: 'Gesperrt' },
  })

  it('gibt oeffenbare Zeilen auf der inboxOpenDecision-Route in die Rangliste', () => {
    const now = new Date('2026-10-22T08:00:00')
    const work = situationalItemsFromInboxQueue(
      ready([invoice, delivery, credit, scale, unknown, blocked, invoice]),
    )
    expect(work.actions.map((action) => [action.id, action.kind, action.target.route])).toEqual([
      ['inbox.queue.INBOX-9', 'navigate', inboxOpenDecision(invoice).href],
      ['inbox.queue.INBOX-LS', 'navigate', inboxOpenDecision(delivery).href],
      ['inbox.queue.INBOX-G', 'navigate', inboxOpenDecision(credit).href],
      ['inbox.queue.INBOX-W', 'navigate', inboxOpenDecision(scale).href],
    ])
    expect(work.actions[0]?.target.route).toBe('/belege/purchase_invoice/neu?inbox=INBOX-9')
    // Document/Erfassung: Rangliste nutzt proposal.label; Widget-Button = actionLabel.
    expect(work.actions[0]?.label).toBe('Rechnungseingang erfassen')
    expect(work.actions[1]?.target.route).toBe('/einkauf/lieferschein-erfassung?inbox=INBOX-LS')
    expect(work.actions[1]?.label).toBe('Zur Übersicht')
    expect(work.actions[2]?.target.route).toBe('/sales/credit-notes?inbox=INBOX-G')
    expect(work.actions[2]?.label).toBe('Zur Übersicht')
    expect(work.actions[3]?.target.route).toBe('/weighing?inbox=INBOX-W')
    expect(work.actions[3]?.label).toBe('Zur Übersicht')
    expect(inboxOpenDecision(invoice).mode).toBe('document')
    expect(inboxOpenDecision(invoice).actionLabel).toBe('Beleg öffnen')
    expect(inboxOpenDecision(invoice).consumesPrefill).toBe(true)
    expect(inboxOpenDecision(delivery).mode).toBe('overview')
    expect(inboxOpenDecision(delivery).actionLabel).toBe('Zur Übersicht')
    expect(inboxOpenDecision(delivery).consumesPrefill).toBe(false)
    expect(inboxOpenDecision(delivery).documentOpenEnabled).toBe(false)
    expect(inboxOpenDecision(credit).consumesPrefill).toBe(false)
    expect(inboxOpenDecision(credit).actionLabel).toBe('Zur Übersicht')
    expect(inboxOpenDecision(scale).consumesPrefill).toBe(false)
    expect(inboxOpenDecision(scale).documentOpenEnabled).toBe(false)
    expect(work.signals.map((signal) => signal.relatedActionIds[0])).toEqual([
      'inbox.queue.INBOX-9',
      'inbox.queue.INBOX-LS',
      'inbox.queue.INBOX-G',
      'inbox.queue.INBOX-W',
    ])
    expect(work.actions.every((action) => action.mcpIntent === 'navigate')).toBe(true)
    expect(JSON.stringify(work)).not.toMatch(/approve/i)
    expect(work.actions.some((action) => action.kind !== 'navigate')).toBe(false)

    const ranked = rankWorkspaceItems({
      actions: [...WORKSPACE_FACHAKTIONEN, ...work.actions],
      context: emptyUserContext({
        scopes: WORKSPACE_FACHAKTIONEN.flatMap((action) => action.requiredScopes),
        pinned: ['workspace.document-inbox'],
      }),
      signals: [
        ...defaultHomeSignals(now),
        ...signalsFromQueueCounts({ inbox: 2 }),
        ...work.signals,
      ],
      now,
    }).slice(0, 8)

    expect(ranked[0]?.action.id).toBe('workspace.document-inbox')
    expect(ranked[0]?.reasonCodes).toContain('pinned')
    const row = ranked.find((entry) => entry.action.id === 'inbox.queue.INBOX-9')
    expect(row?.reasonCodes).toEqual(
      expect.arrayContaining(['layer:situational', 'signal:open-task', 'severity:3']),
    )
    expect(row?.reasonCodes).not.toContain('pinned')
    expect((ranked[0]?.score ?? 0) > (row?.score ?? 0)).toBe(true)
    const note = ranked.find((entry) => entry.action.id === 'inbox.queue.INBOX-LS')
    expect(note?.action.target.route).toBe('/einkauf/lieferschein-erfassung?inbox=INBOX-LS')
    expect(ranked.find((entry) => entry.action.id === 'inbox.queue.INBOX-G')?.action.target.route).toBe(
      '/sales/credit-notes?inbox=INBOX-G',
    )
    expect(ranked.find((entry) => entry.action.id === 'inbox.queue.INBOX-W')?.action.target.route).toBe(
      '/weighing?inbox=INBOX-W',
    )
    expect(ranked.some((entry) => /INBOX-0|INBOX-X/.test(entry.action.id))).toBe(false)
  })

  it('blendet leere Queue, 401 und Fehler aus und doppelt kein Live-Signal', () => {
    expect(situationalItemsFromInboxQueue({ status: 'empty', items: [] })).toEqual({
      actions: [],
      signals: [],
    })
    expect(situationalItemsFromInboxQueue({ status: 'hidden', items: [invoice] })).toEqual({
      actions: [],
      signals: [],
    })
    expect(situationalItemsFromInboxQueue({ status: 'error', items: [invoice] })).toEqual({
      actions: [],
      signals: [],
    })
    expect(situationalItemsFromInboxQueue({ status: 'pending', items: [] })).toEqual({
      actions: [],
      signals: [],
    })

    const live: WorkspaceSignal = {
      id: 'inbox:INBOX-9',
      kind: 'open-task',
      layer: 'situational',
      relatedActionIds: ['inbox.queue.INBOX-9'],
      severity: 3,
      source: 'sse:inbox-row',
    }
    const counted = situationalItemsFromInboxQueue(ready([invoice, delivery]), [live])
    expect(counted.signals.map((signal) => signal.id)).toEqual(['inbox:INBOX-LS'])
    expect(counted.actions.map((action) => action.id)).toEqual([
      'inbox.queue.INBOX-9',
      'inbox.queue.INBOX-LS',
    ])

    const ranked = rankWorkspaceItems({
      actions: counted.actions,
      context: emptyUserContext(),
      signals: [live, ...counted.signals],
      now: new Date('2026-10-22T08:00:00'),
    })
    expect(ranked.filter((entry) => entry.action.id === 'inbox.queue.INBOX-9')).toHaveLength(1)
    expect(ranked.find((entry) => entry.action.id === 'inbox.queue.INBOX-9')?.reasonCodes).toContain(
      'signal:open-task',
    )

    const aggregate = situationalItemsFromInboxQueue(
      ready([invoice]),
      [
        ...signalsFromQueueCounts({ inbox: 1 }),
        signalFromIstEvent('docflow.document.posted')!,
      ],
    )
    expect(aggregate.actions).toHaveLength(1)
    expect(aggregate.signals).toHaveLength(1)

    const booking = item({
      command: {
        ...item().command,
        executable: true,
        booking: true,
      } as InboxQueueItem['command'],
    })
    expect(situationalItemsFromInboxQueue(ready([booking])).actions).toEqual([])
  })

  it('haengt vorhandene Pruefcodes an die Handlungsbedarf-Zeile', () => {
    const plain = item({ id: 'INBOX-A' })
    const marked = item({
      id: 'INBOX-B',
      duplicates: [{ doc_type: 'purchase_order', doc_number: 'RE-9' }],
      uncertainties: [
        { code: 'pflicht_invoice_number', detail: 'Pflichtfeld invoice_number fehlt im Extrakt.' },
        { code: 'dublette', detail: 'Belegnummer existiert bereits im Dokumentspeicher des Mandanten.' },
        { code: 'keine_berechtigung_maske', detail: 'Keine Berechtigung: Belegart purchase_invoice bearbeiten.' },
      ],
    })
    const duplicatesOnly = item({
      id: 'INBOX-D',
      duplicates: [{ doc_type: 'purchase_order', doc_number: 'RE-1' }],
    })
    const fromCommand = item({
      id: 'INBOX-C',
      command: {
        ...item().command,
        uncertainties: [{ code: 'pflicht_date', detail: 'Pflichtfeld date fehlt im Extrakt.' }],
      } as InboxQueueItem['command'],
    })
    const blockedWithCode = item({
      id: 'INBOX-X2',
      can_open: false,
      uncertainties: [{ code: 'keine_berechtigung_maske', detail: 'Keine Berechtigung.' }],
    })

    const work = situationalItemsFromInboxQueue(
      ready([plain, marked, duplicatesOnly, fromCommand, blockedWithCode]),
    )
    expect(work.actions.map((action) => action.id)).toEqual([
      'inbox.queue.INBOX-A',
      'inbox.queue.INBOX-B',
      'inbox.queue.INBOX-D',
      'inbox.queue.INBOX-C',
    ])
    expect(work.signals.find((signal) => signal.id === 'inbox:INBOX-B')?.reasonCodes).toEqual([
      'pflicht_invoice_number',
      'dublette',
      'keine_berechtigung_maske',
    ])
    expect(work.signals.find((signal) => signal.id === 'inbox:INBOX-A')?.reasonCodes).toBeUndefined()
    expect(JSON.stringify(work)).not.toMatch(/approve/i)

    const now = new Date('2026-10-22T08:00:00')
    const ranked = rankWorkspaceItems({
      actions: work.actions,
      context: emptyUserContext(),
      signals: work.signals,
      now,
    })
    const plainRow = ranked.find((entry) => entry.action.id === 'inbox.queue.INBOX-A')
    const markedRow = ranked.find((entry) => entry.action.id === 'inbox.queue.INBOX-B')
    const duplicateRow = ranked.find((entry) => entry.action.id === 'inbox.queue.INBOX-D')
    const commandRow = ranked.find((entry) => entry.action.id === 'inbox.queue.INBOX-C')

    expect(markedRow?.score).toBe(plainRow?.score)
    expect(markedRow?.reasonCodes).toEqual([
      'layer:situational',
      'signal:open-task',
      'severity:3',
      'pflicht_invoice_number',
      'dublette',
      'keine_berechtigung_maske',
    ])
    expect(duplicateRow?.reasonCodes).toEqual([
      'layer:situational',
      'signal:open-task',
      'severity:3',
      'dublette',
    ])
    expect(commandRow?.reasonCodes).toContain('pflicht_date')
    expect(plainRow?.reasonCodes).toEqual(['layer:situational', 'signal:open-task', 'severity:3'])
    expect(ranked.some((entry) => entry.action.id === 'inbox.queue.INBOX-X2')).toBe(false)
  })
})
