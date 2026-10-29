import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { createRequire } from 'node:module'
import { AxiosError } from 'axios'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from '@/app/routing/test-router'
import { apiClient } from '@/lib/api-client'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { validateScreenDefinition } from '@/components/mask-builder/schema'
import { DispositionBoard, hasDispositionWriteClaim } from '@/components/mask-builder/specialized/disposition-board'
import { dispositionBoardScreen } from '@/components/mask-builder/specialized/disposition-board-screen'
import { registeredSpecializedTypes } from '@/components/mask-builder/specialized/registry'
import { DISPOSITION_BOARD_EVENTS } from '@/components/mask-builder/specialized/types'
import { orderDragId } from '@/components/mask-builder/specialized/board-dnd'
import { TIMELINE_FIELD_MISSING, formatStopLatLng } from '@/components/mask-builder/specialized/load-timeline'
import { QUANTITY_POST_FORBIDDEN, postDispositionAssignment } from '@/components/mask-builder/specialized/post-assignment'
import type { User } from '@/lib/auth'
import {
  OPS_AUTH_ERROR,
  WEIGHING_TICKETS_ENDPOINT,
} from '@/components/mask-builder/specialized/ops-signals'
import {
  SSE_AUTH_ERROR,
  WORKSPACE_TOUR_SSE_URL,
} from '@/components/mask-builder/specialized/workspace-tour-sse'

const toast = vi.hoisted(() => vi.fn())
const authToken = vi.hoisted(() => ({ value: 'dispo-fixture-jwt' as string | null }))

type AxeResult = { violations: Array<{ id: string }> }
type AxeApi = {
  run: (context: Element, options: { runOnly: { type: 'rule'; values: string[] } }) => Promise<AxeResult>
}
const testRequire = createRequire(import.meta.url)
const axePlaywrightRequire = createRequire(testRequire.resolve('@axe-core/playwright'))
const axe = axePlaywrightRequire('axe-core') as AxeApi
const authUser = vi.hoisted(() => ({
  value: {
    sub: 'dispatcher', name: 'Dispatcher', email: 'dispatcher@example.invalid',
    exp: 9999999999, scopes: ['logistics.write'], roles: ['disponent'],
  } as User | null,
}))

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({ user: authUser.value }),
}))

vi.mock('@/lib/auth', () => ({
  auth: {
    getAccessToken: () => authToken.value,
  },
}))
const maplibreProbe = vi.hoisted(() => ({
  options: [] as Array<{ style?: { sources?: { osm?: { tiles?: string[] } } } }>,
}))

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({ toast }),
}))

vi.mock('maplibre-gl', () => {
  class Marker {
    element: HTMLElement
    constructor(opts?: { element?: HTMLElement }) {
      this.element = opts?.element ?? document.createElement('div')
    }
    setLngLat(): this { return this }
    addTo(map: { getContainer: () => HTMLElement }): this {
      map.getContainer().appendChild(this.element)
      return this
    }
    remove(): void { this.element.remove() }
  }
  class Map {
    private readonly container: HTMLElement
    constructor(opts: { container: HTMLElement; style?: { sources?: { osm?: { tiles?: string[] } } } }) {
      this.container = opts.container
      maplibreProbe.options.push(opts)
    }
    getContainer(): HTMLElement { return this.container }
    on(event: string, cb: () => void): void {
      if (event === 'load') cb()
    }
    remove(): void {}
    fitBounds(): void {}
  }
  return { Map, Marker }
})

class FakeEventSource {
  static instances: FakeEventSource[] = []
  url: string
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  private readonly listeners = new Map<string, Set<(event: Event) => void>>()

  constructor(url: string) {
    this.url = url
    FakeEventSource.instances.push(this)
  }

  addEventListener(type: string, listener: (event: Event) => void): void {
    const bucket = this.listeners.get(type) ?? new Set()
    bucket.add(listener)
    this.listeners.set(type, bucket)
  }

