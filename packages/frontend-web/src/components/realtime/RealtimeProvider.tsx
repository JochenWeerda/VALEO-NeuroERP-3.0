/**
 * Realtime Provider Component
 * Manages SSE connections and provides realtime updates to child components
 */

import React, { createContext, useContext, useCallback, useEffect } from 'react'
import { useSSE, type SSEMessage } from '@/lib/hooks/useSSE'
import { useQueryClient } from '@tanstack/react-query'

type RealtimeContextValue = {
  isConnected: boolean
  subscribe: (_eventType: string, _handler: (_data: any) => void) => () => void
}

const RealtimeContext = createContext<RealtimeContextValue | null>(null)

export function useRealtime() {
  const context = useContext(RealtimeContext)
  if (!context) {
    throw new Error('useRealtime must be used within RealtimeProvider')
  }
  return context
}

type RealtimeProviderProps = {
  children: React.ReactNode
  channel?: string
  enabled?: boolean
}

export function RealtimeProvider({
  children,
  channel = 'default',
  enabled = true,
}: RealtimeProviderProps) {
  const queryClient = useQueryClient()
  const eventHandlers = React.useRef<Map<string, Set<(_data: any) => void>>>(
    new Map()
  )

  const handleMessage = useCallback(
    (message: SSEMessage) => {
      const eventType = message.event ?? message.data.event ?? 'message'
      const handlers = eventHandlers.current.get(eventType)

      if (handlers) {
        handlers.forEach((handler) => {
          try {
            handler(message.data)
          } catch (error) {
            console.error(`Error in SSE handler for ${eventType}:`, error)
          }
        })
      }

      // Auto-invalidate queries based on event type
      if (eventType.startsWith('customer_')) {
        queryClient.invalidateQueries({ queryKey: ['crm', 'customers'] })
      } else if (eventType.startsWith('article_')) {
        queryClient.invalidateQueries({ queryKey: ['inventory', 'articles'] })
      } else if (eventType.startsWith('workflow_')) {
        queryClient.invalidateQueries({ queryKey: ['workflows'] })
      }
    },
    [queryClient]
  )

  const { status, isConnected } = useSSE({
    channel,
    autoConnect: enabled,
    onMessage: handleMessage,
    onError: (error) => {
      console.error('SSE Error:', error)
    },
    onConnect: () => {
      console.log('✅ Realtime connection established')
    },
    onDisconnect: () => {
      console.log('👋 Realtime connection closed')
    },
  })

  const subscribe = useCallback(
    (eventType: string, handler: (_data: any) => void) => {
      if (!eventHandlers.current.has(eventType)) {
        eventHandlers.current.set(eventType, new Set())
      }

      eventHandlers.current.get(eventType)?.add(handler)

      // Return unsubscribe function
      return () => {
        const handlers = eventHandlers.current.get(eventType)
        if (handlers) {
          handlers.delete(handler)
          if (handlers.size === 0) {
            eventHandlers.current.delete(eventType)
          }
        }
      }
    },
    []
  )

  // Show connection status in dev mode
  useEffect(() => {
    if (import.meta.env.DEV) {
      console.log(`SSE Status: ${status}`)
    }
  }, [status])

  const value: RealtimeContextValue = {
    isConnected,
    subscribe,
  }

  return (
    <RealtimeContext.Provider value={value}>
      {children}
    </RealtimeContext.Provider>
  )
}

/**
 * Hook to subscribe to specific realtime events
 */
export function useRealtimeEvent<T = any>(
  eventType: string,
  handler: (_data: T) => void
) {
  const { subscribe } = useRealtime()

  useEffect(() => {
    const unsubscribe = subscribe(eventType, handler)
    return unsubscribe
  }, [eventType, handler, subscribe])
}

