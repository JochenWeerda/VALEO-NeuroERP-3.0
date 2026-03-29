import { useCallback, useEffect, useRef, useState } from 'react'

interface CopilotMessage {
  type: string
  session_id?: string
  state?: string
  chunk?: string
  full_text?: string
  index?: number
}

interface UseCopilotStreamOptions {
  url?: string
  token?: string
  onStateChange?: (state: string) => void
}

export function useCopilotStream(options: UseCopilotStreamOptions = {}) {
  const {
    url = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/copilot/chat`,
    token,
    onStateChange,
  } = options

  const [connected, setConnected] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [streaming, setStreaming] = useState(false)
  const [currentChunks, setCurrentChunks] = useState<string[]>([])
  const [lastResponse, setLastResponse] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>()

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const wsUrl = token ? `${url}?token=${encodeURIComponent(token)}` : url
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      setConnected(true)
    }

    ws.onmessage = (event) => {
      try {
        const msg: CopilotMessage = JSON.parse(event.data)

        switch (msg.type) {
          case 'session_start':
            setSessionId(msg.session_id ?? null)
            break
          case 'state_change':
            onStateChange?.(msg.state ?? 'unknown')
            break
          case 'stream_start':
            setStreaming(true)
            setCurrentChunks([])
            break
          case 'stream_chunk':
            setCurrentChunks((prev) => [...prev, msg.chunk ?? ''])
            break
          case 'stream_end':
            setStreaming(false)
            setLastResponse(msg.full_text ?? null)
            break
        }
      } catch {
        // ignore parse errors
      }
    }

    ws.onclose = () => {
      setConnected(false)
      setSessionId(null)
      reconnectTimer.current = setTimeout(connect, 3000)
    }

    ws.onerror = () => {
      ws.close()
    }

    wsRef.current = ws
  }, [url, token, onStateChange])

  const disconnect = useCallback(() => {
    clearTimeout(reconnectTimer.current)
    wsRef.current?.close()
    wsRef.current = null
    setConnected(false)
    setSessionId(null)
  }, [])

  const send = useCallback((text: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ text }))
    }
  }, [])

  useEffect(() => {
    return () => {
      clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [])

  return {
    connect,
    disconnect,
    send,
    connected,
    sessionId,
    streaming,
    currentText: currentChunks.join(''),
    lastResponse,
  }
}
