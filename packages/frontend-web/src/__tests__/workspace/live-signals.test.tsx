import { render, waitFor } from '@testing-library/react'
import { AxiosError } from 'axios'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { apiClient } from '@/lib/api-client'
import {
  APPROVAL_QUEUE_PATH,
  IST_EVENT_ACTIONS,
  WORKSPACE_SSE_URL,
  fetchWorkspaceQueueCounts,
  istTypeFromSsePayload,
  mergeHomeSignals,
  parseQueueCount,
  signalFromIstEvent,
  signalsFromQueueCounts,
  useWorkspaceLiveSignals,
} from '@/workspace/live-signals'
import { INBOX_SLOT } from '@/workspace/queue-contracts'
import { WORKSPACE_FACHAKTIONEN } from '@/workspace/registry'
import { emptyUserContext } from '@/workspace/user-context'
import { rankWorkspaceItems } from '@/workspace/prioritization'
import { defaultHomeSignals } from '@/workspace/home-signals'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}))

vi.mock('@/lib/auth', () => ({
  auth: {
    getAccessToken: () => 'workspace-live-fixture-jwt',
    getFreshAccessToken: async () => 'workspace-live-fixture-jwt',
  },
}))

const WORKSPACE_SSE_AUTH_URL = `${WORKSPACE_SSE_URL}&token=workspace-live-fixture-jwt`

class FakeEventSource {
  static instances: FakeEventSource[] = []
  static CONNECTING = 0
  static OPEN = 1
  static CLOSED = 2
  url: string
  readyState = FakeEventSource.CONNECTING
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

  close(): void {
    this.readyState = FakeEventSource.CLOSED
  }

  emit(data: unknown): void {
    this.readyState = FakeEventSource.OPEN
    const encoded = JSON.stringify(data)
    this.onmessage?.(new MessageEvent('message', { data: encoded }))
  }

  fail(): void {
    this.readyState = FakeEventSource.CLOSED
    this.onerror?.(new Event('error'))
  }
}

function HandlungsbedarfProbe({ now }: { now: Date }): JSX.Element {
  const signals = useWorkspaceLiveSignals(now)
  const ranked = rankWorkspaceItems({
    actions: WORKSPACE_FACHAKTIONEN,
    context: emptyUserContext({
      scopes: WORKSPACE_FACHAKTIONEN.flatMap((action) => action.requiredScopes),
    }),
    signals,
    now,
  }).slice(0, 5)
  return (
    <ul data-testid="workspace-work-items">
      {ranked.map((item) => (
        <li key={item.action.id} data-fachaktion-id={item.action.id}>
          {item.action.label}
          <span>{item.reasonCodes.join(' · ')}</span>
        </li>
      ))}
    </ul>
  )
}

