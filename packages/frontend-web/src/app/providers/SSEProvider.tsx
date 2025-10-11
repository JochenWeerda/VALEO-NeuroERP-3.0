import { type PropsWithChildren, createContext, useContext, useEffect, useMemo } from 'react'
import { type ConnectionState, type McpRealtimeListener, type McpTypedListener, mcpEventBus } from '@/lib/mcp-event-bus'
import { useMcpConnectionState } from '@/lib/useMcpRealtime'

type SSEProviderProps = PropsWithChildren<{
  url?: string
  enabled?: boolean
  tokenResolver?: () => string | undefined
  withCredentials?: boolean
}>

interface SSEContextValue {
  addTypedListener: (listener: McpTypedListener) => () => void
  addServiceListener: (service: string, listener: McpRealtimeListener) => () => void
  connectionState: ConnectionState
}

const defaultContextValue: SSEContextValue = {
  addTypedListener: (listener) => mcpEventBus.addTypedListener(listener),
  addServiceListener: (service, listener) => mcpEventBus.addServiceListener(service, listener),
  connectionState: 'idle',
}

const SSEContext = createContext<SSEContextValue>(defaultContextValue)

export function SSEProvider({
  url,
  enabled = true,
  tokenResolver,
  withCredentials = false,
  children,
}: SSEProviderProps): JSX.Element {
  useEffect(() => {
    if (enabled) {
      mcpEventBus.setEventsUrl(url)
      mcpEventBus.setAuthTokenResolver(tokenResolver)
      mcpEventBus.setWithCredentials(withCredentials)
    } else {
      mcpEventBus.setAuthTokenResolver(undefined)
      mcpEventBus.setEventsUrl(undefined)
    }
    return () => {
      if (!enabled) {
        mcpEventBus.setAuthTokenResolver(undefined)
        mcpEventBus.setEventsUrl(undefined)
      }
    }
  }, [enabled, tokenResolver, url, withCredentials])

  const connectionState = useMcpConnectionState({ enabled })

  const value = useMemo<SSEContextValue>(
    () => ({
      addTypedListener: (listener) => mcpEventBus.addTypedListener(listener),
      addServiceListener: (service, listener) => mcpEventBus.addServiceListener(service, listener),
      connectionState,
    }),
    [connectionState],
  )

  return <SSEContext.Provider value={value}>{children}</SSEContext.Provider>
}

export const useSSEContext = (): SSEContextValue => {
  return useContext(SSEContext)
}
