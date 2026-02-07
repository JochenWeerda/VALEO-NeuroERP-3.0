import { useCallback, useEffect, useMemo, useRef, useState } from 'react'

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: Date
  read: boolean
  action?: {
    label: string
    href: string
  }
}

interface UseNotificationsOptions {
  sseUrl?: string
  maxNotifications?: number
}

const STORAGE_KEY = 'valeo-notifications'
const DEFAULT_SSE_URL = '/api/events?stream=notifications'
const SSE_FEATURE_FLAG = (import.meta.env as Record<string, string | undefined>).VITE_FEATURE_SSE
const SSE_ENABLED = SSE_FEATURE_FLAG === '1' || SSE_FEATURE_FLAG === 'true'

function loadStoredNotifications(): Notification[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return []
    const parsed = JSON.parse(stored)
    return parsed.map((n: Notification) => ({
      ...n,
      timestamp: new Date(n.timestamp),
    }))
  } catch {
    return []
  }
}

function saveNotifications(notifications: Notification[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(notifications))
  } catch {
    // Storage full or unavailable
  }
}

export function useNotifications(options: UseNotificationsOptions = {}) {
  const { sseUrl = DEFAULT_SSE_URL, maxNotifications = 50 } = options
  const [notifications, setNotifications] = useState<Notification[]>(loadStoredNotifications)
  const [isConnected, setIsConnected] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)

  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: crypto.randomUUID(),
      timestamp: new Date(),
      read: false,
    }

    setNotifications((prev) => {
      const updated = [newNotification, ...prev].slice(0, maxNotifications)
      queueMicrotask(() => saveNotifications(updated))
      return updated
    })
  }, [maxNotifications])

  const markAsRead = useCallback((id: string) => {
    setNotifications((prev) => {
      const updated = prev.map((n) => (n.id === id ? { ...n, read: true } : n))
      queueMicrotask(() => saveNotifications(updated))
      return updated
    })
  }, [])

  const markAllAsRead = useCallback(() => {
    setNotifications((prev) => {
      const updated = prev.map((n) => ({ ...n, read: true }))
      queueMicrotask(() => saveNotifications(updated))
      return updated
    })
  }, [])

  const clearNotification = useCallback((id: string) => {
    setNotifications((prev) => {
      const updated = prev.filter((n) => n.id !== id)
      queueMicrotask(() => saveNotifications(updated))
      return updated
    })
  }, [])

  const clearAll = useCallback(() => {
    setNotifications([])
    saveNotifications([])
  }, [])

  // Connect to SSE
  useEffect(() => {
    if (!SSE_ENABLED) {
      setIsConnected(false)
      return
    }

    const connect = () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }

      try {
        const eventSource = new EventSource(sseUrl)
        eventSourceRef.current = eventSource

        eventSource.onopen = () => {
          setIsConnected(true)
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current)
            reconnectTimeoutRef.current = null
          }
        }

        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            if (data.type === 'notification') {
              // Defer to avoid blocking message handler (Chrome Violation >50ms)
              const payload = {
                type: (data.severity || 'info') as 'info' | 'success' | 'warning' | 'error',
                title: data.title,
                message: data.message,
                action: data.action,
              }
              queueMicrotask(() => addNotification(payload))
            }
          } catch {
            // Invalid message format
          }
        }

        eventSource.onerror = () => {
          setIsConnected(false)
          eventSource.close()
          eventSourceRef.current = null

          // Reconnect after 5 seconds
          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect()
          }, 5000)
        }
      } catch {
        setIsConnected(false)
      }
    }

    connect()

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
        eventSourceRef.current = null
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
    }
  }, [sseUrl, addNotification])

  const unreadCount = useMemo(
    () => notifications.filter((n) => !n.read).length,
    [notifications]
  )

  return {
    notifications,
    unreadCount,
    isConnected,
    addNotification,
    markAsRead,
    markAllAsRead,
    clearNotification,
    clearAll,
  }
}
