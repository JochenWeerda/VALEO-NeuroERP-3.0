/**
 * FEED-MOB-045 (TDD-Red-Welle 2): Offline-Fallback der mobilen
 * Ist-Dokumentation — Netzwerkfehler reiht in die Queue ein (sichtbar),
 * Replay beim Mount nutzt dieselbe API mit fixiertem idempotency_key.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import MobileFuetterungsdokumentation from '@/pages/futtermittel/fuetterungsdokumentation-mobil'
import { FEEDING_OFFLINE_QUEUE_KEY } from '@/lib/offline/feeding-offline-queue'

const recordActualFeedingMock = vi.hoisted(() => vi.fn())
const fetchActualFeedingsMock = vi.hoisted(() => vi.fn())
const fetchCurrentFeedingPlansMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api/feeding-actual', () => ({
  fetchActualFeedings: fetchActualFeedingsMock,
  recordActualFeeding: recordActualFeedingMock,
}))

vi.mock('@/lib/api/feeding-plans', () => ({
  fetchCurrentFeedingPlans: fetchCurrentFeedingPlansMock,
}))

const PLAN = {
  id: 'pv-1', version_no: 3, plan_status: 'current', published_at: '2026-07-16T06:00:00Z',
  group_id: 'g-1', group_name: 'Hochleistung', animal_count: 60, dosing_step_kg: '5',
  instructions: [{ feed_id: 'f-gras', feed_name: 'Grassilage', target_batch_kg: '120' }],
}

function networkError(): Error {
  const error = new Error('Network Error') as Error & { request?: unknown }
  error.request = {}
  return error
}

function renderPage(): void {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  render(
    <QueryClientProvider client={client}>
      <MobileFuetterungsdokumentation />
    </QueryClientProvider>,
  )
}

describe('Mobile Ist-Dokumentation offline (FEED-MOB-045)', () => {
  beforeEach(() => {
    localStorage.clear()
    recordActualFeedingMock.mockReset()
    fetchActualFeedingsMock.mockReset()
    fetchCurrentFeedingPlansMock.mockReset()
    fetchActualFeedingsMock.mockResolvedValue([])
    fetchCurrentFeedingPlansMock.mockResolvedValue([PLAN])
  })

  it('reiht bei Netzwerkfehler sichtbar in die Offline-Queue ein statt zu verlieren', async () => {
    recordActualFeedingMock.mockRejectedValue(networkError())
    renderPage()

    await userEvent.click(await screen.findByRole('button', { name: /Jetzt füttern/ }))
    await userEvent.click(screen.getByRole('button', { name: /Ist-Fütterung speichern/ }))

    expect(await screen.findByText(/Offline gespeichert/)).toBeInTheDocument()
    const stored = JSON.parse(localStorage.getItem(FEEDING_OFFLINE_QUEUE_KEY) ?? '[]')
    expect(stored).toHaveLength(1)
    expect(stored[0].payload.plan_version_id).toBe('pv-1')
    expect(stored[0].payload.idempotency_key).toMatch(/^mobile-actual-/)
  })

  it('replayt beim Mount ausstehende Eintraege ueber dieselbe API', async () => {
    localStorage.setItem(FEEDING_OFFLINE_QUEUE_KEY, JSON.stringify([{
      id: 'q-1', kind: 'actual_feeding', status: 'pending', attempts: 0,
      enqueued_at: '2026-07-17T05:00:00Z',
      payload: { plan_version_id: 'pv-1', idempotency_key: 'mobile-actual-old',
                 source: 'manual', source_ref: 'mobile:old', cause_class: 'normal',
                 comment: null, supersedes_id: null, context: {},
                 feeding_at: '2026-07-17T05:00:00Z',
                 components: [{ feed_id: 'f-gras', actual_kg: 118 }] },
    }]))
    recordActualFeedingMock.mockResolvedValue({ id: 'r-1', components: [] })
    renderPage()

    await waitFor(() => {
      expect(recordActualFeedingMock).toHaveBeenCalledWith(
        expect.objectContaining({ idempotency_key: 'mobile-actual-old' }))
    })
    await waitFor(() => {
      expect(JSON.parse(localStorage.getItem(FEEDING_OFFLINE_QUEUE_KEY) ?? '[]')).toHaveLength(0)
    })
  })

  it('zeigt Konflikte (Plan veraltet) sichtbar an statt blind erneut zu senden', async () => {
    localStorage.setItem(FEEDING_OFFLINE_QUEUE_KEY, JSON.stringify([{
      id: 'q-1', kind: 'actual_feeding', status: 'conflict', attempts: 1,
      enqueued_at: '2026-07-17T05:00:00Z', last_error: 'Planversion ist veraltet.',
      payload: { plan_version_id: 'pv-0', idempotency_key: 'mobile-actual-stale',
                 source: 'manual', source_ref: 'mobile:stale', cause_class: 'normal',
                 comment: null, supersedes_id: null, context: {},
                 feeding_at: '2026-07-17T05:00:00Z',
                 components: [{ feed_id: 'f-gras', actual_kg: 100 }] },
    }]))
    renderPage()

    expect(await screen.findByText(/Planversion ist veraltet/)).toBeInTheDocument()
    expect(recordActualFeedingMock).not.toHaveBeenCalled()
  })
})
