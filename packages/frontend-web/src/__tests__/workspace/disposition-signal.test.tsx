import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor, within } from '@testing-library/react'
import { AxiosError } from 'axios'
import { MemoryRouter } from '@/app/routing/test-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { LAUNCHPAD_OVERLAY_STORAGE_KEY } from '@/app/navigation/launchpad-personalization'
import {
  ABRUFE_AUTH_ERROR,
  DISPOSITIONEN_PATH,
  KONTRAKTE_LIST_ENDPOINT,
} from '@/components/mask-builder/specialized/load-abrufe'
import { apiClient } from '@/lib/api-client'
import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import {
  WORKSPACE_COMPOSITION_STORAGE_KEY,
  saveWorkspaceCompositionSession,
  setSpecializedKindEnabled,
} from '@/studio/workspace-composition-session'
import {
  AGRAR_CONTRACTS_PATH,
  AdaptiveWorkspaceLayer,
  OPEN_ABRUF_ACTION_ID,
  OPEN_KONTRAKTE_PATH,
  WORKSPACE_FACHAKTIONEN,
  emptyUserContext,
  rankWorkspaceItems,
  signalFromOpenAbrufe,
} from '@/workspace'

const authState = { token: 'disposition-signal-fixture-jwt' as string | null }

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
    getAccessToken: () => authState.token,
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

const EXISTING_ROUTE = '/disposition/touren-disposition'

function httpError(status: number): AxiosError {
  return new AxiosError('request failed', 'ERR_BAD_REQUEST', undefined, undefined, {
    status,
    statusText: 'Error',
    data: {},
    headers: {},
    config: { headers: {} as never },
  })
}

