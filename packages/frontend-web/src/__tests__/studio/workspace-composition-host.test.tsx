import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { MemoryRouter } from '@/app/routing/test-router'
import type { InboxQueueItem } from '@/components/adaptive-workspace/inbox'
import { formatStopLatLng } from '@/components/mask-builder/specialized/load-timeline'
import WorkspaceCompositionPreviewPage from '@/pages/studio/workspace-composition-preview'
import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import { WorkspaceCompositionHost } from '@/studio/WorkspaceCompositionHost'
import { DISPOSITION_BOARD_ROUTE } from '@/studio/workspace-composition-runtime'
import { WORKSPACE_COMPOSITION_STORAGE_KEY } from '@/studio/workspace-composition-session'

class SilentEventSource {
  static instances: SilentEventSource[] = []
  url: string
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  constructor(url: string) {
    this.url = url
    SilentEventSource.instances.push(this)
  }

  addEventListener(): void {}
  removeEventListener(): void {}
  close(): void {}
}

const getMock = vi.hoisted(() => vi.fn())
const postMock = vi.hoisted(() => vi.fn())
const maplibreProbe = vi.hoisted(() => ({
  options: [] as Array<{ style?: { sources?: { osm?: { tiles?: string[] } } } }>,
}))

vi.mock('@/lib/api-client', () => ({
  apiClient: { get: getMock, post: postMock },
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast: vi.fn() }),
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

function emptyQueueItem(): InboxQueueItem {
  return {
    id: 'INBOX-1',
    status: 'pending',
    parsed_fields: {},
    match_values: {},
    confidence: 0.9,
    confidence_band: 'high',
    source: 'test',
    proposal: {
      policy_id: 'incoming-supplier-invoice',
      label: 'Rechnungseingang',
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
      prefill: {
        schema: 'valeo.inbox.prefill.v1',
        documentId: 'INBOX-1',
        partner: { role: 'supplier' },
        amounts: { currency: 'EUR' },
        source: { kind: 'dms_inbox', id: 'INBOX-1' },
        confidence: 0.9,
        confidenceBand: 'high',
        policyId: 'incoming-supplier-invoice',
        documentType: 'supplier_invoice',
        targetRoute: '/einkauf/rechnung-eingang-erfassung',
        booking: false,
        matchValues: {},
        storageKey: 'valeo.inbox.prefill',
        maskConsumesPrefill: true,
      },
      confidence: 0.9,
      confidence_band: 'high',
      blockers: [],
      source: { kind: 'dms_inbox', id: 'INBOX-1' },
      gaps: [],
    },
    booking_allowed: false,
  }
}

function renderHost(node: JSX.Element): ReturnType<typeof render> {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter>{node}</MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('WorkspaceCompositionHost', () => {
  beforeEach(() => {
    getMock.mockReset()
    postMock.mockReset()
    maplibreProbe.options.length = 0
    getMock.mockResolvedValue({ data: { items: [] } })
    localStorage.clear()
    sessionStorage.clear()
    SilentEventSource.instances = []
    vi.stubGlobal('EventSource', SilentEventSource)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('rendert InboxWidget, registrierte Dispo-Tafel und Views aus der Composition', () => {
    renderHost(
        <WorkspaceCompositionHost
          composition={WORKSPACE_COMPOSITION_FIXTURE}
          inboxQueue={[emptyQueueItem()]}
        />
    )

    expect(screen.getByTestId('workspace-composition-host')).toHaveAttribute(
      'data-composition-id',
      'workspace.disposition-und-inbox',
    )
    expect(screen.getByTestId('workspace-composition-host')).toHaveAttribute(
      'data-host-variant',
      'studio',
    )
    expect(screen.getByTestId('workspace-composition-views')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-composition-view-dispo-cockpit')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-composition-slot-slot-document-inbox')).toBeInTheDocument()
    expect(screen.getByTestId('adaptive-workspace-inbox')).toBeInTheDocument()
    const boardSlot = screen.getByTestId('workspace-composition-slot-slot-disposition-board')
    expect(boardSlot).toHaveAttribute('data-board-route', DISPOSITION_BOARD_ROUTE)
    expect(screen.queryByTestId('workspace-composition-disposition-link-slot-disposition-board')).not.toBeInTheDocument()
    const board = screen.getByTestId('disposition-board')
    expect(boardSlot).toContainElement(board)
    expect(board).toHaveAttribute('data-specialized-id', 'lkw-disposition-board')
  })

  it('embedded: View-Pins ohne Studio-h1, Home-Testids und onQueue', () => {
    const onQueue = vi.fn()
    renderHost(
      <WorkspaceCompositionHost
        composition={WORKSPACE_COMPOSITION_FIXTURE}
        inboxQueue={[emptyQueueItem()]}
        variant="embedded"
        onQueue={onQueue}
      />,
    )

    expect(screen.getByTestId('workspace-composition-host')).toHaveAttribute(
      'data-host-variant',
      'embedded',
    )
    expect(screen.queryByTestId('workspace-composition-views')).not.toBeInTheDocument()
    expect(screen.getByTestId('workspace-composition-view-pins')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-specialist-slots')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-disposition-entry')).toHaveAttribute(
      'data-board-route',
      DISPOSITION_BOARD_ROUTE,
    )
    expect(screen.getByTestId('disposition-board')).toBeInTheDocument()
    expect(screen.getByTestId('adaptive-workspace-inbox')).toBeInTheDocument()
    expect(onQueue).toHaveBeenCalled()
  })

  it('pinnt eine View und fixiert sie als Start — Persistenz im Composition-Overlay', async () => {
    const user = userEvent.setup()
    renderHost(
      <WorkspaceCompositionHost
        composition={WORKSPACE_COMPOSITION_FIXTURE}
        inboxQueue={[emptyQueueItem()]}
        variant="embedded"
      />,
    )

    await user.click(screen.getByRole('button', { name: 'Beleg-Inbox pinnen' }))
    await user.click(screen.getByRole('button', { name: 'Beleg-Inbox als Start fixieren' }))

    const inboxView = screen.getByTestId('workspace-composition-view-beleg-inbox-host')
    expect(inboxView).toHaveAttribute('data-view-pinned', 'true')
    expect(inboxView).toHaveAttribute('data-view-fixed-start', 'true')
    expect(inboxView).toHaveAttribute('data-view-order', '10')
    expect(screen.getByTestId('workspace-composition-host')).toHaveAttribute(
      'data-default-view-id',
      'beleg-inbox-host',
    )

    const slots = screen.getByTestId('workspace-specialist-slots')
    const slotNodes = slots.querySelectorAll('[data-specialized-kind]')
    expect(slotNodes[0]).toHaveAttribute('data-specialized-kind', 'inbox')
    expect(slotNodes[1]).toHaveAttribute('data-specialized-kind', 'disposition_board')

    expect(window.localStorage.getItem('valeo.workspace.composition.overlay')).toContain(
      'beleg-inbox-host',
    )
  })

  it('Fixture-Host: inbox + disposition_board zeichnet Stopp-Karte aus Tour-lat/lng', async () => {
    getMock.mockImplementation(async (url: string) => {
      if (url === '/api/v1/logistik/tours') {
        return { data: [{ id: 'tour-1', vehicle_id: 'LKW', status: 'GEPLANT' }] }
      }
      if (url === '/api/v1/logistik/tours/tour-1') {
        return {
          data: {
            id: 'tour-1',
            vehicle_id: 'LKW',
            stops: [{
              id: 'stop-1',
              planned_arrival: '2026-10-22T08:00:00.000Z',
              delivery_note_ref: 'LS-HOST',
              lat: 53.0793,
              lng: 8.8017,
            }],
          },
        }
      }
      return { data: { items: [] } }
    })

    renderHost(
      <WorkspaceCompositionHost
        composition={WORKSPACE_COMPOSITION_FIXTURE}
        inboxQueue={[emptyQueueItem()]}
      />,
    )

    expect(screen.getByTestId('workspace-composition-slot-slot-document-inbox')).toBeInTheDocument()
    expect(screen.getByTestId('adaptive-workspace-inbox')).toBeInTheDocument()
    expect(screen.getByTestId('disposition-board')).toBeInTheDocument()

    const marker = await screen.findByTestId('dispo-map-marker-stop-1')
    expect(marker).toHaveAttribute('data-lat', '53.0793')
    expect(marker).toHaveAttribute('data-lng', '8.8017')
    expect(screen.getByTestId('dispo-stop-map')).toBeInTheDocument()
    expect(screen.getByTestId('dispo-stop-coord-stop-1')).toHaveTextContent(
      `LS-HOST ${formatStopLatLng(53.0793, 8.8017)}`,
    )
    expect(maplibreProbe.options.length).toBeGreaterThan(0)
    for (const option of maplibreProbe.options) {
      expect(option.style?.sources?.osm?.tiles).toEqual([
        'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
      ])
    }
  })

  it('Preview: Slot abwählen remountet Host ohne diesen Slot', async () => {
    const user = userEvent.setup()
    renderHost(<WorkspaceCompositionPreviewPage />)

    expect(screen.getByTestId('workspace-composition-host')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-composition-slot-slot-document-inbox')).toBeInTheDocument()

    const inboxToggle = screen.getByTestId('workspace-composition-toggle-inbox').querySelector('input')
    expect(inboxToggle).toBeTruthy()
    await user.click(inboxToggle!)

    expect(screen.queryByTestId('workspace-composition-slot-slot-document-inbox')).not.toBeInTheDocument()
    expect(screen.getByTestId('workspace-composition-slot-slot-disposition-board')).toBeInTheDocument()
  })

  it('Preview: View nach oben verschieben ändert Host-Reihenfolge', async () => {
    const user = userEvent.setup()
    renderHost(<WorkspaceCompositionPreviewPage />)

    const viewsBefore = screen.getByTestId('workspace-composition-views')
    expect(viewsBefore.firstElementChild).toHaveAttribute(
      'data-testid',
      'workspace-composition-view-dispo-cockpit',
    )

    await user.click(screen.getByTestId('workspace-composition-view-up-beleg-inbox-host'))

    const viewsAfter = screen.getByTestId('workspace-composition-views')
    expect(viewsAfter.firstElementChild).toHaveAttribute(
      'data-testid',
      'workspace-composition-view-beleg-inbox-host',
    )
  })

  it('Preview: Speichern schreibt localStorage', async () => {
    const user = userEvent.setup()
    renderHost(<WorkspaceCompositionPreviewPage />)

    await user.click(screen.getByTestId('workspace-composition-toggle-inbox').querySelector('input')!)
    await user.click(screen.getByTestId('workspace-composition-save'))

    expect(screen.getByTestId('workspace-composition-save-ok')).toBeInTheDocument()
    const stored = localStorage.getItem(WORKSPACE_COMPOSITION_STORAGE_KEY)
    expect(stored).toBeTruthy()
    const parsed = JSON.parse(stored!) as typeof WORKSPACE_COMPOSITION_FIXTURE
    expect(parsed.specializedComponents.every((s) => s.kind !== 'inbox')).toBe(true)
  })

  it('Preview: ungültige Session zeigt Validatorfehler und mountet nicht', () => {
    localStorage.setItem(
      WORKSPACE_COMPOSITION_STORAGE_KEY,
      JSON.stringify({
        ...WORKSPACE_COMPOSITION_FIXTURE,
        specializedComponents: [
          {
            ...WORKSPACE_COMPOSITION_FIXTURE.specializedComponents[0],
            hostViewId: 'missing-view',
          },
        ],
      }),
    )

    renderHost(<WorkspaceCompositionPreviewPage />)

    expect(screen.getByTestId('workspace-composition-issues')).toBeInTheDocument()
    expect(screen.getByTestId('workspace-composition-host-skipped')).toBeInTheDocument()
    expect(screen.queryByTestId('workspace-composition-host')).not.toBeInTheDocument()
  })
})
