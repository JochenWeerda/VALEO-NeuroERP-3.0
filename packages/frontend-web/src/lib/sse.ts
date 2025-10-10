import { useEffect, useRef } from 'react'

export function useSSE(
  channel: string,
  onMessage: (data: unknown) => void,
  opts?: {
    onStatus?: (s: 'open' | 'closed' | 'error') => void
    heartbeatMs?: number
  }
) {
  const handler = useRef(onMessage)
  handler.current = onMessage

  useEffect(() => {
    let es: EventSource | null = null
    let timer: any = null
    let stopped = false

    function connect() {
      if (stopped) return
      es = new EventSource(`/api/stream/${channel}`)
      opts?.onStatus?.('open')
      es.onmessage = (e) => {
        try {
          handler.current(JSON.parse(e.data))
        } catch {
          // ignore parse errors
        }
      }
      es.onerror = () => {
        opts?.onStatus?.('error')
        es?.close()
        es = null
        // Reconnect with backoff
        timer = setTimeout(connect, 1500)
      }
    }

    connect()

    if (opts?.heartbeatMs && opts.heartbeatMs > 0) {
      const hb = setInterval(() => {
        // no-op: browser EventSource keeps alive; server may send comments
      }, opts.heartbeatMs)
      timer = hb
    }

    return () => {
      stopped = true
      if (timer) clearInterval(timer)
      es?.close()
    }
  }, [channel])
}