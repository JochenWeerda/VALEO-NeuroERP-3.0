import { useEffect, useRef, useState } from "react"
import { type ConnectionState, type McpRealtimeEvent, mcpEventBus } from "@/lib/mcp-event-bus"

export type { ConnectionState, McpRealtimeEvent } from "@/lib/mcp-event-bus"

interface RealtimeOptions {
  enabled?: boolean
}

export function useMcpRealtime(
  service: string,
  handler: (event: McpRealtimeEvent) => void,
  options?: RealtimeOptions,
): void {
  const { enabled = true } = options ?? {}
  const stableHandler = useRef(handler)

  useEffect(() => {
    stableHandler.current = handler
  }, [handler])

  useEffect(() => {
    if (!enabled) {
      return
    }
    const unsubscribe = mcpEventBus.addServiceListener(service, (event) => {
      stableHandler.current(event)
    })
    return () => {
      unsubscribe()
    }
  }, [enabled, service])
}

export function useMcpConnectionState(options?: RealtimeOptions): ConnectionState {
  const { enabled = true } = options ?? {}
  const [state, setState] = useState<ConnectionState>(
    enabled ? mcpEventBus.getConnectionState() : "idle",
  )

  useEffect(() => {
    if (!enabled) {
      return
    }
    return mcpEventBus.addConnectionListener(setState)
  }, [enabled])

  return enabled ? state : "idle"
}
