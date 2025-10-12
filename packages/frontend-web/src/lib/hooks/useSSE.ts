/**
 * React Hook for Server-Sent Events (SSE)
 * Production-ready with auto-reconnect and error handling
 */

import { useEffect, useRef, useState, useCallback } from 'react'

export type SSEMessage = {
  event?: string
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data: any
  timestamp?: string
}

export type SSEStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

export type UseSSEOptions = {
  channel: string
  baseUrl?: string
  autoConnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
  onMessage?: (message: SSEMessage) => void
  onError?: (error: Error) => void
  onConnect?: () => void
  onDisconnect?: () => void
}

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export function useSSE(options: UseSSEOptions) {
  const {
    channel,
    baseUrl = 'http://localhost:8000',
    autoConnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
    onMessage,
    onError,
    onConnect,
    onDisconnect,
  } = options

  const [status, setStatus] = useState<SSEStatus>('disconnected')
  const [lastMessage, setLastMessage] = useState<SSEMessage | null>(null)
  const [reconnectCount, setReconnectCount] = useState(0)

  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      return // Already connected
    }

    setStatus('connecting')

    const url = `${baseUrl}/api/stream/${channel}`
    const eventSource = new EventSource(url)

    eventSource.onopen = () => {
      setStatus('connected')
      setReconnectCount(0)
      onConnect?.()
    }

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        const message: SSEMessage = {
          data,
          timestamp: new Date().toISOString(),
        }
        setLastMessage(message)
        onMessage?.(message)
      } catch (error) {
        console.error('Failed to parse SSE message:', error)
      }
    }

    eventSource.onerror = () => {
      setStatus('error')
      eventSource.close()
      eventSourceRef.current = null

      const error = new Error('SSE connection error')
      onError?.(error)

      // Auto-reconnect
      if (reconnectCount < maxReconnectAttempts) {
        reconnectTimeoutRef.current = setTimeout(() => {
          setReconnectCount((prev) => prev + 1)
          connect()
        }, reconnectInterval)
      } else {
        setStatus('disconnected')
        onDisconnect?.()
      }
    }

    // Custom event listeners
    eventSource.addEventListener('connected', (event) => {
      console.log('SSE Connected:', event.data)
    })

    eventSource.addEventListener('ping', () => {
      // Heartbeat received
    })

    eventSourceRef.current = eventSource
  }, [
    channel,
    baseUrl,
    reconnectCount,
    maxReconnectAttempts,
    reconnectInterval,
    onMessage,
    onError,
    onConnect,
    onDisconnect,
  ])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
      setStatus('disconnected')
      onDisconnect?.()
    }
  }, [onDisconnect])

  useEffect(() => {
    if (autoConnect) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [autoConnect, connect, disconnect])

  return {
    status,
    lastMessage,
    reconnectCount,
    connect,
    disconnect,
    isConnected: status === 'connected',
  }
}

