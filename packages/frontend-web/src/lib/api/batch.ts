/**
 * OData-style API batch client.
 *
 * Collects GET requests within a configurable time window and sends them
 * as a single POST /$batch request to reduce HTTP round-trips.
 */
import { apiClient } from '../api-client'

interface SubRequest {
  id: string
  path: string
}

interface SubResponse {
  id: string
  status: number
  body: unknown
}

interface BatchResponse {
  responses: SubResponse[]
}

type PendingRequest = {
  path: string
  resolve: (value: SubResponse) => void
  reject: (reason: unknown) => void
}

const BATCH_WINDOW_MS = 50
const MAX_BATCH_SIZE = 10

const pendingQueue: PendingRequest[] = []
let flushTimer: ReturnType<typeof setTimeout> | null = null

function scheduleFlush(): void {
  if (flushTimer !== null) return
  flushTimer = setTimeout(flush, BATCH_WINDOW_MS)
}

async function flush(): Promise<void> {
  flushTimer = null
  if (pendingQueue.length === 0) return

  const batch = pendingQueue.splice(0, MAX_BATCH_SIZE)

  const subRequests: SubRequest[] = batch.map((item, idx) => ({
    id: String(idx),
    path: item.path,
  }))

  try {
    const { data } = await apiClient.post<BatchResponse>('/api/v1/$batch', {
      requests: subRequests,
    })

    for (const resp of data.responses) {
      const idx = Number(resp.id)
      batch[idx]?.resolve(resp)
    }
  } catch (err) {
    for (const item of batch) {
      item.reject(err)
    }
  }

  if (pendingQueue.length > 0) {
    scheduleFlush()
  }
}

/**
 * Enqueue a GET request for batching. Returns a promise that resolves
 * with the sub-response once the batch is executed.
 *
 * @example
 * const resp = await batchGet('/api/v1/contacts?skip=0&limit=25')
 * if (resp.status === 200) {
 *   console.log(resp.body)
 * }
 */
export function batchGet(path: string): Promise<SubResponse> {
  return new Promise<SubResponse>((resolve, reject) => {
    pendingQueue.push({ path, resolve, reject })
    scheduleFlush()
  })
}

/**
 * Force-flush any pending batch requests immediately.
 * Useful before navigation or when you need results synchronously.
 */
export function flushBatch(): Promise<void> {
  if (flushTimer !== null) {
    clearTimeout(flushTimer)
    flushTimer = null
  }
  return flush()
}
