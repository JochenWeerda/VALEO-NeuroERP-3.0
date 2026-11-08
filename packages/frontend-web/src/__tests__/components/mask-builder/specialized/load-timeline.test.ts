import { describe, expect, it } from 'vitest'
import {
  TIMELINE_FIELD_MISSING,
  axisFromLanes,
  formatStopLatLng,
  laneFromTourDetail,
  markerOffset,
  readPlannedArrival,
  readStopLatLng,
} from '@/components/mask-builder/specialized/load-timeline'

describe('tour timeline reader', () => {
  it('liest nur vorhandenes planned_arrival und erfindet kein Zeitfenster', () => {
    expect(readPlannedArrival(null)).toBeNull()
    expect(readPlannedArrival('nicht-iso')).toBeNull()
    expect(readPlannedArrival('2026-10-22T08:00:00.000Z')).toBe('2026-10-22T08:00:00.000Z')
    const lane = laneFromTourDetail({
      id: 'tour-1',
      vehicle_id: 'LKW',
      stops: [
        { id: 's1', planned_arrival: '2026-10-22T08:00:00.000Z', delivery_note_ref: 'LS-1' },
        { id: 's2', planned_arrival: null, address: 'ohne Zeit' },
      ],
    }, 'tour-1')
    expect(lane.stops).toEqual([
      { stopId: 's1', resourceId: 'tour-1', plannedArrival: '2026-10-22T08:00:00.000Z', label: 'LS-1' },
    ])
    expect(axisFromLanes([lane])).toEqual({
      startMs: Date.parse('2026-10-22T08:00:00.000Z'),
      endMs: Date.parse('2026-10-22T08:00:00.000Z'),
    })
    expect(markerOffset('2026-10-22T08:00:00.000Z', { startMs: 1, endMs: 1 })).toBe(50)
    expect(lane.coordinates).toEqual([])
    expect(TIMELINE_FIELD_MISSING).toMatch(/planned_arrival fehlt/)
  })

  it('uebernimmt lat/lng aus dem Tour-GET und verwirft ungueltige Werte', () => {
    expect(readStopLatLng('53.1', 8.8)).toBeNull()
    expect(readStopLatLng(91, 8.8)).toBeNull()
    expect(readStopLatLng(53.1, Number.NaN)).toBeNull()
    const lane = laneFromTourDetail({
      id: 'tour-1',
      vehicle_id: 'LKW',
      stops: [
        {
          id: 's1',
          planned_arrival: '2026-10-22T08:00:00.000Z',
          delivery_note_ref: 'LS-1',
          lat: 53.0793,
          lng: 8.8017,
        },
        { id: 's2', planned_arrival: null, address: 'nur Lage', lat: 53.5, lng: 8.1 },
        { id: 's3', address: 'text', lat: '53.1', lng: 8.2 },
      ],
    }, 'tour-1')
    expect(lane.stops).toEqual([
      {
        stopId: 's1',
        resourceId: 'tour-1',
        plannedArrival: '2026-10-22T08:00:00.000Z',
        label: 'LS-1',
        lat: 53.0793,
        lng: 8.8017,
      },
    ])
    expect(lane.coordinates).toEqual([
      { stopId: 's1', label: 'LS-1', lat: 53.0793, lng: 8.8017 },
      { stopId: 's2', label: 'nur Lage', lat: 53.5, lng: 8.1 },
    ])
    expect(formatStopLatLng(53.0793, 8.8017)).toBe('53,07930, 8,80170')
  })
})