function emptyInbox() {
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

function abrufRow(id: string, status: string) {
  return {
    id,
    kontrakt_id: 'c1',
    kontrakt_nr: 'K-100',
    disposition_nr: 1,
    menge: 12,
    status,
  }
}

function pinInbox(): void {
  window.localStorage.setItem(
    LAUNCHPAD_OVERLAY_STORAGE_KEY,
    JSON.stringify({ pinnedTileIds: ['workspace.document-inbox'] }),
  )
}

function renderLayer(): ReturnType<typeof render> & { queryClient: QueryClient } {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return {
    ...render(
      <MemoryRouter>
        <QueryClientProvider client={queryClient}>
          <AdaptiveWorkspaceLayer />
        </QueryClientProvider>
      </MemoryRouter>,
    ),
    queryClient,
  }
}

describe('signalFromOpenAbrufe', () => {
  const morning = new Date('2026-10-22T08:00:00')

  it('macht aus mehreren Abrufen ein Signal auf die bestehende Aktion', () => {
    expect(signalFromOpenAbrufe([])).toBeNull()
    const signal = signalFromOpenAbrufe([{ id: 'a1' }, { id: 'a2' }])
    expect(signal).toEqual({
      id: 'queue-open-abrufe',
      kind: 'open-task',
      layer: 'situational',
      relatedActionIds: [OPEN_ABRUF_ACTION_ID],
      severity: 3,
      source: 'disposition:open-abrufe',
      count: 2,
    })
    expect(signal?.relatedActionIds).toHaveLength(1)
  })

  it('laesst einen Pin vor dem Dispositions-Signal stehen', () => {
    const signal = signalFromOpenAbrufe([{ id: 'a1' }, { id: 'a2' }])
    const inbox = WORKSPACE_FACHAKTIONEN.find((action) => action.id === 'workspace.document-inbox')
    const trucks = WORKSPACE_FACHAKTIONEN.find((action) => action.id === OPEN_ABRUF_ACTION_ID)
    const ranked = rankWorkspaceItems({
      actions: [trucks!, inbox!],
      context: emptyUserContext({
        scopes: ['dms:read', 'logistics:read'],
        pinned: ['workspace.document-inbox'],
      }),
      signals: signal ? [signal] : [],
      now: morning,
    })
    expect(ranked.map((item) => item.action.id)).toEqual([
      'workspace.document-inbox',
      OPEN_ABRUF_ACTION_ID,
    ])
    expect(ranked[0]?.reasonCodes).toContain('pinned')
    expect(ranked[1]?.reasonCodes).toEqual(
      expect.arrayContaining(['signal:open-task', 'severity:3', 'count:2']),
    )
    expect(ranked[1]?.reasonCodes).not.toContain('pinned')
    expect(ranked[1]?.action.target.route).toBe('/disposition/touren-disposition')
    expect(ranked[1]?.action.catalogId).toBe('logistik.undispatched_vehicles.list')
  })
})

describe('offene Abrufe in der Rangliste', () => {
  beforeEach(() => {
    authState.token = 'disposition-signal-fixture-jwt'
    vi.stubGlobal('EventSource', SilentEventSource)
    window.localStorage.clear()
    window.sessionStorage.clear()
    vi.mocked(apiClient.get).mockReset()
    vi.mocked(apiClient.post).mockReset()
  })

  it('reiht ein Sammelsignal hinter dem Pin und nicht eine Zeile pro Abruf', async () => {
    pinInbox()
    vi.mocked(apiClient.get).mockImplementation(async (path: string, config) => {
      const url = String(path)
      const params = (config as { params?: Record<string, unknown> } | undefined)?.params
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return emptyInbox()
      }
      if (url === KONTRAKTE_LIST_ENDPOINT && params?.status === 'OFFEN') {
        return { data: { items: [{ contract_id: 'c1' }] } }
      }
      if (url === DISPOSITIONEN_PATH('c1')) {
        return {
          data: [
            abrufRow('abruf-1', 'OFFEN'),
            abrufRow('abruf-2', 'FREIGEGEBEN'),
            abrufRow('abruf-done', 'GELIEFERT'),
          ],
        }
      }
      if (url === OPEN_KONTRAKTE_PATH || url === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      return { data: { items: [], total: 0 } }
    })

    renderLayer()

    const work = await screen.findByTestId('workspace-work-items')
    await waitFor(() => {
      expect(within(work).getByRole('link', { name: 'Nicht disponierte LKW-Auftraege' })).toBeInTheDocument()
    })

    const items = within(work).getAllByRole('listitem')
    expect(items[0]).toHaveAttribute('data-fachaktion-id', 'workspace.document-inbox')
    expect(items[0]).toHaveTextContent('pinned')

    const row = within(work).getByRole('link', { name: 'Nicht disponierte LKW-Auftraege' }).closest('li')
    expect(row).toHaveAttribute('data-fachaktion-id', OPEN_ABRUF_ACTION_ID)
    expect(row).toHaveAttribute('data-catalog-id', 'logistik.undispatched_vehicles.list')
    expect(within(work).getByRole('link', { name: 'Nicht disponierte LKW-Auftraege' })).toHaveAttribute(
      'href',
      EXISTING_ROUTE,
    )
    expect(row).toHaveTextContent('signal:open-task')
    expect(row).toHaveTextContent('count:2')
    expect(row).not.toHaveTextContent('pinned')
    expect(work.querySelectorAll('[data-catalog-id="logistik.undispatched_vehicles.list"]')).toHaveLength(1)
    expect(work.querySelector('[data-fachaktion-id="abruf-1"]')).toBeNull()
    expect(work.querySelector('[data-fachaktion-id="abruf-2"]')).toBeNull()
    expect(apiClient.get).toHaveBeenCalledWith(
      KONTRAKTE_LIST_ENDPOINT,
      expect.objectContaining({ params: expect.objectContaining({ status: 'OFFEN' }) }),
    )
    expect(apiClient.post).not.toHaveBeenCalled()
  })

  it.each([
    [401, ABRUFE_AUTH_ERROR],
    [403, ABRUFE_AUTH_ERROR],
    [503, 'Abrufe nicht lesbar: Dienst oder Schema nicht bereit.'],
  ] as const)('zeigt bei HTTP %s ehrlichen Hinweis und kein Fake-Signal', async (status, message) => {
    vi.mocked(apiClient.get).mockImplementation(async (path: string, config) => {
      const url = String(path)
      const params = (config as { params?: Record<string, unknown> } | undefined)?.params
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return emptyInbox()
      }
      if (url === KONTRAKTE_LIST_ENDPOINT && params?.status === 'OFFEN') {
        throw httpError(status)
      }
      if (url === OPEN_KONTRAKTE_PATH || url === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      return { data: { items: [], total: 0 } }
    })

    const denied = renderLayer()
    await waitFor(() => {
      expect(apiClient.get).toHaveBeenCalledWith(
        KONTRAKTE_LIST_ENDPOINT,
        expect.objectContaining({ params: expect.objectContaining({ status: 'OFFEN' }) }),
      )
    })
    expect(screen.queryByRole('link', { name: 'Nicht disponierte LKW-Auftraege' })).not.toBeInTheDocument()
    expect(await screen.findByTestId('workspace-abrufe-error')).toHaveTextContent(message)
    denied.unmount()

    vi.mocked(apiClient.get).mockClear()
    vi.mocked(apiClient.get).mockImplementation(async (path: string, config) => {
      const url = String(path)
      const params = (config as { params?: Record<string, unknown> } | undefined)?.params
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return emptyInbox()
      }
      if (url === KONTRAKTE_LIST_ENDPOINT && params?.status === 'OFFEN') {
        return { data: { items: [] } }
      }
      if (url === OPEN_KONTRAKTE_PATH || url === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      return { data: { items: [], total: 0 } }
    })

    renderLayer()
    await waitFor(() => {
      expect(apiClient.get).toHaveBeenCalledWith(
        KONTRAKTE_LIST_ENDPOINT,
        expect.objectContaining({ params: expect.objectContaining({ status: 'OFFEN', include_done: false }) }),
      )
    })
    expect(screen.queryByRole('link', { name: 'Nicht disponierte LKW-Auftraege' })).not.toBeInTheDocument()
    expect(screen.queryByTestId('workspace-abrufe-error')).not.toBeInTheDocument()
    expect(apiClient.post).not.toHaveBeenCalled()
  })

  it('zeigt ohne Sitzung Auth-Hinweis und kein Abrufe-Ranking-Signal', async () => {
    authState.token = null
    vi.mocked(apiClient.get).mockImplementation(async (path: string) => {
      const url = String(path)
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return emptyInbox()
      }
      if (url === OPEN_KONTRAKTE_PATH || url === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      return { data: { items: [], total: 0 } }
    })

    renderLayer()
    expect(await screen.findByTestId('workspace-abrufe-error')).toHaveTextContent(ABRUFE_AUTH_ERROR)
    expect(screen.queryByRole('link', { name: 'Nicht disponierte LKW-Auftraege' })).not.toBeInTheDocument()
    // Ranking-Query bleibt disabled; die eingebettete Dispo-Tafel darf weiter laden (Board schon ehrlich).
    expect(apiClient.post).not.toHaveBeenCalled()
  })

  it('blendet offene Abrufe aus wenn die Composition keine Dispo-Tafel enthaelt', async () => {
    pinInbox()
    saveWorkspaceCompositionSession(
      setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'disposition_board', false),
    )
    vi.mocked(apiClient.get).mockImplementation(async (path: string, config) => {
      const url = String(path)
      const params = (config as { params?: Record<string, unknown> } | undefined)?.params
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return emptyInbox()
      }
      if (url === KONTRAKTE_LIST_ENDPOINT && params?.status === 'OFFEN') {
        return { data: { items: [{ contract_id: 'c1' }] } }
      }
      if (url === DISPOSITIONEN_PATH('c1')) {
        return {
          data: [abrufRow('abruf-1', 'OFFEN'), abrufRow('abruf-2', 'FREIGEGEBEN')],
        }
      }
      if (url === OPEN_KONTRAKTE_PATH || url === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      return { data: { items: [], total: 0 } }
    })

    const view = renderLayer()
    await waitFor(() => {
      expect(view.queryClient.getQueryState(['disposition', 'kontrakt-abrufe'])?.status).toBe('success')
    })

    const work = screen.getByTestId('workspace-work-items')
    const items = within(work).getAllByRole('listitem')
    expect(items[0]).toHaveAttribute('data-fachaktion-id', 'workspace.document-inbox')
    expect(items[0]).toHaveTextContent('pinned')
    expect(work).not.toHaveTextContent('count:2')
    expect(work.querySelector('[data-fachaktion-id="abruf-1"]')).toBeNull()
    expect(screen.queryByTestId('workspace-disposition-entry')).not.toBeInTheDocument()
    expect(screen.queryByTestId('workspace-abrufe-error')).not.toBeInTheDocument()
    expect(apiClient.post).not.toHaveBeenCalled()
  })

  it('blendet Auth-Hinweis aus wenn Composition keine Dispo-Tafel hat', async () => {
    authState.token = null
    saveWorkspaceCompositionSession(
      setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'disposition_board', false),
    )
    vi.mocked(apiClient.get).mockImplementation(async (path: string) => {
      const url = String(path)
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return emptyInbox()
      }
      if (url === OPEN_KONTRAKTE_PATH || url === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      return { data: { items: [], total: 0 } }
    })

    renderLayer()
    await screen.findByTestId('workspace-work-items')
    expect(screen.queryByTestId('workspace-abrufe-error')).not.toBeInTheDocument()
    expect(apiClient.get).not.toHaveBeenCalledWith(
      KONTRAKTE_LIST_ENDPOINT,
      expect.objectContaining({
        params: expect.objectContaining({ status: 'OFFEN', include_done: false }),
      }),
    )
  })

  it('behaelt offene Abrufe bei ungueltiger Composition', async () => {
    pinInbox()
    window.sessionStorage.setItem(WORKSPACE_COMPOSITION_STORAGE_KEY, '{kaputt')
    vi.mocked(apiClient.get).mockImplementation(async (path: string, config) => {
      const url = String(path)
      const params = (config as { params?: Record<string, unknown> } | undefined)?.params
      if (url.includes('/api/mcp/documents/inbox/queue')) {
        return emptyInbox()
      }
      if (url === KONTRAKTE_LIST_ENDPOINT && params?.status === 'OFFEN') {
        return { data: { items: [{ contract_id: 'c1' }] } }
      }
      if (url === DISPOSITIONEN_PATH('c1')) {
        return {
          data: [abrufRow('abruf-1', 'OFFEN'), abrufRow('abruf-2', 'FREIGEGEBEN')],
        }
      }
      if (url === OPEN_KONTRAKTE_PATH || url === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      return { data: { items: [], total: 0 } }
    })

    renderLayer()
    const work = await screen.findByTestId('workspace-work-items')
    await waitFor(() => {
      expect(within(work).getByRole('link', { name: 'Nicht disponierte LKW-Auftraege' })).toBeInTheDocument()
    })
    const row = within(work).getByRole('link', { name: 'Nicht disponierte LKW-Auftraege' }).closest('li')
    expect(row).toHaveTextContent('count:2')
    const items = within(work).getAllByRole('listitem')
    expect(items[0]).toHaveAttribute('data-fachaktion-id', 'workspace.document-inbox')
    expect(items[0]).toHaveTextContent('pinned')
  })
})