  removeEventListener(type: string, listener: (event: Event) => void): void {
    this.listeners.get(type)?.delete(listener)
  }

  close(): void {}

  emit(data: unknown): void {
    const encoded = typeof data === 'string' ? data : JSON.stringify(data)
    this.onmessage?.(new MessageEvent('message', { data: encoded }))
  }

  fail(): void {
    this.onerror?.(new Event('error'))
  }
}

function wrap(node: JSX.Element): JSX.Element {
  return (
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter>{node}</MemoryRouter>
    </QueryClientProvider>
  )
}

const fixture = {
  orders: [
    { id: 'ord-1', label: 'Weizen LS-1001', quantity: 12, contractId: 'K-1' },
    { id: 'ord-2', label: 'Gerste LS-1002', quantity: 8, contractId: 'K-2' },
    {
      id: 'abruf-1',
      label: 'K-100 Abruf 1',
      quantity: 12,
      contractId: 'c1',
      abrufId: 'abruf-1',
    },
  ],
  resources: [{ id: 'tour-1', label: 'LKW HH-AB 123', driver: 'Meier', status: 'geplant' }],
  operations: [
    { id: 'waage', label: 'Waage offen', value: '2', tone: 'warning' as const },
    { id: 'stoerung', label: 'Gesperrte Chargen', value: '0', tone: 'neutral' as const },
  ],
}

function dropOnTour(orderId = 'ord-1') {
  fireEvent.drop(screen.getByTestId('dispo-resource-tour-1'), {
    dataTransfer: { getData: () => orderDragId(orderId) },
  })
}

