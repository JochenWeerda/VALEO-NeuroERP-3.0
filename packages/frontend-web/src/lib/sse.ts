import { useEffect, useRef } from 'react'

type SSEStatus = 'open' | 'closed' | 'error'

const RECONNECT_DELAY_MS = 1_500

interface UseSSEOptions {
  onStatus?: (_status: SSEStatus) => void
  heartbeatMs?: number
}

export function useSSE(channel: string, onMessage: (_data: unknown) => void, opts?: UseSSEOptions): void {
  const handler = useRef(onMessage)
  handler.current = onMessage

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    let eventSource: EventSource | null = null
    let reconnectTimeout: number | undefined
    let heartbeatInterval: number | undefined
    let stopped = false

    const clearReconnect = (): void => {
      if (reconnectTimeout !== undefined) {
        window.clearTimeout(reconnectTimeout)
        reconnectTimeout = undefined
      }
    }

    const clearHeartbeat = (): void => {
      if (heartbeatInterval !== undefined) {
        window.clearInterval(heartbeatInterval)
        heartbeatInterval = undefined
      }
    }

    const connect = (): void => {
      if (stopped) {
        return
      }

      eventSource = new EventSource(`/api/stream/${channel}`)
      opts?.onStatus?.('open')

      eventSource.onmessage = (event): void => {
        try {
          handler.current(JSON.parse(event.data))
        } catch {
          // ignore parse errors
        }
      }

      eventSource.onerror = (): void => {
        opts?.onStatus?.('error')
        eventSource?.close()
        eventSource = null
        clearReconnect()
        reconnectTimeout = window.setTimeout(connect, RECONNECT_DELAY_MS)
      }
    }

    connect()

    if (typeof opts?.heartbeatMs === 'number' && opts.heartbeatMs > 0) {
      heartbeatInterval = window.setInterval((): void => {
        // browser EventSource keeps the connection alive; hook reserved for future metrics
      }, opts.heartbeatMs)
    }

    return () => {
      stopped = true
      clearReconnect()
      clearHeartbeat()
      eventSource?.close()
      opts?.onStatus?.('closed')
    }
  }, [channel, opts?.heartbeatMs, opts?.onStatus])
}