describe('workspace live signals', () => {
  beforeEach(() => {
    FakeEventSource.instances = []
    vi.stubGlobal('EventSource', FakeEventSource)
    vi.mocked(apiClient.get).mockReset()
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('konsumiert Ist-Typen und ignoriert Soll-Rename', () => {
    expect(istTypeFromSsePayload({ type: 'connected', channel: 'workspace' })).toBeNull()
    expect(istTypeFromSsePayload({ type: 'assignment_confirmed' })).toBeNull()
    expect(istTypeFromSsePayload({ type: 'document_proposed' })).toBeNull()
    expect(istTypeFromSsePayload({ type: 'document_posted' })).toBeNull()
    expect(istTypeFromSsePayload({ type: 'sales.offer.created' })).toBeNull()
    expect(istTypeFromSsePayload({ type: 'finance.ap_invoice.approval_requested' })).toBe(
      'finance.ap_invoice.approval_requested',
    )
    expect(IST_EVENT_ACTIONS['logistik.tour.created']?.relatedActionIds).toEqual([
      'logistics.undispatched-truck-orders',
    ])
    expect(IST_EVENT_ACTIONS.LOADING_STARTED?.relatedActionIds).toEqual([
      'logistics.undispatched-truck-orders',
    ])
    expect(IST_EVENT_ACTIONS.LOADING_FINISHED?.relatedActionIds).toEqual([
      'logistics.undispatched-truck-orders',
    ])
    expect(istTypeFromSsePayload({ type: 'LOADING_STARTED' })).toBe('LOADING_STARTED')
    expect(signalFromIstEvent('LOADING_FINISHED')?.relatedActionIds).toEqual([
      'logistics.undispatched-truck-orders',
    ])
    expect(signalFromIstEvent('goods_receipt.created')?.relatedActionIds).toEqual([
      'procurement.goods-receipt-qty-variance',
    ])
    expect(signalFromIstEvent('docflow.document.posted')?.relatedActionIds).toEqual(['workspace.document-inbox'])
    expect(istTypeFromSsePayload({ type: 'agrar.quality_protocol.completed' })).toBe(
      'agrar.quality_protocol.completed',
    )
    expect(signalFromIstEvent('agrar.quality_protocol.completed')?.relatedActionIds).toEqual([
      'agrar.qualitaets-handlungsbedarf',
    ])
    expect(istTypeFromSsePayload({ type: 'agrar.weighing_ticket.allocated' })).toBe(
      'agrar.weighing_ticket.allocated',
    )
    expect(signalFromIstEvent('agrar.weighing_ticket.allocated')?.relatedActionIds).toEqual([
      'harvest.intake-queue',
    ])
    expect(istTypeFromSsePayload({ type: 'tenant1.agrar.weighing_ticket.completed' })).toBeNull()
    expect(istTypeFromSsePayload({ type: 'document_posted', ist_event_type: 'agrar.weighing_ticket.allocated' })).toBe(
      'agrar.weighing_ticket.allocated',
    )
  })

  it('baut Queue-Signale nur aus echten Counts und faellt sonst auf den Kalender zurueck', async () => {
    expect(parseQueueCount({ count: 3, items: [{ id: 'a' }] })).toBe(3)
    const approvalSignals = signalsFromQueueCounts({ inbox: 0, approval: 2 })
    expect(approvalSignals.map((signal) => signal.id)).toEqual(['queue-approval'])
    expect(approvalSignals[0]).toMatchObject({
      layer: 'proactive',
      reasonCodes: ['queue:approval', 'ops:freigabe'],
    })
    expect(signalFromIstEvent('finance.ap_invoice.approval_requested')?.reasonCodes).toEqual([
      'ops:freigabe',
      'ist:approval_requested',
    ])

    const calendar = defaultHomeSignals(new Date('2026-10-22T08:00:00'))
    expect(mergeHomeSignals(calendar, []).every((signal) => signal.source === 'calendar' || signal.source === 'clock')).toBe(
      true,
    )

    vi.mocked(apiClient.get).mockRejectedValue(
      new AxiosError('Unauthorized', 'ERR_BAD_REQUEST', undefined, undefined, {
        status: 401,
        statusText: 'Unauthorized',
        data: {},
        headers: {},
        config: { headers: {} as never },
      }),
    )
    expect(await fetchWorkspaceQueueCounts()).toBe('unavailable')
    expect(apiClient.get).toHaveBeenCalledWith(INBOX_SLOT.queueEndpoint)
    expect(apiClient.get).toHaveBeenCalledWith(APPROVAL_QUEUE_PATH)
  })

  it('aktualisiert den Handlungsbedarf bei finance.ap_invoice.approval_requested', async () => {
    vi.mocked(apiClient.get).mockRejectedValue(new AxiosError('Network Error', 'ERR_NETWORK'))
    const now = new Date('2026-10-22T08:00:00')
    const view = render(<HandlungsbedarfProbe now={now} />)

    await waitFor(() => {
      expect(FakeEventSource.instances[0]?.url).toBe(WORKSPACE_SSE_AUTH_URL)
    })
    expect(
      view.getByTestId('workspace-work-items').querySelector('[data-fachaktion-id="finance.invoices-awaiting-my-approval"]'),
    ).not.toHaveTextContent('signal:open-task')

    FakeEventSource.instances[0]?.emit({
      type: 'finance.ap_invoice.approval_requested',
      payload: { count: 4 },
    })

    await waitFor(() => {
      const row = view
        .getByTestId('workspace-work-items')
        .querySelector('[data-fachaktion-id="finance.invoices-awaiting-my-approval"]')
      expect(row).toBeTruthy()
      expect(row).toHaveTextContent('Rechnungen auf meine Freigabe')
      expect(row).toHaveTextContent('signal:open-task')
      expect(row).toHaveTextContent('count:4')
    })

    FakeEventSource.instances[0]?.fail()
    expect(view.getByTestId('workspace-work-items').textContent).toMatch(/Annahme-Warteschlange|Ueberfaellige/)
  })

  it('haengt LOADING_* an die Handlungsbedarf-Liste mit ops:verladung reasonCodes', async () => {
    expect(signalFromIstEvent('LOADING_STARTED')?.reasonCodes).toEqual([
      'ops:verladung',
      'ist:LOADING_STARTED',
    ])
    expect(signalFromIstEvent('LOADING_FINISHED')?.reasonCodes).toEqual([
      'ops:verladung',
      'ist:LOADING_FINISHED',
    ])

    vi.mocked(apiClient.get).mockRejectedValue(new AxiosError('Network Error', 'ERR_NETWORK'))
    const now = new Date('2026-10-22T08:00:00')
    const view = render(<HandlungsbedarfProbe now={now} />)

    await waitFor(() => {
      expect(FakeEventSource.instances[0]?.url).toBe(WORKSPACE_SSE_AUTH_URL)
    })

    FakeEventSource.instances[0]?.emit({
      type: 'LOADING_STARTED',
      payload: { tour_id: 'tour-9', count: 1 },
    })

    await waitFor(() => {
      const row = view
        .getByTestId('workspace-work-items')
        .querySelector('[data-fachaktion-id="logistics.undispatched-truck-orders"]')
      expect(row).toBeTruthy()
      expect(row).toHaveTextContent('ops:verladung')
      expect(row).toHaveTextContent('ist:LOADING_STARTED')
      expect(row).toHaveTextContent('signal:incident')
    })
  })
})
