import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor, within } from '@testing-library/react'
import { AxiosError } from 'axios'
import { MemoryRouter } from '@/app/routing/test-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
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
    getAccessToken: () => 'agrar-chain-ranking-fixture-jwt',
    getFreshAccessToken: async () => 'agrar-chain-ranking-fixture-jwt',
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

describe('Agrar-Kette in der Rangliste', () => {
  beforeEach(() => {
    vi.stubGlobal('EventSource', SilentEventSource)
    window.localStorage.clear()
    window.sessionStorage.clear()
    vi.mocked(apiClient.get).mockReset()
  })

  it('reiht den geladenen Waage-Schritt hinter dem Pin und laesst done aussen', async () => {
    pinInbox()
    vi.mocked(apiClient.get).mockImplementation(async (path: string, config) => {
      const url = String(path)
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return {
          data: {
            ok: true,
            source: 'mcp',
            available: true,
            booking_allowed: false,
            count: 0,
            items: [],
            gaps: [],
          },
        }
      }
      if (url === OPEN_KONTRAKTE_PATH) {
        return {
          data: {
            items: [
              { contract_id: 'K-2', status: 'OFFEN', lieferstatus: 'FREIGEGEBEN' },
              { contract_id: 'K-9', status: 'ERLEDIGT' },
            ],
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
        return {
          data: {
            contract_ref: 'K-9',
            source_model: 'kon',
            next_step: 'done',
            reason: 'kontrakt_erledigt_oder_settlement_posted',
          },
        }
      }
      return { data: { items: [], total: 0 } }
    })

    renderLayer()

    const work = await screen.findByTestId('workspace-work-items')
    await waitFor(() => {
      expect(within(work).getByRole('link', { name: 'K-2: Waage' })).toBeInTheDocument()
    })

    const items = within(work).getAllByRole('listitem')
    expect(items[0]).toHaveAttribute('data-fachaktion-id', 'workspace.document-inbox')
    expect(items[0]).toHaveTextContent('pinned')

    const waageRow = within(work).getByRole('link', { name: 'K-2: Waage' }).closest('li')
    expect(waageRow).toHaveAttribute('data-fachaktion-id', 'agrar.chain.kon.K-2.waage')
    expect(within(work).getByRole('link', { name: 'K-2: Waage' })).toHaveAttribute('href', '/waage/wiegungen')
    expect(waageRow).toHaveTextContent('layer:situational')
    expect(waageRow).toHaveTextContent('signal:open-task')
    expect(waageRow).toHaveTextContent('severity:3')
    expect(waageRow).not.toHaveTextContent('pinned')
    expect(work).not.toHaveTextContent('K-9')
    expect(work).not.toHaveTextContent('Abgeschlossen')

    expect(screen.getAllByRole('link', { name: 'K-2: Waage' })).toHaveLength(2)
    expect(screen.getByText('K-9: Abgeschlossen')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'K-9: Abgeschlossen' })).not.toBeInTheDocument()

    const kontraktCalls = vi.mocked(apiClient.get).mock.calls.filter((call) => {
      if (call[0] !== OPEN_KONTRAKTE_PATH) return false
      const params = (call[1] as { params?: { include_done?: boolean } } | undefined)?.params
      return params?.include_done === true
    })
    expect(kontraktCalls).toHaveLength(1)
    const chainCalls = vi.mocked(apiClient.get).mock.calls.filter((call) => call[0] === AGRAR_CHAIN_PATH)
    expect(chainCalls).toHaveLength(2)
    for (const call of chainCalls) {
      const params = (call[1] as { params?: Record<string, unknown> } | undefined)?.params
      expect(params?.quality_is_final).toBeUndefined()
    }
    expect(chainCalls.some((call) => {
      const params = (call[1] as { params?: Record<string, unknown> } | undefined)?.params
      return params?.contract_ref === 'K-2' && params?.disposition_status === 'FREIGEGEBEN'
    })).toBe(true)
  })

  it('zeigt bei leerer Liste und 401 keinen Ketten-Eintrag in der Rangliste', async () => {
    vi.mocked(apiClient.get).mockImplementation(async (path: string) => {
      const url = String(path)
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return {
          data: {
            ok: true,
            source: 'mcp',
            available: true,
            booking_allowed: false,
            count: 0,
            items: [],
            gaps: [],
          },
        }
      }
      if (url === OPEN_KONTRAKTE_PATH || url === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      return { data: { items: [], total: 0 } }
    })

    const empty = renderLayer()
    expect(await screen.findByText('keine Kette')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-work-items').querySelector('[data-fachaktion-id^="agrar.chain."]')).toBeNull()
    empty.unmount()

    vi.mocked(apiClient.get).mockImplementation(async (path: string) => {
      const url = String(path)
      if (url === OPEN_KONTRAKTE_PATH || url === AGRAR_CONTRACTS_PATH) {
        throw httpError(401)
      }
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return {
          data: {
            ok: true,
            source: 'mcp',
            available: true,
            booking_allowed: false,
            count: 0,
            items: [],
            gaps: [],
          },
        }
      }
      return { data: { items: [], total: 0 } }
    })

    renderLayer()
    await waitFor(() => {
      expect(screen.queryByTestId('workspace-agrar-chain')).toBeNull()
    })
    expect(screen.getByTestId('workspace-work-items').querySelector('[data-fachaktion-id^="agrar.chain."]')).toBeNull()
  })

  it('laesst die Agrar-Kette stehen wenn Inbox und Dispo abgewaehlt sind', async () => {
    pinInbox()
    const inboxOff = setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'inbox', false)
    saveWorkspaceCompositionSession(setSpecializedKindEnabled(inboxOff, 'disposition_board', false))
    vi.mocked(apiClient.get).mockImplementation(async (path: string, config) => {
      const url = String(path)
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return {
          data: {
            ok: true,
            source: 'mcp',
            available: true,
            booking_allowed: false,
            count: 2,
            items: [{ id: 'INBOX-9' }, { id: 'INBOX-LS' }],
            gaps: [],
          },
        }
      }
      if (url === APPROVAL_QUEUE_PATH) {
        return { data: { items: [{ id: 'freigabe-1' }] } }
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
      expect(within(work).getByRole('link', { name: 'K-2: Waage' })).toBeInTheDocument()
      const approval = within(work).getByRole('link', { name: 'Rechnungen auf meine Freigabe' }).closest('li')
      expect(approval).toHaveTextContent('count:1')
    })

    const items = within(work).getAllByRole('listitem')
    expect(items[0]).toHaveAttribute('data-fachaktion-id', 'workspace.document-inbox')
    expect(items[0]).toHaveTextContent('pinned')
    expect(items[0]).not.toHaveTextContent('count:')
    const waageRow = within(work).getByRole('link', { name: 'K-2: Waage' }).closest('li')
    expect(waageRow).toHaveAttribute('data-fachaktion-id', 'agrar.chain.kon.K-2.waage')
    expect(waageRow).toHaveTextContent('signal:open-task')
    expect(waageRow).not.toHaveTextContent('pinned')
    expect(work.querySelector('[data-fachaktion-id^="inbox.queue."]')).toBeNull()
    expect(screen.queryByTestId('workspace-specialist-slots')).not.toBeInTheDocument()
  })
})
