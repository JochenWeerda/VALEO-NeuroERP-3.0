import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { load as loadYaml } from 'js-yaml'
import { describe, expect, it } from 'vitest'
import { situationalItemsFromInboxQueue, type InboxQueueItem } from '@/components/adaptive-workspace/inbox'
import { dispositionBoardScreen } from '@/components/mask-builder/specialized/disposition-board-screen'
import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import {
  saveWorkspaceCompositionSession,
  setSpecializedKindEnabled,
} from '@/studio/workspace-composition-session'
import {
  OPEN_ABRUF_ACTION_ID,
  WORKSPACE_FACHAKTIONEN,
  emptyUserContext,
  getFachaktion,
  mapFachaktionToCommand,
  rankWorkspaceItems,
  resolveHomeSpecialistKinds,
  signalFromIstEvent,
  signalFromOpenAbrufe,
  signalsForHomeSpecialists,
  signalsFromQueueCounts,
} from '@/workspace'
import { resolveFachaktionLive } from '@/workspace/fachaktion-resolve'
import { requestExistingCommandPalette } from '@/workspace/request-command-palette'

const HERE = dirname(fileURLToPath(import.meta.url))
const DISPOSITION_PAGE = resolve(HERE, '../../pages/disposition/touren-disposition.tsx')
const ROUTE_TREE = resolve(HERE, '../../app/routing/route-tree.gen.tsx')

function memoryStorage(): Storage {
  const map = new Map<string, string>()
  return {
    get length() {
      return map.size
    },
    clear: () => map.clear(),
    getItem: (key: string) => map.get(key) ?? null,
    key: (index: number) => [...map.keys()][index] ?? null,
    removeItem: (key: string) => {
      map.delete(key)
    },
    setItem: (key: string, value: string) => {
      map.set(key, value)
    },
  }
}

function invoiceWithApproveHref(): InboxQueueItem {
  const approveHref = '/api/mcp/documents/inbox/INBOX-9/approve'
  return {
    id: 'INBOX-9',
    status: 'pending',
    parsed_fields: {},
    match_values: {},
    confidence: 0.8,
    confidence_band: 'high',
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
        href: '/einkauf/rechnung-eingang-erfassung',
        enabled: true,
        booking: false,
      },
      {
        key: 'approve',
        label: 'Freigeben',
        kind: 'secondary',
        href: approveHref,
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
      prefill: {
        schema: 'valeo.inbox.prefill.v1',
        documentId: 'INBOX-9',
        partner: { role: 'supplier' },
        amounts: { currency: 'EUR' },
        source: { kind: 'dms_inbox', id: 'INBOX-9' },
        confidence: 0.8,
        confidenceBand: 'high',
        policyId: 'incoming-supplier-invoice',
        documentType: 'supplier_invoice',
        targetRoute: '/einkauf/rechnung-eingang-erfassung',
        booking: false,
        matchValues: {},
        storageKey: 'valeo.inbox.prefill',
        maskConsumesPrefill: true,
      },
      confidence: 0.8,
      confidence_band: 'high',
      blockers: [{ code: 'booking_not_from_inbox', detail: 'Approve bleibt 409.' }],
      source: { kind: 'dms_inbox', id: 'INBOX-9' },
      gaps: [],
    },
    can_open: true,
    booking_allowed: false,
  }
}

