import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from '@/app/routing/test-router'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import {
  WORKSPACE_COMPOSITION_STORAGE_KEY,
  moveWorkspaceView,
  saveWorkspaceCompositionSession,
  setSpecializedKindEnabled,
  workspaceCompositionStorageKey,
} from '@/studio/workspace-composition-session'
import {
  EMPTY_COMPOSITION_OVERLAY,
  setFixedStartView,
} from '@/studio/workspace-composition-overlay'
import {
  AdaptiveWorkspaceLayer,
  DEFAULT_HOME_SPECIALIST_KINDS,
  homeSignalSpecialistKind,
  personalizeHomeComposition,
  resolveHomeComposition,
  resolveHomeSpecialistKinds,
  signalFromIstEvent,
  signalFromOpenAbrufe,
  signalsForHomeSpecialists,
  signalsFromQueueCounts,
} from '@/workspace'

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
    getAccessToken: () => 'home-composition-fixture-jwt',
  },
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(async (path: string) => {
      if (String(path).includes('/api/mcp/documents/inbox/queue')) {
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
      if (String(path) === '/api/v1/kontrakte' || String(path) === '/api/v1/agrar/contracts') {
        return { data: { items: [], total: 0, skip: 0, limit: 20 } }
      }
      if (String(path).startsWith('/api/v1/logistik/tours')) {
        return { data: [] }
      }
      return { data: { items: [] } }
    }),
    post: vi.fn(),
  },
}))

class SilentEventSource {
  url: string
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  constructor(url: string) {
    this.url = url
  }
  addEventListener(): void {}
  removeEventListener(): void {}
  close(): void {}
}

function memoryStorage(seed: Record<string, string> = {}): Storage {
  const map = new Map(Object.entries(seed))
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

function slotKinds(): string[] {
  const root = screen.queryByTestId('workspace-specialist-slots')
  if (!root) return []
  return [...root.querySelectorAll('[data-specialized-kind]')].map(
    (node) => node.getAttribute('data-specialized-kind') ?? '',
  )
}

function renderHomeLayer(): void {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <AdaptiveWorkspaceLayer />
      </QueryClientProvider>
    </MemoryRouter>,
  )
}

