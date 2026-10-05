/**
 * Offline-Warteschlange fuer mobile Fuetterungsdaten (FEED-MOB-045).
 *
 * Ausdruecklich KEIN zweiter Datenpfad: die Queue haelt exakt die Payloads
 * der bestehenden APIs (inkl. beim Einreihen fixiertem idempotency_key) und
 * replayt sie idempotent ueber dieselben Sender-Funktionen.
 *
 * Statusregeln:
 *  - Netzwerkfehler (kein Response): Eintrag bleibt `pending`, der Replay
 *    stoppt (weiter offline — nicht jeden Eintrag anrennen).
 *  - HTTP 409 (z. B. Plan veraltet): `conflict` mit sichtbarer Meldung;
 *    wird nicht blind erneut gesendet, braucht eine fachliche Entscheidung.
 *  - andere HTTP-Fehler: `failed` mit Fehlertext — nie stilles Verwerfen;
 *    `retry()` stoesst explizit neu an.
 */

export type QueueKind = 'actual_feeding'

export type QueueItemStatus = 'pending' | 'conflict' | 'failed'

export interface QueuedItem {
  id: string
  kind: QueueKind
  status: QueueItemStatus
  attempts: number
  enqueued_at: string
  last_error?: string
  payload: Record<string, unknown> & { idempotency_key?: string }
}

export interface QueueStorage {
  load(): QueuedItem[]
  save(items: QueuedItem[]): void
}

export interface ReplaySummary {
  sent: number
  conflicts: number
  failed: number
  remaining: number
}

export const FEEDING_OFFLINE_QUEUE_KEY = 'valeo.feeding-offline-queue.v1'

interface HttpishError {
  response?: { status?: number; data?: { detail?: unknown } }
  request?: unknown
  message?: string
}

/** Netzwerkfehler = Request ohne Response (axios-Konvention). */
export function isNetworkError(error: unknown): boolean {
  const candidate = error as HttpishError
  return Boolean(candidate && candidate.request !== undefined && candidate.response === undefined)
}

function errorDetail(error: unknown): string {
  const candidate = error as HttpishError
  const detail = candidate?.response?.data?.detail
  if (typeof detail === 'string' && detail) return detail
  return candidate?.message ?? 'Unbekannter Fehler'
}

export function createMemoryQueueStorage(): QueueStorage {
  let items: QueuedItem[] = []
  return {
    load: () => items.map((item) => ({ ...item })),
    save: (next) => { items = next.map((item) => ({ ...item })) },
  }
}

export function createLocalStorageQueueStorage(key: string = FEEDING_OFFLINE_QUEUE_KEY): QueueStorage {
  return {
    load: () => {
      try {
        const raw = localStorage.getItem(key)
        const parsed = raw ? (JSON.parse(raw) as QueuedItem[]) : []
        return Array.isArray(parsed) ? parsed : []
      } catch {
        // defekter Speicherstand darf die Erfassung nicht blockieren;
        // die Queue startet leer und der Nutzer sieht ausstehende Fehler serverseitig
        return []
      }
    },
    save: (items) => { localStorage.setItem(key, JSON.stringify(items)) },
  }
}

export class FeedingOfflineQueue {
  constructor(private readonly storage: QueueStorage = createLocalStorageQueueStorage()) {}

  items(): QueuedItem[] {
    return this.storage.load()
  }

  pending(): QueuedItem[] {
    return this.items().filter((item) => item.status === 'pending')
  }

  conflicts(): QueuedItem[] {
    return this.items().filter((item) => item.status === 'conflict')
  }

  enqueue(kind: QueueKind, payload: QueuedItem['payload']): QueuedItem {
    const item: QueuedItem = {
      id: crypto.randomUUID(),
      kind,
      status: 'pending',
      attempts: 0,
      enqueued_at: new Date().toISOString(),
      // idempotency_key wird beim Einreihen fixiert: jeder Replay derselben
      // Eingabe trifft den idempotenten API-Vertrag, nie einen Doppelstand.
      payload: { ...payload, idempotency_key: String(payload.idempotency_key ?? crypto.randomUUID()) },
    }
    this.storage.save([...this.items(), item])
    return item
  }

  remove(id: string): void {
    this.storage.save(this.items().filter((item) => item.id !== id))
  }

  retry(id: string): void {
    this.storage.save(this.items().map((item) =>
      item.id === id ? { ...item, status: 'pending' as const } : item))
  }

  async replay(senders: Record<QueueKind, (payload: QueuedItem['payload']) => Promise<unknown>>): Promise<ReplaySummary> {
    const summary: ReplaySummary = { sent: 0, conflicts: 0, failed: 0, remaining: 0 }
    let items = this.items()
    for (const item of [...items]) {
      if (item.status !== 'pending') continue
      const sender = senders[item.kind]
      if (!sender) continue
      try {
        await sender(item.payload)
        items = items.filter((candidate) => candidate.id !== item.id)
        summary.sent += 1
      } catch (error) {
        if (isNetworkError(error)) {
          // weiter offline: unveraendert pending lassen und Replay stoppen
          break
        }
        const status: QueueItemStatus =
          (error as HttpishError).response?.status === 409 ? 'conflict' : 'failed'
        if (status === 'conflict') summary.conflicts += 1
        else summary.failed += 1
        items = items.map((candidate) => candidate.id === item.id
          ? { ...candidate, status, attempts: candidate.attempts + 1, last_error: errorDetail(error) }
          : candidate)
      }
      this.storage.save(items)
    }
    this.storage.save(items)
    summary.remaining = items.filter((item) => item.status === 'pending').length
    return summary
  }
}
