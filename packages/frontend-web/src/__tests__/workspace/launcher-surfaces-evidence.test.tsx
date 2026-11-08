/**
 * Browser-Ersatznachweis fuer Launcher-Flaechen (Auth-STOP ohne JWT).
 * Rendert AdaptiveWorkspaceLayer, CommandPalette, InboxWidget und DispositionBoard
 * mit Fixtures und belegt die Gate-Invarianten — kein Schein-Import-Test.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as domMatchers from '@testing-library/jest-dom/matchers'

expect.extend(domMatchers)
import { MemoryRouter } from '@/app/routing/test-router'
import {
  InboxPrefillBanner,
  InboxWidget,
  INBOX_PREFILL_SCHEMA,
  INBOX_PREFILL_STORAGE_KEY,
} from '@/components/adaptive-workspace/inbox'
import type { InboxPrefillPayload, InboxQueueItem } from '@/components/adaptive-workspace/inbox'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { DispositionBoard } from '@/components/mask-builder/specialized/disposition-board'
import { dispositionBoardScreen } from '@/components/mask-builder/specialized/disposition-board-screen'
import { formatStopLatLng } from '@/components/mask-builder/specialized/load-timeline'
import { orderDragId } from '@/components/mask-builder/specialized/board-dnd'
import { CommandPalette } from '@/components/navigation/CommandPalette'
import { apiClient } from '@/lib/api-client'
import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import {
  saveWorkspaceCompositionSession,
  setSpecializedKindEnabled,
} from '@/studio/workspace-composition-session'
import { AdaptiveWorkspaceLayer } from '@/workspace/AdaptiveWorkspaceLayer'
import {
  FACHAKTION_MCP_CALL_PATH,
  FACHAKTION_RESOLVE_TOOL,
} from '@/workspace/fachaktion-resolve'

const dispatchMock = vi.fn<(_actionId: string, _params?: Record<string, unknown>) => Promise<boolean>>()

vi.mock('@/app/navigation/nav-runtime', () => ({
  useNavSections: () => [],
  useNavigationShortcuts: () => [],
}))

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({ user: null }),
}))

vi.mock('@/lib/auth', () => ({
  auth: {
    getAccessToken: () => 'launcher-evidence-fixture-jwt',
    getFreshAccessToken: async () => 'launcher-evidence-fixture-jwt',
  },
}))

vi.mock('@/hooks/useFeature', () => ({
  useFeature: (feature: string) => feature === 'agrar' || feature === 'commandPalette',
}))

vi.mock('@/features/ki-usability/context/ActionDispatchHooks', () => ({
  useActionDispatch: () => ({
    registerHandler: vi.fn(),
    dispatch: dispatchMock,
  }),
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: vi.fn() }),
}))

const maplibreProbe = vi.hoisted(() => ({
  options: [] as Array<{ style?: { sources?: { osm?: { tiles?: string[] } } } }>,
}))

vi.mock('maplibre-gl', () => {
  class Marker {
    element: HTMLElement
    constructor(opts?: { element?: HTMLElement }) {
      this.element = opts?.element ?? document.createElement('div')
    }
    setLngLat(): this {
      return this
    }
    addTo(map: { getContainer: () => HTMLElement }): this {
      map.getContainer().appendChild(this.element)
      return this
    }
    remove(): void {
      this.element.remove()
    }
  }
  class Map {
    private readonly container: HTMLElement
    constructor(opts: { container: HTMLElement; style?: { sources?: { osm?: { tiles?: string[] } } } }) {
      this.container = opts.container
      maplibreProbe.options.push(opts)
    }
    getContainer(): HTMLElement {
      return this.container
    }
    on(event: string, cb: () => void): void {
      if (event === 'load') cb()
    }
    remove(): void {}
    fitBounds(): void {}
  }
  return { Map, Marker }
})

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

const mockedGet = vi.mocked(apiClient.get)
const mockedPost = vi.mocked(apiClient.post)

class FakeEventSource {
  static instances: FakeEventSource[] = []
  url: string
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  constructor(url: string) {
    this.url = url
    FakeEventSource.instances.push(this)
  }
  addEventListener(): void {}
  removeEventListener(): void {}
  close(): void {}
}

function wrap(node: JSX.Element): JSX.Element {
  return (
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>{node}</MemoryRouter>
    </QueryClientProvider>
  )
}

function dropOnTour(orderId = 'ord-1'): void {
  fireEvent.drop(screen.getByTestId('dispo-resource-tour-1'), {
    dataTransfer: { getData: () => orderDragId(orderId) },
  })
}

function queueItem(): InboxQueueItem {
  return {
    id: 'INBOX-EV-1',
    status: 'pending',
    parsed_fields: {},
    match_values: {},
    confidence: 0.72,
    confidence_band: 'medium',
    source: 'evidence-ocr-class',
    proposal: {
      policy_id: 'incoming-supplier-invoice',
      label: 'Rechnungseingang erfassen',
      document_type: 'supplier_invoice',
      document_kind: 'EINGANGSRECHNUNG',
      direction: 'incoming',
      target_route: '/einkauf/rechnung-eingang-erfassung',
      reason: 'evidence',
    },
    duplicates: [],
    blockers: [],
    actions: [
      {
        key: 'open_mask',
        label: 'Beleg öffnen',
        kind: 'primary',
        href: '/belege/purchase_invoice/neu?inbox=INBOX-EV-1',
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
        schema: INBOX_PREFILL_SCHEMA,
        documentId: 'INBOX-EV-1',
        partner: { role: 'supplier' },
        amounts: { currency: 'EUR' },
        source: {
          kind: 'dms_inbox',
          id: 'INBOX-EV-1',
          classification: 'evidence-ocr-class',
        },
        confidence: 0.72,
        confidenceBand: 'medium',
        policyId: 'incoming-supplier-invoice',
        documentType: 'supplier_invoice',
        targetRoute: '/einkauf/rechnung-eingang-erfassung',
        booking: false,
        matchValues: {},
        storageKey: INBOX_PREFILL_STORAGE_KEY,
        maskConsumesPrefill: true,
      },
      confidence: 0.72,
      confidence_band: 'medium',
      blockers: [],
      source: { kind: 'dms_inbox', id: 'INBOX-EV-1' },
      gaps: [],
    },
    can_open: true,
    booking_allowed: false,
  }
}

function samplePrefill(): InboxPrefillPayload {
  return {
    schema: INBOX_PREFILL_SCHEMA,
    documentId: 'INBOX-EV-1',
    partner: { role: 'supplier' },
    amounts: { currency: 'EUR' },
    source: { kind: 'dms_inbox', id: 'INBOX-EV-1', classification: 'evidence-ocr-class' },
    confidence: 0.72,
    confidenceBand: 'medium',
    policyId: 'incoming-supplier-invoice',
    documentType: 'supplier_invoice',
    targetRoute: '/einkauf/rechnung-eingang-erfassung',
    booking: false,
    matchValues: {},
    storageKey: INBOX_PREFILL_STORAGE_KEY,
    maskConsumesPrefill: true,
  }
}

describe('Launcher-Flaechen Evidence (ohne Browser-Login)', () => {
  beforeEach(() => {
    localStorage.clear()
    sessionStorage.clear()
    dispatchMock.mockReset()
    dispatchMock.mockResolvedValue(true)
    mockedGet.mockReset()
    mockedPost.mockReset()
    maplibreProbe.options.length = 0
    FakeEventSource.instances = []
    vi.stubGlobal('EventSource', FakeEventSource)
    window.HTMLElement.prototype.scrollIntoView = vi.fn()

    mockedGet.mockImplementation(async (url: string) => {
      if (String(url).includes('/api/mcp/documents/inbox/queue')) {
        return {
          data: {
            ok: true,
            source: 'mcp',
            available: true,
            booking_allowed: false,
            count: 1,
            items: [queueItem()],
            gaps: [],
          },
        } as never
      }
      if (String(url).includes('/search')) {
        return { data: { results: [] } } as never
      }
      if (String(url).includes('/omnibox-catalog')) {
        return { data: [] } as never
      }
      if (String(url).includes('mask-registry') || String(url).includes('/masks')) {
        return { data: { schema_version: 1, masks: [] } } as never
      }
      if (String(url) === '/api/v1/logistik/tours') {
        return { data: [{ id: 'tour-1', vehicle_id: 'LKW', status: 'GEPLANT' }] } as never
      }
      if (String(url) === '/api/v1/logistik/tours/tour-1') {
        return {
          data: {
            id: 'tour-1',
            vehicle_id: 'LKW',
            stops: [
              {
                id: 'stop-1',
                planned_arrival: '2026-10-22T08:00:00.000Z',
                delivery_note_ref: 'LS-EV',
                lat: 53.0793,
                lng: 8.8017,
              },
            ],
          },
        } as never
      }
      return { data: { items: [], total: 0 } } as never
    })
  })

  it('rendert Start/Handlungsbedarf und blendet Dispo per Composition-Filter aus', async () => {
    saveWorkspaceCompositionSession(
      setSpecializedKindEnabled(WORKSPACE_COMPOSITION_FIXTURE, 'disposition_board', false),
    )
    render(wrap(<AdaptiveWorkspaceLayer />))

    expect(await screen.findByTestId('adaptive-workspace-layer')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Start' })).toBeInTheDocument()
    expect(screen.getByTestId('workspace-work-items')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-dialog-layer')).toBeInTheDocument()
    expect(screen.getByTestId('adaptive-workspace-inbox')).toBeInTheDocument()
    expect(screen.queryByTestId('workspace-disposition-entry')).not.toBeInTheDocument()
  })

  it('loest Palette-Aliase im dryRun ohne Auto-Submit', async () => {
    mockedPost.mockResolvedValue({
      data: {
        action_id: 'logistik.undispatched_vehicles.list',
        authorized: true,
        executable: true,
        four_eyes: false,
        access: 'read',
        reason: 'ok',
      },
    } as never)

    render(wrap(<CommandPalette open onOpenChange={vi.fn()} />))

    fireEvent.change(screen.getByPlaceholderText(/Aktion suchen/), {
      target: { value: 'nicht disponierte LKW' },
    })

    await waitFor(() => {
      expect(mockedPost).toHaveBeenCalledWith(
        FACHAKTION_MCP_CALL_PATH,
        expect.objectContaining({
          tool_name: FACHAKTION_RESOLVE_TOOL,
          mode: 'dryRun',
          parameters: expect.objectContaining({ command: 'nicht disponierte LKW' }),
        }),
      )
    })

    await waitFor(() => {
      expect(
        document.querySelector('[data-catalog-id="logistik.undispatched_vehicles.list"]'),
      ).not.toBeNull()
    })
    expect(dispatchMock).not.toHaveBeenCalled()
    expect(JSON.stringify(mockedPost.mock.calls)).not.toMatch(/autoSubmit|auto-submit|"execute"/)
  })

  it('zeigt Inbox-Klassifikation und Prefill ohne Buchung', () => {
    const row = queueItem()
    render(wrap(<InboxWidget queue={[row]} />))
    expect(screen.getByTestId('adaptive-workspace-inbox')).toBeInTheDocument()
    expect(screen.getByTestId('inbox-confidence-INBOX-EV-1')).toHaveTextContent(/72\s*%/)
    expect(screen.getByTestId('inbox-source-INBOX-EV-1')).toHaveTextContent('evidence-ocr-class')

    render(<InboxPrefillBanner payload={samplePrefill()} />)
    expect(screen.getByTestId('inbox-prefill-classification')).toHaveTextContent('evidence-ocr-class')
    expect(screen.getByTestId('inbox-prefill-confidence')).toHaveTextContent(/72\s*%/)
    expect(samplePrefill().booking).toBe(false)
    expect(row.booking_allowed).toBe(false)
  })

  it('haengt Disposition an Meridian und zeigt Karte mit gesperrter Zuweisung', async () => {
    expect(dispositionBoardScreen.specialized?.type).toBe('disposition_board')
    const plan = compileRenderPlanFromScreenDefinition(dispositionBoardScreen)
    expect(plan.specialized?.type).toBe('disposition_board')

    const { unmount: unmountMeridian } = render(wrap(<UniversalMaskRenderer plan={plan} />))
    expect(await screen.findByTestId('disposition-board')).toBeInTheDocument()
    const marker = await screen.findByTestId('dispo-map-marker-stop-1')
    expect(marker).toHaveAttribute('data-lat', '53.0793')
    expect(marker).toHaveAttribute('data-lng', '8.8017')
    expect(screen.getByTestId('dispo-stop-coord-stop-1')).toHaveTextContent(
      `LS-EV ${formatStopLatLng(53.0793, 8.8017)}`,
    )
    for (const option of maplibreProbe.options) {
      expect(option.style?.sources?.osm?.tiles).toEqual([
        'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
      ])
    }
    unmountMeridian()

    mockedPost.mockResolvedValue({
      data: {
        ok: true,
        event: 'logistik.tour.created',
        persisted: true,
        quantity_posted: false,
        tour_id: 'tour-1',
      },
    } as never)

    const model = {
      orders: [{ id: 'ord-1', label: 'Weizen', quantity: 12, contractId: 'K-1' }],
      resources: [{ id: 'tour-1', label: 'LKW', driver: 'Meier', status: 'geplant' }],
      operations: [],
    }
    render(wrap(<DispositionBoard contract={dispositionBoardScreen.specialized!} model={model} />))
    expect(screen.getByTestId('dispo-preview-notice')).toHaveTextContent('Zuweisungen sind noch nicht freigegeben')
    dropOnTour('ord-1')
    expect(mockedPost).not.toHaveBeenCalled()
  })
})
