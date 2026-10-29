import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor, within } from '@testing-library/react'
import { AxiosError } from 'axios'
import { MemoryRouter } from '@/app/routing/test-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as domMatchers from '@testing-library/jest-dom/matchers'

expect.extend(domMatchers)
import { LAUNCHPAD_OVERLAY_STORAGE_KEY } from '@/app/navigation/launchpad-personalization'
import { apiClient } from '@/lib/api-client'
import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import {
  saveWorkspaceCompositionSession,
  setSpecializedKindEnabled,
} from '@/studio/workspace-composition-session'
import {
  AGRAR_CHAIN_PATH,
  AGRAR_CONTRACTS_PATH,
  APPROVAL_QUEUE_PATH,
  AdaptiveWorkspaceLayer,
  OPEN_KONTRAKTE_PATH,
} from '@/workspace'

vi.mock('@/workspace/home-signals', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/workspace/home-signals')>()
  return {
    ...actual,
    workspaceNow: () => new Date('2026-10-22T08:00:00'),
  }
})

vi.mock('@/app/navigation/nav-runtime', () => ({
  useNavSections: () => [],
}))

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({ user: null }),
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: vi.fn() }),
}))

vi.mock('@/lib/auth', () => ({
  auth: {
    getAccessToken: () => 'inbox-ranking-fixture-jwt',
    getFreshAccessToken: async () => 'inbox-ranking-fixture-jwt',
  },
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

class SilentEventSource {
  url: string
  constructor(url: string) {
    this.url = url
  }
  addEventListener(): void {}
  removeEventListener(): void {}
  close(): void {}
}

function httpError(status: number): AxiosError {
  return new AxiosError('request failed', 'ERR_BAD_REQUEST', undefined, undefined, {
    status,
    statusText: 'Error',
    data: {},
    headers: {},
    config: { headers: {} as never },
  })
}

function queueItem(id: string, kind: string | null, canOpen = true) {
  return {
    id,
    status: 'pending',
    parsed_fields: {},
    match_values: {},
    confidence: 0.8,
    confidence_band: 'high',
    source: 'test',
    proposal: {
      policy_id: 'incoming-supplier-invoice',
      label:
        kind === 'LIEFERSCHEIN'
          ? 'Lieferschein oeffnen'
          : kind === 'GUTSCHRIFT'
            ? 'Gutschrift oeffnen'
            : kind === 'WIEGESCHEIN'
              ? 'Wiegeschein oeffnen'
              : 'Rechnungseingang erfassen',
      document_type: 'supplier_invoice',
      document_kind: kind,
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
        enabled: canOpen,
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
      confidence: 0.8,
      confidence_band: 'high',
      blockers: [],
      source: { kind: 'dms_inbox', id },
      gaps: ['create_from_inbox_bucht_nicht'],
    },
    can_open: canOpen,
    booking_allowed: false,
  }
}

function inboxResponse(items: ReturnType<typeof queueItem>[]) {
  return {
    data: {
      ok: true,
      source: 'mcp',
      available: true,
      booking_allowed: false,
      count: items.length,
      items,
      gaps: ['create_from_inbox_bucht_nicht'],
    },
  }
}

function renderLayer(): ReturnType<typeof render> {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <AdaptiveWorkspaceLayer />
      </QueryClientProvider>
    </MemoryRouter>,
  )
}

function pinInbox(): void {
  window.localStorage.setItem(
    LAUNCHPAD_OVERLAY_STORAGE_KEY,
    JSON.stringify({ pinnedTileIds: ['workspace.document-inbox'] }),
  )
}

describe('Inbox in der Rangliste', () => {
  beforeEach(() => {
    vi.stubGlobal('EventSource', SilentEventSource)
    window.localStorage.clear()
    window.sessionStorage.clear()
    vi.mocked(apiClient.get).mockReset()
    vi.mocked(apiClient.post).mockReset()
  })

  it('reiht oeffenbare Queue-Zeilen hinter dem Pin und laesst die Agrar-Kette stehen', async () => {
    pinInbox()
    vi.mocked(apiClient.get).mockImplementation(async (path: string, config) => {
      const url = String(path)
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return inboxResponse([
          queueItem('INBOX-9', 'EINGANGSRECHNUNG'),
          queueItem('INBOX-LS', 'LIEFERSCHEIN'),
          queueItem('INBOX-G', 'GUTSCHRIFT'),
          queueItem('INBOX-W', 'WIEGESCHEIN'),
          queueItem('INBOX-0', null),
          queueItem('INBOX-X', 'EINGANGSRECHNUNG', false),
        ])
      }
      if (url === OPEN_KONTRAKTE_PATH) {
        return {
          data: {
            items: [{ contract_id: 'K-2', status: 'OFFEN', lieferstatus: 'FREIGEGEBEN' }],
          },
        }
      }
      if (url === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      if (url === AGRAR_CHAIN_PATH) {
        const params = (config as { params?: Record<string, unknown> } | undefined)?.params ?? {}
        if (params.contract_ref === 'K-2') {
          return {
            data: {
              contract_ref: 'K-2',
              source_model: 'kon',
              next_step: 'waage',
              reason: 'abruf_freigegeben_waage_fehlt',
            },
          }
        }
      }
      return { data: { items: [], total: 0 } }
    })

    renderLayer()

    const work = await screen.findByTestId('workspace-work-items')
    await waitFor(() => {
      expect(within(work).getByRole('link', { name: 'Rechnungseingang erfassen' })).toBeInTheDocument()
      expect(within(work).getByRole('link', { name: 'K-2: Waage' })).toBeInTheDocument()
    })

    const items = within(work).getAllByRole('listitem')
    expect(items[0]).toHaveAttribute('data-fachaktion-id', 'workspace.document-inbox')
    expect(items[0]).toHaveTextContent('pinned')

    const invoice = within(work).getByRole('link', { name: 'Rechnungseingang erfassen' }).closest('li')
    expect(invoice).toHaveAttribute('data-fachaktion-id', 'inbox.queue.INBOX-9')
    expect(within(work).getByRole('link', { name: 'Rechnungseingang erfassen' })).toHaveAttribute(
      'href',
      '/belege/purchase_invoice/neu?inbox=INBOX-9',
    )
    expect(invoice).toHaveTextContent('layer:situational')
    expect(invoice).toHaveTextContent('signal:open-task')
    expect(invoice).toHaveTextContent('severity:3')
    expect(invoice).not.toHaveTextContent('pinned')
    expect(invoice).not.toHaveTextContent('vorbereiten')

    expect(within(work).getByRole('link', { name: 'K-2: Waage' })).toHaveAttribute('href', '/waage/wiegungen')
    // Top-5: Pin/Kalender/Agrar verdrängen Gutschrift/Wiegeschein — Href-Verdrahtung in inbox-rank.
    expect(work.querySelector('[data-fachaktion-id="inbox.queue.INBOX-G"]')).toBeNull()
    expect(work.querySelector('[data-fachaktion-id="inbox.queue.INBOX-W"]')).toBeNull()
    expect(work.querySelector('[data-fachaktion-id="inbox.queue.INBOX-0"]')).toBeNull()
    expect(work.querySelector('[data-fachaktion-id="inbox.queue.INBOX-X"]')).toBeNull()
    expect(within(work).getAllByRole('link', { name: 'Rechnungseingang erfassen' })).toHaveLength(1)
    expect(apiClient.post).not.toHaveBeenCalled()
  })

  it('zeigt bei leerer Queue und 401 keinen Inbox-Eintrag in der Rangliste', async () => {
    vi.mocked(apiClient.get).mockImplementation(async (path: string) => {
      const url = String(path)
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return inboxResponse([])
      }
      if (url === OPEN_KONTRAKTE_PATH || url === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      return { data: { items: [], total: 0 } }
    })

    const empty = renderLayer()
    expect(await screen.findByText('Kein Eingang in der Queue.')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-work-items').querySelector('[data-fachaktion-id^="inbox.queue."]')).toBeNull()
    empty.unmount()

    vi.mocked(apiClient.get).mockImplementation(async (path: string) => {
      const url = String(path)
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        throw httpError(401)
      }
      if (url === OPEN_KONTRAKTE_PATH || url === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      return { data: { items: [], total: 0 } }
    })

    renderLayer()
    await waitFor(() => {
      expect(screen.getByTestId('adaptive-workspace-inbox')).toHaveTextContent(/401|Unauthorized|request failed/i)
    })
    expect(screen.getByTestId('workspace-work-items').querySelector('[data-fachaktion-id^="inbox.queue."]')).toBeNull()
    expect(apiClient.post).not.toHaveBeenCalled()
  })

  it('blendet Inbox-Signale aus wenn die Composition keine Inbox enthaelt', async () => {
    pinInbox()
    saveWorkspaceCompositionSession(
      setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'inbox', false),
    )
    vi.mocked(apiClient.get).mockImplementation(async (path: string, config) => {
      const url = String(path)
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return inboxResponse([
          queueItem('INBOX-9', 'EINGANGSRECHNUNG'),
          queueItem('INBOX-LS', 'LIEFERSCHEIN'),
        ])
      }
      if (url === APPROVAL_QUEUE_PATH) {
        return { data: { items: [{ id: 'freigabe-1' }, { id: 'freigabe-2' }, { id: 'freigabe-3' }] } }
      }
      if (url === OPEN_KONTRAKTE_PATH) {
        return {
          data: {
            items: [{ contract_id: 'K-2', status: 'OFFEN', lieferstatus: 'FREIGEGEBEN' }],
          },
        }
      }
      if (url === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      if (url === AGRAR_CHAIN_PATH) {
        const params = (config as { params?: Record<string, unknown> } | undefined)?.params ?? {}
        if (params.contract_ref === 'K-2') {
          return {
            data: {
              contract_ref: 'K-2',
              source_model: 'kon',
              next_step: 'waage',
              reason: 'abruf_freigegeben_waage_fehlt',
            },
          }
        }
      }
      return { data: { items: [], total: 0 } }
    })

    renderLayer()

    const work = await screen.findByTestId('workspace-work-items')
    await waitFor(() => {
      const approval = within(work).getByRole('link', { name: 'Rechnungen auf meine Freigabe' }).closest('li')
      expect(approval).toHaveTextContent('count:3')
      expect(within(work).getByRole('link', { name: 'K-2: Waage' })).toBeInTheDocument()
    })

    const items = within(work).getAllByRole('listitem')
    expect(items[0]).toHaveAttribute('data-fachaktion-id', 'workspace.document-inbox')
    expect(items[0]).toHaveTextContent('pinned')
    expect(items[0]).not.toHaveTextContent('count:')
    expect(work.querySelector('[data-fachaktion-id^="inbox.queue."]')).toBeNull()
    expect(within(work).queryByRole('link', { name: 'Rechnungseingang erfassen' })).not.toBeInTheDocument()
    expect(screen.queryByTestId('adaptive-workspace-inbox')).not.toBeInTheDocument()
    expect(apiClient.post).not.toHaveBeenCalled()
  })
})
