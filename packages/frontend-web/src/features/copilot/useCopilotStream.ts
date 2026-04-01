import { useCallback, useEffect, useRef, useState } from 'react'

interface CopilotMessage {
  type: string
  session_id?: string
  state?: string
  chunk?: string
  full_text?: string
  index?: number
  result?: Record<string, unknown>
  error?: string
}

interface UseCopilotStreamOptions {
  url?: string
  token?: string
  tenantId?: string
  onStateChange?: (state: string) => void
  onMessage?: (message: CopilotMessage) => void
  autoReconnect?: boolean
}

export function useCopilotStream(options: UseCopilotStreamOptions = {}) {
  const {
    url = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/copilot/chat`,
    token,
    tenantId,
    onStateChange,
    onMessage,
    autoReconnect = true,
  } = options

  const [connected, setConnected] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [streaming, setStreaming] = useState(false)
  const [currentChunks, setCurrentChunks] = useState<string[]>([])
  const [lastResponse, setLastResponse] = useState<string | null>(null)
  const [pipelineResult, setPipelineResult] = useState<Record<string, unknown> | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>()
  const manuallyClosedRef = useRef(false)
  const onMessageRef = useRef(onMessage)
  const onStateChangeRef = useRef(onStateChange)

  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])

  useEffect(() => {
    onStateChangeRef.current = onStateChange
  }, [onStateChange])

  const connect = useCallback(() => {
    manuallyClosedRef.current = false
    if (wsRef.current?.readyState === WebSocket.OPEN) return
    if (wsRef.current?.readyState === WebSocket.CONNECTING) return

    const params = new URLSearchParams()
    if (token) {
      params.set('token', token)
    }
    if (tenantId) {
      params.set('tenant_id', tenantId)
    }
    const wsUrl = params.size > 0 ? `${url}?${params.toString()}` : url
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      setConnected(true)
    }

    ws.onmessage = (event) => {
      try {
        const msg: CopilotMessage = JSON.parse(event.data)
        onMessageRef.current?.(msg)

        switch (msg.type) {
          case 'session_start':
            setSessionId(msg.session_id ?? null)
            break
          case 'state_change':
            onStateChangeRef.current?.(msg.state ?? 'unknown')
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
          case 'pipeline_result':
            setPipelineResult(msg.result ?? null)
            break
        }
      } catch {
        // ignore parse errors
      }
    }

    ws.onclose = () => {
      setConnected(false)
      setSessionId(null)
      wsRef.current = null
      if (!manuallyClosedRef.current && autoReconnect) {
        reconnectTimer.current = setTimeout(connect, 3000)
      }
    }

    ws.onerror = () => {
      ws.close()
    }

    wsRef.current = ws
  }, [url, token, tenantId, autoReconnect])

  const disconnect = useCallback(() => {
    manuallyClosedRef.current = true
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
      manuallyClosedRef.current = true
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
    pipelineResult,
  }
}
