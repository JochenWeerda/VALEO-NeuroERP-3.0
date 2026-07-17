/**
 * FEED-MOB-045 (TDD-Red-Welle 1): Offline-Warteschlange fuer mobile
 * Ist-Fuetterungen — kein zweiter Datenpfad, idempotente Replays ueber
 * dieselben APIs. Vor der Implementierung geschrieben.
 */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  FeedingOfflineQueue,
  createMemoryQueueStorage,
  isNetworkError,
} from '@/lib/offline/feeding-offline-queue'

function networkError(): Error {
  const error = new Error('Network Error') as Error & { request?: unknown }
  error.request = {}
  return error
}

function httpError(status: number, detail: string): Error {
  const error = new Error(detail) as Error & { response?: { status: number; data: { detail: string } } }
  error.response = { status, data: { detail } }
  return error
}

const PAYLOAD = {
  plan_version_id: 'pv-1',
  feeding_at: '2026-07-17T06:00:00Z',
  source: 'manual',
  source_ref: 'mobile:cmd-1',
  cause_class: 'normal',
  comment: null,
  supersedes_id: null,
  context: {},
  idempotency_key: 'mobile-actual-cmd-1',
  components: [{ feed_id: 'f-1', actual_kg: 120 }],
}

describe('FeedingOfflineQueue', () => {
  let queue: FeedingOfflineQueue

  beforeEach(() => {
    queue = new FeedingOfflineQueue(createMemoryQueueStorage())
  })

  it('reiht Payloads mit fixiertem idempotency_key ein und persistiert sie', () => {
    const item = queue.enqueue('actual_feeding', { ...PAYLOAD })
    expect(item.status).toBe('pending')
    expect(item.payload.idempotency_key).toBe('mobile-actual-cmd-1')
    expect(queue.pending()).toHaveLength(1)
  })

  it('replayt FIFO mit exakt dem eingereihten Payload und entfernt Erfolge', async () => {
    queue.enqueue('actual_feeding', { ...PAYLOAD, source_ref: 'mobile:a' })
    queue.enqueue('actual_feeding', { ...PAYLOAD, source_ref: 'mobile:b' })
    const sender = vi.fn().mockResolvedValue({ id: 'r-1' })

    const summary = await queue.replay({ actual_feeding: sender })

    expect(summary.sent).toBe(2)
    expect(queue.pending()).toHaveLength(0)
    expect(sender).toHaveBeenNthCalledWith(1, expect.objectContaining({ source_ref: 'mobile:a' }))
    expect(sender).toHaveBeenNthCalledWith(2, expect.objectContaining({ source_ref: 'mobile:b' }))
    // kein zweiter Datenpfad: der Sender erhaelt den unveraenderten API-Payload
    expect(sender.mock.calls[0][0].idempotency_key).toBe('mobile-actual-cmd-1')
  })

  it('stoppt bei Netzwerkfehler und laesst Eintraege unveraendert pending', async () => {
    queue.enqueue('actual_feeding', { ...PAYLOAD, source_ref: 'mobile:a' })
    queue.enqueue('actual_feeding', { ...PAYLOAD, source_ref: 'mobile:b' })
    const sender = vi.fn().mockRejectedValue(networkError())

    const summary = await queue.replay({ actual_feeding: sender })

    expect(summary.sent).toBe(0)
    expect(summary.remaining).toBe(2)
    expect(sender).toHaveBeenCalledTimes(1), 'weiter offline: nicht jeden Eintrag anrennen'
    expect(queue.pending().map((item) => item.status)).toEqual(['pending', 'pending'])
  })

  it('markiert 409 als Konflikt mit sichtbarer Meldung und sendet ihn nicht blind erneut', async () => {
    queue.enqueue('actual_feeding', { ...PAYLOAD })
    const sender = vi.fn().mockRejectedValue(httpError(409, 'Planversion ist veraltet.'))

    const first = await queue.replay({ actual_feeding: sender })
    expect(first.conflicts).toBe(1)
    const conflict = queue.items()[0]
    expect(conflict.status).toBe('conflict')
    expect(conflict.last_error).toContain('veraltet')

    sender.mockClear()
    const second = await queue.replay({ actual_feeding: sender })
    expect(second.sent).toBe(0)
    expect(sender).not.toHaveBeenCalled()
  })

  it('markiert fachliche Fehler als failed statt sie still zu verwerfen', async () => {
    queue.enqueue('actual_feeding', { ...PAYLOAD })
    const sender = vi.fn().mockRejectedValue(httpError(422, 'Komponente unbekannt.'))

    const summary = await queue.replay({ actual_feeding: sender })
    expect(summary.failed).toBe(1)
    const failed = queue.items()[0]
    expect(failed.status).toBe('failed')
    expect(failed.last_error).toContain('Komponente unbekannt')
    // explizites Wiederanstossen ist moeglich
    queue.retry(failed.id)
    expect(queue.pending()).toHaveLength(1)
  })

  it('erkennt Netzwerkfehler (kein Response) im Gegensatz zu HTTP-Fehlern', () => {
    expect(isNetworkError(networkError())).toBe(true)
    expect(isNetworkError(httpError(409, 'x'))).toBe(false)
  })
})