describe('Workspace-Invarianten', () => {
  it('bereitet prepare-command vor und submitted den Katalog nicht', () => {
    const prepare = WORKSPACE_FACHAKTIONEN.filter((action) => action.kind === 'prepare-command')
    expect(prepare.length).toBeGreaterThan(0)
    for (const action of prepare) {
      const command = mapFachaktionToCommand(action)
      expect(command.hint).toBe('vorbereiten')
      expect(String(command.actionParams.path)).toContain(`omniboxAction=${action.target.actionKey}`)
      expect(JSON.stringify(command)).not.toMatch(/autoSubmit|auto-submit/)
    }
    expect(resolveFachaktionLive.toString()).toMatch(/mode:\s*['"]dryRun['"]/)
    expect(resolveFachaktionLive.toString()).not.toMatch(/autoSubmit|auto-submit/)
    expect(requestExistingCommandPalette.toString()).not.toMatch(/\.submit\(|autoSubmit/)
  })

  it('nimmt den Approve-Pfad nicht in die Rangliste', () => {
    const approveHref = '/api/mcp/documents/inbox/INBOX-9/approve'
    const work = situationalItemsFromInboxQueue({
      status: 'ready',
      items: [invoiceWithApproveHref()],
    })
    expect(work.actions.map((action) => action.target.route)).toEqual([
      '/belege/purchase_invoice/neu?inbox=INBOX-9',
    ])
    expect(work.actions.every((action) => action.kind === 'navigate')).toBe(true)
    expect(JSON.stringify(work)).not.toContain(approveHref)
    expect(JSON.stringify(work)).not.toMatch(/\/approve(?:\/|$|\?)/)

    const ranked = rankWorkspaceItems({
      actions: work.actions,
      context: emptyUserContext(),
      signals: work.signals,
      now: new Date('2026-10-22T08:00:00'),
    })
    expect(ranked).toHaveLength(1)
    expect(ranked[0]?.action.target.route).not.toMatch(/\/approve(?:\/|$|\?)/)
    expect(ranked[0]?.action.id).toBe('inbox.queue.INBOX-9')
  })

  it('setzt posts_quantity im Dispo-Signal nicht auf true und haengt keinen Status-Query an', () => {
    const action = getFachaktion(OPEN_ABRUF_ACTION_ID)
    expect(action?.target.route).toBe('/disposition/touren-disposition')
    expect(action?.target.worklistQuery).toBeUndefined()
    const signal = signalFromOpenAbrufe([{ id: 'a1' }, { id: 'a2' }])
    expect(signal?.source).toBe('disposition:open-abrufe')
    expect(JSON.stringify(signal)).not.toMatch(/"posts_quantity"\s*:\s*true/)
    const command = mapFachaktionToCommand(action!)
    expect(command.actionParams.path).toBe('/disposition/touren-disposition')
    expect(String(command.actionParams.path)).not.toContain('status=undispatched')
    expect(JSON.stringify(command)).not.toMatch(/"posts_quantity"\s*:\s*true/)
  })

  it('lässt LOADING_* keine Mengenbuchung auslösen und verlangt ops:verladung reasonCodes', () => {
    for (const istType of ['LOADING_STARTED', 'LOADING_FINISHED'] as const) {
      const signal = signalFromIstEvent(istType)
      expect(signal).toBeTruthy()
      expect(signal?.relatedActionIds).toEqual([OPEN_ABRUF_ACTION_ID])
      expect(signal?.reasonCodes).toEqual(['ops:verladung', `ist:${istType}`])
      expect(JSON.stringify(signal)).not.toMatch(/"posts_quantity"\s*:\s*true/)
      expect(JSON.stringify(signal)).not.toMatch(/quantity_posted|Mengenbuchung/)
    }
    const action = getFachaktion(OPEN_ABRUF_ACTION_ID)
    expect(JSON.stringify(mapFachaktionToCommand(action!))).not.toMatch(/"posts_quantity"\s*:\s*true/)
  })

  it('blendet Inbox-Signale ohne inbox und offene Abrufe ohne disposition_board aus', () => {
    const storage = memoryStorage()
    const inboxRow = { id: 'inbox-row', source: 'inbox-queue' }
    const inboxCount = signalsFromQueueCounts({ inbox: 2 })[0]
    const abrufe = signalFromOpenAbrufe([{ id: 'a1' }])
    const calendar = { id: 'cal-season', source: 'calendar' }
    expect(inboxCount && abrufe).toBeTruthy()
    const all = [inboxRow, inboxCount!, abrufe!, calendar]

    const inboxOnly = setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'disposition_board', false)
    expect(saveWorkspaceCompositionSession(inboxOnly, storage).ok).toBe(true)
    const withoutBoard = signalsForHomeSpecialists(all, resolveHomeSpecialistKinds(storage))
    expect(withoutBoard.map((signal) => signal.id)).toEqual(['inbox-row', inboxCount!.id, 'cal-season'])
    expect(withoutBoard.some((signal) => signal.source === 'disposition:open-abrufe')).toBe(false)

    const boardOnly = setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'inbox', false)
    expect(saveWorkspaceCompositionSession(boardOnly, storage).ok).toBe(true)
    const withoutInbox = signalsForHomeSpecialists(all, resolveHomeSpecialistKinds(storage))
    expect(withoutInbox.map((signal) => signal.source)).toEqual(['disposition:open-abrufe', 'calendar'])
    expect(withoutInbox.some((signal) => signal.source === 'inbox-queue' || signal.source === 'queue:inbox')).toBe(false)
  })

  it('haengt Touren-Disposition an ScreenDefinition→RenderPlan→useUniversalMaskRuntime→UniversalMaskRenderer mit disposition_board', () => {
    const page = readFileSync(DISPOSITION_PAGE, 'utf8')
    expect(page).toContain('UniversalNativeCockpitPage')
    expect(page).toContain("'disposition/touren-disposition'")
    expect(dispositionBoardScreen.id).toBe('disposition/touren-disposition')
    expect(dispositionBoardScreen.specialized?.type).toBe('disposition_board')

    const routeTree = readFileSync(ROUTE_TREE, 'utf8')
    expect(routeTree).toContain('path: "disposition/touren-disposition"')
    expect(routeTree).toContain('renderPage("@/pages/disposition/touren-disposition")')
  })

  it('hat richtungsgetrennte Gutschrift-Uebersichten und Wiegeschein-/Lieferschein-Liste ohne Beleg-ID', () => {
    const sales = getFachaktion('sales.credit-notes-list')
    expect(sales?.catalogId).toBe('sales.credit_note.list')
    expect(sales?.target.route).toBe('/sales/credit-notes')
    expect(sales?.target.route).not.toMatch(/:[a-z]+/i)

    const purchase = getFachaktion('einkauf.gutschriften-list')
    expect(purchase?.catalogId).toBe('einkauf.gutschrift.list')
    expect(purchase?.target.route).toBe('/einkauf/gutschriften-belastungen')
    expect(purchase?.target.route).not.toBe(sales?.target.route)

    const weighing = getFachaktion('weighing.tickets-list')
    expect(weighing?.catalogId).toBe('weighing.tickets.list')
    expect(weighing?.target.route).toBe('/weighing')
    expect(weighing?.target.route).not.toContain('/waage/wiegeschein/')
    expect(JSON.stringify(mapFachaktionToCommand(weighing!))).not.toMatch(/"posts_quantity"\s*:\s*true/)

    const delivery = getFachaktion('einkauf.lieferschein-list')
    expect(delivery?.catalogId).toBe('einkauf.lieferschein.list')
    expect(delivery?.target.route).toBe('/einkauf/lieferschein-erfassung')
    expect(delivery?.target.route).not.toMatch(/:[a-z]+/i)
  })

  it('haelt catalogId 1:1 an YAML action_id und route_path fuer Inbox-Uebersichts-Actions', () => {
    const yamlPath = resolve(
      dirname(fileURLToPath(import.meta.url)),
      '../../../../../config/adaptive_workspace_fachaktionen.yaml',
    )
    const catalog = loadYaml(readFileSync(yamlPath, 'utf8')) as {
      actions: Array<{ action_id: string; route_path?: string | null }>
    }
    const expected: Array<[string, string, string]> = [
      ['sales.credit-notes-list', 'sales.credit_note.list', '/sales/credit-notes'],
      ['einkauf.gutschriften-list', 'einkauf.gutschrift.list', '/einkauf/gutschriften-belastungen'],
      ['weighing.tickets-list', 'weighing.tickets.list', '/weighing'],
      ['einkauf.lieferschein-list', 'einkauf.lieferschein.list', '/einkauf/lieferschein-erfassung'],
    ]
    for (const [localId, catalogId, route] of expected) {
      const yamlAction = catalog.actions.find((action) => action.action_id === catalogId)
      expect(yamlAction, catalogId).toBeTruthy()
      expect(yamlAction?.route_path).toBe(route)
      const local = getFachaktion(localId)
      expect(local?.catalogId).toBe(catalogId)
      expect(local?.catalogId).toBe(yamlAction?.action_id)
      expect(local?.target.route).toBe(yamlAction?.route_path)
    }
  })

  it('haelt die fuenf Beispiel-Queries YAML↔Registry (catalogId, route, scope)', () => {
    const yamlPath = resolve(
      dirname(fileURLToPath(import.meta.url)),
      '../../../../../config/adaptive_workspace_fachaktionen.yaml',
    )
    const catalog = loadYaml(readFileSync(yamlPath, 'utf8')) as {
      actions: Array<{
        action_id: string
        route_path?: string | null
        permission?: { scope?: string }
      }>
    }
    const examples: Array<[string, string, string]> = [
      ['logistics.undispatched-truck-orders', 'logistik.undispatched_vehicles.list', 'logistics:read'],
      ['agrar.overdue-contracts', 'agrar.contract.overdue.list', 'agrar:read'],
      ['sales.customer-quotes-list', 'sales.customer_quote.list', 'sales:read'],
      ['procurement.goods-receipt-qty-variance', 'einkauf.goods_receipt.quantity_variance.list', 'einkauf:read'],
      ['finance.invoices-awaiting-my-approval', 'finance.ap_invoice.approval.worklist', 'finance:read'],
    ]
    for (const [localId, catalogId, scope] of examples) {
      const yamlAction = catalog.actions.find((action) => action.action_id === catalogId)
      expect(yamlAction, catalogId).toBeTruthy()
      expect(yamlAction?.permission?.scope).toBe(scope)
      const local = getFachaktion(localId)
      expect(local?.catalogId).toBe(catalogId)
      expect(local?.requiredScopes).toEqual([scope])
      expect(local?.target.route).toBe(yamlAction?.route_path)
      expect(local?.target.route).toMatch(/^\//)
      expect(local?.target.route.includes('/api/')).toBe(false)
    }
  })
})