describe('Home Composition Session', () => {
  beforeEach(() => {
    sessionStorage.clear()
    localStorage.clear()
    vi.stubGlobal('EventSource', SilentEventSource)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('nimmt leer und ungueltiges JSON als Fixture-Fallback ohne Crash', () => {
    expect(resolveHomeSpecialistKinds(memoryStorage())).toEqual([
      'disposition_board',
      'inbox',
    ])
    expect(DEFAULT_HOME_SPECIALIST_KINDS).toEqual(['disposition_board', 'inbox'])
    const fallback = resolveHomeComposition(memoryStorage())
    expect(fallback.source).toBe('fallback')
    expect(fallback.composition.id).toBe(WORKSPACE_COMPOSITION_FIXTURE.id)
    expect(fallback.kinds).toEqual(['disposition_board', 'inbox'])

    const invalidJson = memoryStorage({
      [WORKSPACE_COMPOSITION_STORAGE_KEY]: '{nicht-json',
    })
    expect(resolveHomeSpecialistKinds(invalidJson)).toEqual(['disposition_board', 'inbox'])

    const invalidShape = memoryStorage({
      [WORKSPACE_COMPOSITION_STORAGE_KEY]: JSON.stringify({ id: '' }),
    })
    expect(resolveHomeSpecialistKinds(invalidShape)).toEqual(['disposition_board', 'inbox'])

    const exploding: Pick<Storage, 'getItem'> = {
      getItem: () => {
        throw new Error('quota')
      },
    }
    expect(resolveHomeSpecialistKinds(exploding)).toEqual(['disposition_board', 'inbox'])
  })

  it('ordnet Home-Slots nach Host-View-order und laesst fehlende Kinds weg', () => {
    const storage = memoryStorage()
    expect(saveWorkspaceCompositionSession(WORKSPACE_COMPOSITION_FIXTURE, storage).ok).toBe(true)
    expect(resolveHomeSpecialistKinds(storage)).toEqual(['disposition_board', 'inbox'])

    const inboxFirst = moveWorkspaceView(
      WORKSPACE_COMPOSITION_FIXTURE,
      'dispo-cockpit',
      'down',
    )
    expect(saveWorkspaceCompositionSession(inboxFirst, storage).ok).toBe(true)
    expect(resolveHomeSpecialistKinds(storage)).toEqual(['inbox', 'disposition_board'])

    const inboxOnly = setSpecializedKindEnabled(
      WORKSPACE_COMPOSITION_FIXTURE,
      'disposition_board',
      false,
    )
    expect(saveWorkspaceCompositionSession(inboxOnly, storage).ok).toBe(true)
    expect(resolveHomeSpecialistKinds(storage)).toEqual(['inbox'])

    const none = setSpecializedKindEnabled(inboxOnly, 'inbox', false)
    expect(saveWorkspaceCompositionSession(none, storage).ok).toBe(true)
    expect(resolveHomeSpecialistKinds(storage)).toEqual([])
  })

  it('liest mit sub denselben Composition-Key wie die Session', () => {
    const subject = 'person-a'
    const storage = memoryStorage({
      [WORKSPACE_COMPOSITION_STORAGE_KEY]: JSON.stringify(WORKSPACE_COMPOSITION_FIXTURE),
    })
    expect(resolveHomeSpecialistKinds(storage, subject)).toEqual(['disposition_board', 'inbox'])
    expect(storage.getItem(workspaceCompositionStorageKey(subject))).toBeNull()

    const inboxOnly = setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'disposition_board', false)
    expect(saveWorkspaceCompositionSession(inboxOnly, storage, subject).ok).toBe(true)
    expect(resolveHomeSpecialistKinds(storage, subject)).toEqual(['inbox'])
    expect(storage.getItem(WORKSPACE_COMPOSITION_STORAGE_KEY)).toContain('disposition_board')
  })

  it('liest mit Mandant und sub denselben Composition-Key wie die Session', () => {
    const subject = 'person-a'
    const tenant = 'haus-a'
    const inboxOnly = setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'disposition_board', false)
    const storage = memoryStorage({
      [workspaceCompositionStorageKey(subject)]: JSON.stringify(inboxOnly),
    })
    expect(resolveHomeSpecialistKinds(storage, subject, tenant)).toEqual(['inbox'])
    expect(storage.getItem(workspaceCompositionStorageKey(subject, tenant))).toBeNull()

    expect(saveWorkspaceCompositionSession(WORKSPACE_COMPOSITION_FIXTURE, storage, subject, tenant).ok).toBe(true)
    expect(resolveHomeSpecialistKinds(storage, subject, tenant)).toEqual(['disposition_board', 'inbox'])
    expect(storage.getItem(workspaceCompositionStorageKey(subject))).toContain('"kind":"inbox"')
  })

  it('mountet denselben Composition-Host mit Inbox und Dispo (Fixture-Fallback)', async () => {
    renderHomeLayer()
    expect(await screen.findByTestId('adaptive-workspace-layer')).toBeInTheDocument()
    const host = screen.getByTestId('workspace-composition-host')
    expect(host).toHaveAttribute('data-host-variant', 'embedded')
    expect(host).toHaveAttribute('data-composition-id', WORKSPACE_COMPOSITION_FIXTURE.id)
    expect(slotKinds()).toEqual(['disposition_board', 'inbox'])
    expect(screen.getByTestId('adaptive-workspace-inbox')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-disposition-entry')).toBeInTheDocument()
    expect(screen.getByTestId('disposition-board')).toBeInTheDocument()
  })

  it('respektiert die Fixture-View-Reihenfolge Dispo vor Inbox', async () => {
    saveWorkspaceCompositionSession(WORKSPACE_COMPOSITION_FIXTURE)
    renderHomeLayer()
    expect(await screen.findByTestId('workspace-specialist-slots')).toBeInTheDocument()
    expect(slotKinds()).toEqual(['disposition_board', 'inbox'])
    expect(screen.getByTestId('workspace-composition-host')).toHaveAttribute(
      'data-host-variant',
      'embedded',
    )
  })

  it('reiht Specialist-Kinds nach persönlichem Start-Fix ohne Studio-Session zu aendern', () => {
    const base = resolveHomeComposition(memoryStorage())
    expect(base.kinds).toEqual(['disposition_board', 'inbox'])
    const overlay = setFixedStartView(EMPTY_COMPOSITION_OVERLAY, 'beleg-inbox-host')
    const personalized = personalizeHomeComposition(base, overlay)
    expect(personalized.kinds).toEqual(['inbox', 'disposition_board'])
    expect(personalized.source).toBe(base.source)
    expect(base.composition.views[0]?.id).toBe('dispo-cockpit')
  })

  it('blendet die Dispo-Tafel aus wenn die Composition nur Inbox hat', async () => {
    saveWorkspaceCompositionSession(
      setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'disposition_board', false),
    )
    renderHomeLayer()
    expect(await screen.findByTestId('adaptive-workspace-inbox')).toBeInTheDocument()
    expect(slotKinds()).toEqual(['inbox'])
    expect(screen.queryByTestId('workspace-disposition-entry')).not.toBeInTheDocument()
    expect(screen.queryByTestId('disposition-board')).not.toBeInTheDocument()
  })

  it('filtert Specialist-Signale nach der Composition und behaelt den Default', () => {
    const inboxRow = { id: 'inbox:INBOX-9', source: 'inbox-queue' }
    const inboxCount = signalsFromQueueCounts({ inbox: 2 })[0]
    const approval = signalsFromQueueCounts({ approval: 1 })[0]
    const abrufe = signalFromOpenAbrufe([{ id: 'a1' }])
    const agrar = { id: 'agrar-chain:kon:K-2:waage', source: 'agrar-chain' }
    const freigabe = signalFromIstEvent('finance.ap_invoice.approval_requested')
    const calendar = { id: 'cal-season', source: 'calendar' }
    expect(inboxCount && approval && abrufe && freigabe).toBeTruthy()
    const all = [inboxRow, inboxCount!, approval!, abrufe!, agrar, freigabe!, calendar]

    expect(homeSignalSpecialistKind(inboxRow)).toBe('inbox')
    expect(homeSignalSpecialistKind(inboxCount!)).toBe('inbox')
    expect(homeSignalSpecialistKind(abrufe!)).toBe('disposition_board')
    expect(homeSignalSpecialistKind(approval!)).toBeNull()
    expect(homeSignalSpecialistKind(agrar)).toBeNull()
    expect(homeSignalSpecialistKind(freigabe!)).toBeNull()
    expect(homeSignalSpecialistKind(calendar)).toBeNull()

    const kept = (kinds: ReturnType<typeof resolveHomeSpecialistKinds>) =>
      signalsForHomeSpecialists(all, kinds).map((signal) => signal.id)

    expect(kept(resolveHomeSpecialistKinds(memoryStorage()))).toEqual(all.map((signal) => signal.id))

    const storage = memoryStorage()
    const inboxOnly = setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'disposition_board', false)
    expect(saveWorkspaceCompositionSession(inboxOnly, storage).ok).toBe(true)
    expect(kept(resolveHomeSpecialistKinds(storage))).toEqual([
      inboxRow.id,
      inboxCount!.id,
      approval!.id,
      agrar.id,
      freigabe!.id,
      calendar.id,
    ])

    const boardOnly = setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'inbox', false)
    expect(saveWorkspaceCompositionSession(boardOnly, storage).ok).toBe(true)
    expect(kept(resolveHomeSpecialistKinds(storage))).toEqual([
      approval!.id,
      abrufe!.id,
      agrar.id,
      freigabe!.id,
      calendar.id,
    ])

    const none = setSpecializedKindEnabled(boardOnly, 'disposition_board', false)
    expect(saveWorkspaceCompositionSession(none, storage).ok).toBe(true)
    expect(resolveHomeSpecialistKinds(storage)).toEqual([])
    expect(kept(resolveHomeSpecialistKinds(storage))).toEqual([
      approval!.id,
      agrar.id,
      freigabe!.id,
      calendar.id,
    ])
  })

  it('faellt bei kaputtem JSON auf Fixture-Host Dispo-dann-Inbox zurueck', async () => {
    sessionStorage.setItem(WORKSPACE_COMPOSITION_STORAGE_KEY, '{kaputt')
    expect(() => renderHomeLayer()).not.toThrow()
    expect(await screen.findByTestId('adaptive-workspace-inbox')).toBeInTheDocument()
    expect(slotKinds()).toEqual(['disposition_board', 'inbox'])
    expect(screen.getByTestId('workspace-composition-host')).toHaveAttribute(
      'data-composition-id',
      WORKSPACE_COMPOSITION_FIXTURE.id,
    )
  })
})