describe('disposition_board specialized component', () => {
  beforeEach(() => {
    toast.mockReset()
    maplibreProbe.options = []
    authToken.value = 'dispo-fixture-jwt'
    authUser.value = {
      sub: 'dispatcher', name: 'Dispatcher', email: 'dispatcher@example.invalid',
      exp: 9999999999, scopes: ['logistics.write'], roles: ['disponent'],
    }
    vi.restoreAllMocks()
    FakeEventSource.instances = []
    vi.stubGlobal('EventSource', FakeEventSource)
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('registriert nur den Typ disposition_board', () => {
    expect(registeredSpecializedTypes()).toEqual(['disposition_board'])
    expect(validateScreenDefinition(dispositionBoardScreen)).toEqual([])
    expect(dispositionBoardScreen.specialized?.type).toBe('disposition_board')
    expect(dispositionBoardScreen.specialized?.id).toBe('lkw-disposition-board')
    expect(dispositionBoardScreen.specialized?.liveChannel).toBe('disposition.board')
  })

  it('leitet Dispo-Schreibrecht nur aus Token-Claims ab', () => {
    const base = { sub: 'test', name: 'Test', email: 'test@example.invalid', exp: 9999999999 }
    expect(hasDispositionWriteClaim(null)).toBe(false)
    expect(hasDispositionWriteClaim({ ...base, scopes: [], roles: [] })).toBe(false)
    expect(hasDispositionWriteClaim({ ...base, scopes: ['logistics.read'], roles: [] })).toBe(false)
    expect(hasDispositionWriteClaim({ ...base, scopes: ['logistics.write'], roles: [] })).toBe(true)
    expect(hasDispositionWriteClaim({ ...base, scopes: [], roles: ['disponent'] })).toBe(true)
    expect(hasDispositionWriteClaim({ ...base, scopes: [], roles: ['CRM_BEARBEITEN'] })).toBe(false)
  })

  it('lehnt andere specialized-Typen in der ScreenDefinition ab', () => {
    const invalid = {
      ...dispositionBoardScreen,
      specialized: { type: 'gantt_chart' as never, id: 'x' },
    }
    expect(validateScreenDefinition(invalid)).toContain('specialized.type is invalid: gantt_chart')
  })

  it('rendert die drei Sichten im UniversalMaskRenderer', () => {
    vi.spyOn(apiClient, 'get').mockResolvedValue({ data: { items: [] } } as never)
    const plan = compileRenderPlanFromScreenDefinition(dispositionBoardScreen)
    expect(plan.specialized?.type).toBe('disposition_board')
    render(wrap(<UniversalMaskRenderer plan={plan} />))
    expect(screen.getByTestId('disposition-board')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Aufträge / Kontrakte' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Ressourcen / Planung' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Betriebszustände' })).toBeInTheDocument()
    expect(screen.getByText('/logistik/tourenplanung')).toBeInTheDocument()
    expect(FakeEventSource.instances[0]?.url).toBe(
      `${WORKSPACE_TOUR_SSE_URL}&token=dispo-fixture-jwt`,
    )
  })

  it('verbindet Live-SSE nicht ohne Token und zeigt den Auth-Hinweis', async () => {
    authToken.value = null
    vi.spyOn(apiClient, 'get').mockResolvedValue({ data: { items: [] } } as never)
    render(wrap(
      <DispositionBoard contract={dispositionBoardScreen.specialized!} />,
    ))
    expect(FakeEventSource.instances).toHaveLength(0)
    expect(await screen.findByTestId('dispo-sse-error')).toHaveTextContent(SSE_AUTH_ERROR)
    expect(screen.getByTestId('disposition-board')).toBeInTheDocument()
  })

  it('sendet trotz Schreibrolle und deklarierter Berechtigung keinen Drop-POST vor Capability-Freigabe', () => {
    const onAction = vi.fn()
    const post = vi.spyOn(apiClient, 'post')
    render(wrap(
      <DispositionBoard
        contract={dispositionBoardScreen.specialized!}
        onAction={onAction}
        model={fixture}
      />,
    ))
    expect(screen.getByTestId('dispo-preview-notice')).toHaveTextContent('Zuweisungen sind noch nicht freigegeben')
    dropOnTour()
    expect(post).not.toHaveBeenCalled()
    expect(onAction).not.toHaveBeenCalled()
    expect(toast).not.toHaveBeenCalled()
    expect(screen.queryByTestId('dispo-feedback')).not.toBeInTheDocument()
  })

  it('zeigt bei fehlendem Nutzerscope keine Bestätigung; der isolierte Client erhält weiterhin 422', async () => {
    authUser.value = null
    const onAction = vi.fn()
    const error = new AxiosError('Unprocessable Entity')
    error.response = {
      status: 422,
      statusText: 'Unprocessable Entity',
      headers: {},
      config: {} as never,
      data: {
        detail: {
          ok: false,
          issues: [{
            code: QUANTITY_POST_FORBIDDEN,
            message: 'Kontraktmengen werden nicht beim Drop gebucht, sondern erst beim fachlichen Buchungsereignis.',
          }],
        },
      },
    }
    const post = vi.spyOn(apiClient, 'post').mockRejectedValue(error)
    render(wrap(
      <DispositionBoard
        contract={dispositionBoardScreen.specialized!}
        onAction={onAction}
        model={fixture}
      />,
    ))
    dropOnTour()
    expect(post).not.toHaveBeenCalled()
    expect(onAction.mock.calls.some((call) => call[0] === DISPOSITION_BOARD_EVENTS.assignmentConfirmed)).toBe(false)
    expect(onAction.mock.calls.some((call) => call[0] === DISPOSITION_BOARD_EVENTS.quantityPosted)).toBe(false)
    expect(screen.getByTestId('dispo-preview-notice')).toBeInTheDocument()
    expect(screen.getByTestId('dispo-order-ord-2')).toBeDisabled()
    await expect(postDispositionAssignment({ orderId: 'ord-1', resourceId: 'tour-1', tenantId: 'tenant-1' }))
      .rejects.toMatchObject({ code: QUANTITY_POST_FORBIDDEN, status: 422 })
  })

  it('zeigt vorhandene Abrufe als Quelle ohne sie per Drop zuzuweisen', () => {
    const post = vi.spyOn(apiClient, 'post')
    render(wrap(
      <DispositionBoard
        contract={dispositionBoardScreen.specialized!}
        model={fixture}
      />,
    ))
    expect(screen.getByTestId('dispo-order-abruf-1')).toHaveTextContent('K-100 Abruf 1')
    dropOnTour('abruf-1')
    expect(post).not.toHaveBeenCalled()
  })

  it('lädt Abrufe live über GET dispositionen', async () => {
    vi.spyOn(apiClient, 'get').mockImplementation(async (url: string) => {
      if (url === '/api/v1/kontrakte') {
        return { data: { items: [{ contract_id: 'c1' }], total: 1 } } as never
      }
      if (url === '/api/v1/kontrakte/c1/dispositionen') {
        return {
          data: [{
            id: 'abruf-live',
            kontrakt_id: 'c1',
            kontrakt_nr: 'K-100',
            disposition_nr: 3,
            menge: 9,
            status: 'OFFEN',
          }],
        } as never
      }
      return { data: [] } as never
    })
    render(wrap(
      <DispositionBoard contract={dispositionBoardScreen.specialized!} />,
    ))
    expect(await screen.findByTestId('dispo-order-abruf-live')).toHaveTextContent('K-100 Abruf 3')
  })

  it('zeigt ehrlichen Fehler statt leerer Abruf-Liste bei 403', async () => {
    const error = new AxiosError('Forbidden')
    error.response = {
      status: 403,
      statusText: 'Forbidden',
      headers: {},
      config: {} as never,
      data: { detail: 'denied' },
    }
    vi.spyOn(apiClient, 'get').mockImplementation(async (url: string) => {
      if (String(url).startsWith('/api/v1/kontrakte')) throw error
      return { data: [] } as never
    })
    render(wrap(
      <DispositionBoard contract={dispositionBoardScreen.specialized!} />,
    ))
    expect(await screen.findByTestId('dispo-orders-error')).toHaveTextContent(
      'Abrufe nicht lesbar: Recht oder Anmeldung fehlt.',
    )
  })

  it('behält Listensemantik und innere Alerts bei Abruf- und Waagenfehlern', async () => {
    const error = new AxiosError('Forbidden')
    error.response = {
      status: 403,
      statusText: 'Forbidden',
      headers: {},
      config: {} as never,
      data: { detail: 'denied' },
    }
    vi.spyOn(apiClient, 'get').mockImplementation(async (url: string) => {
      if (String(url).startsWith('/api/v1/kontrakte') || url === WEIGHING_TICKETS_ENDPOINT) {
        throw error
      }
      return { data: [] } as never
    })

    const { container } = render(wrap(
      <DispositionBoard contract={dispositionBoardScreen.specialized!} />,
    ))
    const ordersError = await screen.findByTestId('dispo-orders-error')
    const operationsError = await screen.findByTestId('dispo-ops-error')

    for (const errorItem of [ordersError, operationsError]) {
      expect(errorItem.tagName).toBe('LI')
      expect(errorItem.closest('ul')).toBeTruthy()
      expect(errorItem.getAttribute('role')).not.toBe('alert')
      expect(errorItem.querySelector('[role="alert"]')).toBeTruthy()
    }

    const { violations } = await axe.run(container, {
      runOnly: { type: 'rule', values: ['list', 'listitem', 'aria-required-children'] },
    })
    expect(violations).toEqual([])
  })

  it('lädt Aufträge und Ressourcen nach SSE logistik.tour.created neu', async () => {
    const get = vi.spyOn(apiClient, 'get').mockImplementation(async (url: string) => {
      if (url === '/api/v1/kontrakte') {
        return { data: { items: [{ contract_id: 'c1' }], total: 1 } } as never
      }
      if (url === '/api/v1/kontrakte/c1/dispositionen') {
        return {
          data: [{
            id: 'abruf-live',
            kontrakt_id: 'c1',
            kontrakt_nr: 'K-100',
            disposition_nr: 3,
            menge: 9,
            status: 'OFFEN',
          }],
        } as never
      }
      if (url === '/api/v1/logistik/tours') {
        return { data: [{ id: 'tour-1', vehicle_id: 'LKW', driver_id: 'Meier', status: 'GEPLANT' }] } as never
      }
      return { data: [] } as never
    })
    render(wrap(
      <DispositionBoard contract={dispositionBoardScreen.specialized!} />,
    ))
    expect(await screen.findByTestId('dispo-order-abruf-live')).toBeInTheDocument()
    get.mockClear()
    FakeEventSource.instances[0]?.emit({ type: 'assignment_confirmed' })
    FakeEventSource.instances[0]?.emit({ type: 'logistik.tour.created', event_type: 'logistik.tour.created' })
    await waitFor(() => {
      expect(get).toHaveBeenCalledWith('/api/v1/kontrakte', expect.anything())
      expect(get).toHaveBeenCalledWith('/api/v1/logistik/tours')
    })
  })

  it('lädt nach einem gesperrten Drop nicht neu, aber weiterhin nach einem Server-Ereignis', async () => {
    const get = vi.spyOn(apiClient, 'get').mockImplementation(async (url: string) => {
      if (url === '/api/v1/kontrakte') {
        return { data: { items: [{ contract_id: 'c1' }], total: 1 } } as never
      }
      if (url === '/api/v1/kontrakte/c1/dispositionen') {
        return {
          data: [{
            id: 'abruf-live',
            kontrakt_id: 'c1',
            kontrakt_nr: 'K-100',
            disposition_nr: 3,
            menge: 9,
            status: 'OFFEN',
          }],
        } as never
      }
      if (url === '/api/v1/logistik/tours') {
        return { data: [{ id: 'tour-1', vehicle_id: 'LKW', driver_id: 'Meier', status: 'GEPLANT' }] } as never
      }
      return { data: [] } as never
    })
    const post = vi.spyOn(apiClient, 'post')
    render(wrap(
      <DispositionBoard contract={dispositionBoardScreen.specialized!} />,
    ))
    expect(await screen.findByTestId('dispo-order-abruf-live')).toBeInTheDocument()
    expect(await screen.findByTestId('dispo-resource-tour-1')).toBeInTheDocument()
    get.mockClear()
    dropOnTour('abruf-live')
    expect(post).not.toHaveBeenCalled()
    expect(get).not.toHaveBeenCalled()
    FakeEventSource.instances[0]?.emit({ type: 'logistik.tour.created', event_type: 'logistik.tour.created' })
    await waitFor(() => {
      expect(get).toHaveBeenCalledWith('/api/v1/kontrakte', expect.anything())
      expect(get).toHaveBeenCalledWith('/api/v1/logistik/tours')
    })
  })

  it('zeigt geplante Ankunftszeiten auf der Zeitachse und sperrt auch dort Drop-POST', async () => {
    vi.spyOn(apiClient, 'get').mockImplementation(async (url: string) => {
      if (url === '/api/v1/kontrakte') {
        return { data: { items: [{ contract_id: 'c1' }], total: 1 } } as never
      }
      if (url === '/api/v1/kontrakte/c1/dispositionen') {
        return {
          data: [{
            id: 'abruf-live',
            kontrakt_id: 'c1',
            kontrakt_nr: 'K-100',
            disposition_nr: 3,
            menge: 9,
            status: 'OFFEN',
          }],
        } as never
      }
      if (url === '/api/v1/logistik/tours') {
        return { data: [{ id: 'tour-1', vehicle_id: 'LKW', driver_id: 'Meier', status: 'GEPLANT' }] } as never
      }
      if (url === '/api/v1/logistik/tours/tour-1') {
        return {
          data: {
            id: 'tour-1',
            vehicle_id: 'LKW',
            stops: [{
              id: 'stop-1',
              planned_arrival: '2026-10-22T08:00:00.000Z',
              delivery_note_ref: 'LS-1',
            }],
          },
        } as never
      }
      return { data: [] } as never
    })
    const post = vi.spyOn(apiClient, 'post')
    render(wrap(
      <DispositionBoard contract={dispositionBoardScreen.specialized!} />,
    ))
    expect(await screen.findByTestId('dispo-timeline-stop-stop-1')).toBeInTheDocument()
    expect(screen.queryByTestId('dispo-map-marker-stop-1')).not.toBeInTheDocument()
    expect(screen.queryByTestId('dispo-stop-map')).not.toBeInTheDocument()
    fireEvent.drop(screen.getByTestId('dispo-timeline-tour-1'), {
      dataTransfer: { getData: () => orderDragId('abruf-live') },
    })
    expect(post).not.toHaveBeenCalled()
  })

  it('zeigt ehrlichen Leerzustand wenn planned_arrival fehlt', async () => {
    vi.spyOn(apiClient, 'get').mockImplementation(async (url: string) => {
      if (url === '/api/v1/logistik/tours') {
        return { data: [{ id: 'tour-1', vehicle_id: 'LKW', status: 'GEPLANT' }] } as never
      }
      if (url === '/api/v1/logistik/tours/tour-1') {
        return { data: { id: 'tour-1', stops: [{ id: 'stop-1', planned_arrival: null }] } } as never
      }
      return { data: { items: [] } } as never
    })
    render(wrap(
      <DispositionBoard contract={dispositionBoardScreen.specialized!} />,
    ))
    expect(await screen.findByTestId('dispo-timeline-empty')).toHaveTextContent(TIMELINE_FIELD_MISSING)
    expect(screen.queryByTestId('dispo-map-marker-stop-1')).not.toBeInTheDocument()
    expect(screen.queryByTestId('dispo-stop-map')).not.toBeInTheDocument()
  })

  it('zeichnet vorhandene lat/lng als Kartenmarker', async () => {
    vi.spyOn(apiClient, 'get').mockImplementation(async (url: string) => {
      if (url === '/api/v1/logistik/tours') {
        return { data: [{ id: 'tour-1', vehicle_id: 'LKW', status: 'GEPLANT' }] } as never
      }
      if (url === '/api/v1/logistik/tours/tour-1') {
        return {
          data: {
            id: 'tour-1',
            vehicle_id: 'LKW',
            stops: [{
              id: 'stop-1',
              planned_arrival: '2026-10-22T08:00:00.000Z',
              delivery_note_ref: 'LS-1',
              lat: 53.0793,
              lng: 8.8017,
            }],
          },
        } as never
      }
      return { data: { items: [] } } as never
    })
    render(wrap(
      <DispositionBoard contract={dispositionBoardScreen.specialized!} />,
    ))
    const coord = formatStopLatLng(53.0793, 8.8017)
    const marker = await screen.findByTestId('dispo-map-marker-stop-1')
    expect(marker).toHaveAttribute('data-lat', '53.0793')
    expect(marker).toHaveAttribute('data-lng', '8.8017')
    expect(maplibreProbe.options.length).toBeGreaterThan(0)
    for (const option of maplibreProbe.options) {
      expect(option.style?.sources?.osm?.tiles).toEqual(['https://tile.openstreetmap.org/{z}/{x}/{y}.png'])
    }
    expect(screen.getByTestId('dispo-stop-coord-stop-1')).toHaveTextContent(`LS-1 ${coord}`)
    expect(screen.getByTestId('dispo-timeline-stop-stop-1')).toHaveAttribute('data-lat', '53.0793')
    expect(screen.getByTestId('dispo-timeline-stop-stop-1')).toHaveAttribute('data-lng', '8.8017')
    expect(screen.getByTestId('dispo-map-note')).toHaveTextContent('nur lat/lng aus der Tour')
  })

  it('hält die Tafel bei SSE-401 und zeigt den Fehler', async () => {
    vi.spyOn(apiClient, 'get').mockResolvedValue({ data: { items: [] } } as never)
    render(wrap(
      <DispositionBoard contract={dispositionBoardScreen.specialized!} />,
    ))
    expect(screen.getByTestId('disposition-board')).toBeInTheDocument()
    FakeEventSource.instances[0]?.fail()
    expect(await screen.findByTestId('dispo-sse-error')).toHaveTextContent(SSE_AUTH_ERROR)
    expect(screen.getByTestId('disposition-board')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Aufträge / Kontrakte' })).toBeInTheDocument()
  })

  it('zeigt offene Wiegescheine als Waage belegt statt erfundener KPIs', async () => {
    vi.spyOn(apiClient, 'get').mockImplementation(async (url: string) => {
      if (url === WEIGHING_TICKETS_ENDPOINT) {
        return {
          data: {
            items: [{
              id: 't-1',
              ticket_number: 'WS-1',
              vehicle_plate: 'HH-AB 123',
              status: 'open',
              first_weighing_at: '2026-10-22T08:15:00.000Z',
            }],
          },
        } as never
      }
      return { data: { items: [] } } as never
    })
    render(wrap(
      <DispositionBoard contract={dispositionBoardScreen.specialized!} />,
    ))
    expect(await screen.findByTestId('dispo-ops-waage-t-1')).toHaveTextContent('Waage belegt')
    expect(screen.getByTestId('dispo-ops-waage-t-1').textContent).toMatch(/\d{1,2}:\d{2}/)
    expect(screen.queryByText('Verladung unterwegs')).not.toBeInTheDocument()
    expect(screen.queryByText('Gesperrte Chargen')).not.toBeInTheDocument()
    expect(screen.queryByText('Waage offen')).not.toBeInTheDocument()
  })

  it('hängt SSE Waage belegt und Einlagerung mit Zeit an', async () => {
    vi.spyOn(apiClient, 'get').mockResolvedValue({ data: { items: [] } } as never)
    render(wrap(
      <DispositionBoard contract={dispositionBoardScreen.specialized!} />,
    ))
    expect(await screen.findByTestId('dispo-ops-empty')).toBeInTheDocument()
    FakeEventSource.instances[0]?.emit({
      type: 'agrar.weighing_ticket.allocated',
      payload: { ticket_id: 't-9', timestamp: '2026-10-22T09:00:00.000Z' },
    })
    FakeEventSource.instances[0]?.emit({
      type: 'lager.einlagerung.created',
      payload: { id: 'ein-1', created_at: '2026-10-22T09:05:00.000Z' },
    })
    FakeEventSource.instances[0]?.emit({ type: 'assignment_confirmed' })
    expect(await screen.findByTestId('dispo-ops-waage-t-9')).toHaveTextContent('Waage belegt')
    expect(screen.getByTestId('dispo-ops-lager-ein-1')).toHaveTextContent('Einlagerung')
    expect(screen.getByTestId('dispo-ops-waage-t-9').textContent).toMatch(/\d{1,2}:\d{2}/)
    expect(screen.getByTestId('dispo-ops-lager-ein-1').textContent).toMatch(/\d{1,2}:\d{2}/)
  })

  it('zeigt 401 der Waagenbelegung und hält die Tafel', async () => {
    const error = new AxiosError('Unauthorized')
    error.response = {
      status: 401,
      statusText: 'Unauthorized',
      headers: {},
      config: {} as never,
      data: { detail: 'denied' },
    }
    vi.spyOn(apiClient, 'get').mockImplementation(async (url: string) => {
      if (url === WEIGHING_TICKETS_ENDPOINT) throw error
      return { data: { items: [] } } as never
    })
    render(wrap(
      <DispositionBoard contract={dispositionBoardScreen.specialized!} />,
    ))
    expect(await screen.findByTestId('dispo-ops-error')).toHaveTextContent(OPS_AUTH_ERROR)
    expect(screen.getByTestId('disposition-board')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Aufträge / Kontrakte' })).toBeInTheDocument()
  })
})
