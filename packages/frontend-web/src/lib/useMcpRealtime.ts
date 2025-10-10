import { useEffect, useRef, useState } from "react";
import {
  type ConnectionState,
  type McpRealtimeEvent,
  mcpEventBus,
} from "@/lib/mcp-event-bus";

export type { ConnectionState, McpRealtimeEvent } from "@/lib/mcp-event-bus";

export function useMcpRealtime(service: string, handler: (event: McpRealtimeEvent) => void): void {
  const stableHandler = useRef(handler);
  useEffect(() => {
    stableHandler.current = handler;
  }, [handler]);

  useEffect(() => {
    const unsubscribe = mcpEventBus.addServiceListener(service, (event) => {
      stableHandler.current(event);
    });
    return () => {
      unsubscribe();
    };
  }, [service]);
}

export function useMcpConnectionState(): ConnectionState {
  const [state, setState] = useState<ConnectionState>(mcpEventBus.getConnectionState());
  useEffect(() => mcpEventBus.addConnectionListener(setState), []);
  return state;
}
