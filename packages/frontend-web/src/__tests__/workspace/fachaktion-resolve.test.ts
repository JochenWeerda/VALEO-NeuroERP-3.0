import { AxiosError } from 'axios'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { apiClient } from '@/lib/api-client'
import { WORKSPACE_FACHAKTIONEN } from '@/workspace'
import {
  FACHAKTION_MCP_CALL_PATH,
  FACHAKTION_RESOLVE_TOOL,
  consumeResolvedFachaktion,
  findLocalByCatalogId,
  isLiveResolveUnavailable,
  localResolveFallback,
  resolveCatalogIdFromCommand,
  resolveFachaktionCommand,
  shouldBlockClientExecution,
} from '@/workspace/fachaktion-resolve'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}))

describe('fachaktion live resolve', () => {
  beforeEach(() => {
    vi.mocked(apiClient.post).mockReset()
  })

  it('mappt YAML-action_id 1:1 auf den lokalen catalogId-Alias', () => {
    expect(findLocalByCatalogId('harvest.intake-queue')?.id).toBe('harvest.intake-queue')
    expect(findLocalByCatalogId('workspace.document-inbox')?.id).toBe('workspace.document-inbox')
    expect(findLocalByCatalogId('logistik.undispatched_vehicles.list')?.id).toBe(
      'logistics.undispatched-truck-orders',
    )
    expect(WORKSPACE_FACHAKTIONEN.every((action) => Boolean(action.catalogId))).toBe(true)
  })

  it('konsumiert live resolve und faellt bei 401 auf den lokalen Katalog zurueck', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        action_id: 'harvest.intake-queue',
        authorized: true,
        executable: true,
        four_eyes: false,
        access: 'read',
        reason: 'ok',
      },
    } as never)

    const live = await resolveFachaktionCommand('harvest.intake-queue')
    expect(apiClient.post).toHaveBeenCalledWith(FACHAKTION_MCP_CALL_PATH, {
      tool_name: FACHAKTION_RESOLVE_TOOL,
      parameters: { command: 'harvest.intake-queue' },
      mode: 'dryRun',
    })
    expect(live).toMatchObject({
      source: 'live',
      action: { catalogId: 'harvest.intake-queue', kind: 'navigate' },
    })

    vi.mocked(apiClient.post).mockRejectedValue(
      new AxiosError('Unauthorized', 'ERR_BAD_REQUEST', undefined, undefined, {
        status: 401,
        statusText: 'Unauthorized',
        data: {},
        headers: {},
        config: { headers: {} as never },
      }),
    )
    const fallback = await resolveFachaktionCommand('Beleg-Inbox')
    expect(fallback.source).toBe('local')
    expect(fallback.action?.catalogId).toBe('workspace.document-inbox')
  })

  it('blockiert WRITE, Vier-Augen und executable:false ohne Auto-Submit', () => {
    expect(
      shouldBlockClientExecution({
        action_id: 'document.capture.open',
        authorized: false,
        reason: 'nicht ausfuehrbar',
        four_eyes: false,
        executable: false,
        access: 'write',
        command_endpoint: 'POST /api/v1/documents/approve',
        route_path: null,
        screen_id: null,
      }),
    ).toBe(true)

    const blocked = consumeResolvedFachaktion(
      {
        action_id: 'document.capture.open',
        authorized: false,
        reason: 'executable:false',
        four_eyes: false,
        executable: false,
        access: 'write',
        command_endpoint: 'POST /api/v1/documents/approve',
        route_path: null,
        screen_id: null,
      },
      'document.capture.open',
    )
    expect(blocked.source).toBe('blocked')
    expect(blocked.action).toBeUndefined()

    const prepare = consumeResolvedFachaktion(
      {
        action_id: 'sales.customer_quote.create',
        authorized: true,
        reason: 'write',
        four_eyes: false,
        executable: true,
        access: 'write',
        command_endpoint: 'POST /api/v1/sales/quotes',
        route_path: '/sales/angebot/neu',
        screen_id: 'sales/angebote/neu',
      },
      'Angebot anlegen',
    )
    expect(prepare.source).toBe('live')
    expect(prepare.action?.kind).toBe('prepare-command')
    expect(isLiveResolveUnavailable(new AxiosError('Network Error', 'ERR_NETWORK'))).toBe(true)
    expect(localResolveFallback('Annahme-Warteschlange')?.catalogId).toBe('harvest.intake-queue')

    const liveList = consumeResolvedFachaktion(
      {
        action_id: 'sales.customer_quote.list',
        authorized: true,
        reason: 'authorized',
        four_eyes: false,
        executable: true,
        access: 'read',
        command_endpoint: 'GET /api/v1/sales/offers',
        route_path: '/sales/angebote-liste',
        screen_id: 'sales/angebote-liste',
      },
      'Angebot Kunde',
    )
    expect(liveList.source).toBe('live')
    expect(liveList.action?.catalogId).toBe('sales.customer_quote.list')
    expect(liveList.action?.kind).toBe('open-worklist')
  })

  it('bildet YAML-Phrasen lokal auf catalogId ab, unbekannter Text bleibt ohne Treffer', () => {
    const phrases: Array<[string, string]> = [
      ['nicht disponierte LKW', 'logistik.undispatched_vehicles.list'],
      ['nicht disponierte lastwagen', 'logistik.undispatched_vehicles.list'],
      ['zeige mir nicht disponierte lkw bitte', 'logistik.undispatched_vehicles.list'],
      ['überfällige Kontrakte', 'agrar.contract.overdue.list'],
      ['ueberfaellige vertraege', 'agrar.contract.overdue.list'],
      ['Angebot Kunde', 'sales.customer_quote.list'],
      ['angebot anlegen', 'sales.customer_quote.create'],
      ['WE Mengenabweichung', 'einkauf.goods_receipt.quantity_variance.list'],
      ['Rechnungen Freigabe', 'finance.ap_invoice.approval.worklist'],
      ['ernte annahme', 'harvest.intake-queue'],
      ['dokumenteneingang', 'workspace.document-inbox'],
      ['qualitaets-check', 'agrar.qualitaets-handlungsbedarf'],
      ['tour anlegen', 'logistik.tour.anlegen'],
      ['wareneingang buchen', 'einkauf.anlieferavis.wareneingang'],
      ['Gutschriften Verkauf', 'sales.credit_note.list'],
      ['gutschriften einkauf', 'einkauf.gutschrift.list'],
      ['wiegeschein liste', 'weighing.tickets.list'],
      ['lieferscheine einkauf', 'einkauf.lieferschein.list'],
      ['lieferant anlegen', 'einkauf.lieferant.create'],
      ['artikel anlegen', 'artikel.stamm.create'],
    ]
    for (const [phrase, actionId] of phrases) {
      expect(resolveCatalogIdFromCommand(phrase)).toBe(actionId)
    }
    expect(localResolveFallback('nicht disponierte LKW')?.catalogId).toBe(
      'logistik.undispatched_vehicles.list',
    )
    expect(localResolveFallback('angebot anlegen')?.kind).toBe('prepare-command')
    expect(localResolveFallback('Angebot Kunde')?.catalogId).toBe('sales.customer_quote.list')
    expect(localResolveFallback('Angebot Kunde')?.kind).toBe('open-worklist')
    expect(localResolveFallback('WE Mengenabweichung')?.requiredScopes).toEqual(['einkauf:read'])
    expect(localResolveFallback('Rechnungen Freigabe')?.requiredScopes).toEqual(['finance:read'])
    expect(localResolveFallback('tour anlegen')).toBeUndefined()
    expect(localResolveFallback('SELECT * FROM invoices')).toBeUndefined()
    expect(localResolveFallback('https://example.invalid/api/v1/tours')).toBeUndefined()
    expect(localResolveFallback('/api/v1/logistik/tours')).toBeUndefined()
    expect(localResolveFallback('xyzzy plover')).toBeUndefined()
    expect(resolveCatalogIdFromCommand('auftrag')).toBeNull()
  })
})
