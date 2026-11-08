import { describe, expect, it, vi, afterEach } from 'vitest'
import { AxiosError } from 'axios'
import { apiClient } from '@/lib/api-client'
import {
  EINLAGERUNG_IST,
  GOODS_RECEIPT_IST,
  LOADING_FINISHED_IST,
  LOADING_STARTED_IST,
  OPS_AUTH_ERROR,
  WAAGE_ALLOCATED_IST,
  WEIGHING_TICKETS_ENDPOINT,
  fetchOpenScaleOccupancy,
  mergeOpsSignals,
  occupancyFromTickets,
  opsSignalFromSse,
} from '@/components/mask-builder/specialized/ops-signals'

afterEach(() => {
  vi.restoreAllMocks()
})

function axiosError(status: number): AxiosError {
  const error = new AxiosError('request failed')
  error.response = {
    status,
    statusText: 'Error',
    headers: {},
    config: {} as never,
    data: { detail: 'denied' },
  }
  return error
}

describe('ops-signals', () => {
  it('macht Waage- und Einlagerungs-Ist zu Zeilen mit Zeit', () => {
    expect(opsSignalFromSse({
      type: WAAGE_ALLOCATED_IST,
      payload: { ticket_id: 't-1', timestamp: '2026-10-22T08:15:00.000Z' },
    })).toEqual(expect.objectContaining({
      id: 'waage:t-1',
      label: 'Waage belegt',
      at: '2026-10-22T08:15:00.000Z',
    }))
    expect(opsSignalFromSse({
      event_type: EINLAGERUNG_IST,
      payload: { id: 'ein-1', created_at: '2026-10-22T09:00:00.000Z' },
    })?.label).toBe('Einlagerung')
    expect(opsSignalFromSse({
      type: GOODS_RECEIPT_IST,
      payload: { receiptId: 'gr-1', receivedDate: '2026-10-22T10:00:00.000Z' },
    })?.label).toBe('Einlagerung')
    expect(opsSignalFromSse({
      type: LOADING_STARTED_IST,
      payload: { tour_id: 'tour-9', timestamp: '2026-10-23T11:00:00.000Z' },
    })).toEqual(expect.objectContaining({
      id: 'verladung:tour-9',
      kind: 'verladung',
      label: 'Verladung gestartet',
      at: '2026-10-23T11:00:00.000Z',
    }))
    expect(opsSignalFromSse({
      event_type: LOADING_FINISHED_IST,
      payload: { id: 'tour-9' },
    })?.label).toBe('Verladung beendet')
    expect(opsSignalFromSse({ type: 'assignment_confirmed' })).toBeNull()
  })

  it('liest offene Wiegescheine als Waage belegt, keine geschlossenen', () => {
    expect(occupancyFromTickets([
      {
        id: 't-open',
        ticket_number: 'WS-1',
        vehicle_plate: 'HH-AB 123',
        status: 'open',
        first_weighing_at: '2026-10-22T07:30:00.000Z',
      },
      { id: 't-closed', ticket_number: 'WS-2', status: 'closed', first_weighing_at: '2026-10-22T06:00:00.000Z' },
    ])).toEqual([{
      id: 'waage:t-open',
      kind: 'waage',
      label: 'Waage belegt',
      at: '2026-10-22T07:30:00.000Z',
      detail: 'HH-AB 123',
    }])
  })

  it('holt die Belegung über GET weighing-tickets', async () => {
    const get = vi.spyOn(apiClient, 'get').mockResolvedValue({
      data: {
        items: [{
          id: 't-1',
          ticket_number: 'WS-9',
          status: 'open',
          first_weighing_at: '2026-10-22T08:00:00.000Z',
        }],
      },
    } as never)
    await expect(fetchOpenScaleOccupancy()).resolves.toEqual([
      expect.objectContaining({ id: 'waage:t-1', label: 'Waage belegt' }),
    ])
    expect(get).toHaveBeenCalledWith(WEIGHING_TICKETS_ENDPOINT, { params: { limit: 100 } })
  })

  it('macht 401 am Wiegeschein-GET sichtbar', async () => {
    vi.spyOn(apiClient, 'get').mockRejectedValue(axiosError(401))
    await expect(fetchOpenScaleOccupancy()).rejects.toThrow(OPS_AUTH_ERROR)
  })

  it('hängt SSE-Zeilen vor den GET-Stand und dedupliziert', () => {
    const occupancy = occupancyFromTickets([{ id: 't-1', status: 'open', ticket_number: 'WS-1' }])
    const live = opsSignalFromSse({
      type: WAAGE_ALLOCATED_IST,
      payload: { ticket_id: 't-1', timestamp: '2026-10-22T08:15:00.000Z' },
    })
    const extra = opsSignalFromSse({
      type: EINLAGERUNG_IST,
      payload: { id: 'ein-1', created_at: '2026-10-22T09:00:00.000Z' },
    })
    expect(mergeOpsSignals(occupancy, [live!, extra!]).map((row) => row.id)).toEqual(['waage:t-1', 'lager:ein-1'])
  })
})
