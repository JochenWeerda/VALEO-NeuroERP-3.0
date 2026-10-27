import { describe, expect, it } from 'vitest'
import {
  TOUR_CREATED_IST_EVENT,
  WORKSPACE_TOUR_SSE_URL,
  isTourCreatedSsePayload,
  workspaceTourSseUrl,
} from '@/components/mask-builder/specialized/workspace-tour-sse'
import {
  EINLAGERUNG_IST,
  GOODS_RECEIPT_IST,
  WAAGE_ALLOCATED_IST,
  istTypeFromSse,
} from '@/components/mask-builder/specialized/ops-signals'
import { appendSseAuthToken } from '@/lib/sse-client'

describe('workspace tour SSE', () => {
  it('erkennt nur den Ist-Namen auf dem Workspace-Kanal', () => {
    expect(WORKSPACE_TOUR_SSE_URL).toBe('/api/events?stream=workspace')
    expect(TOUR_CREATED_IST_EVENT).toBe('logistik.tour.created')
    expect(isTourCreatedSsePayload({ type: 'logistik.tour.created' })).toBe(true)
    expect(isTourCreatedSsePayload({ event_type: 'logistik.tour.created', canonical: 'assignment_confirmed' })).toBe(true)
    expect(isTourCreatedSsePayload(JSON.stringify({ ist_event_type: 'logistik.tour.created' }))).toBe(true)
    expect(isTourCreatedSsePayload({ type: 'assignment_confirmed' })).toBe(false)
    expect(isTourCreatedSsePayload({ type: 'connected', channel: 'workspace' })).toBe(false)
    expect(isTourCreatedSsePayload({}, 'assignment_confirmed')).toBe(false)
    expect(isTourCreatedSsePayload({}, 'logistik.tour.created')).toBe(true)
  })

  it('haengt den Bearer als Query-Token an (EventSource-Grenze)', () => {
    expect(appendSseAuthToken(WORKSPACE_TOUR_SSE_URL, null)).toBeNull()
    expect(appendSseAuthToken(WORKSPACE_TOUR_SSE_URL, '')).toBeNull()
    expect(workspaceTourSseUrl(() => null)).toBeNull()
    expect(workspaceTourSseUrl(() => 'fixture-jwt')).toBe(
      '/api/events?stream=workspace&token=fixture-jwt',
    )
    expect(appendSseAuthToken(WORKSPACE_TOUR_SSE_URL, 'a+b/c=')).toBe(
      '/api/events?stream=workspace&token=a%2Bb%2Fc%3D',
    )
  })

  it('erkennt Waage- und Einlagerungs-Ist-Typen auf demselben Kanal', () => {
    expect(istTypeFromSse({ type: WAAGE_ALLOCATED_IST })).toBe(WAAGE_ALLOCATED_IST)
    expect(istTypeFromSse({ event_type: EINLAGERUNG_IST, canonical: 'document_posted' })).toBe(EINLAGERUNG_IST)
    expect(istTypeFromSse({ type: GOODS_RECEIPT_IST })).toBe(GOODS_RECEIPT_IST)
    expect(istTypeFromSse({ type: 'assignment_confirmed' })).toBeNull()
    expect(istTypeFromSse({ type: TOUR_CREATED_IST_EVENT })).toBeNull()
  })
})
