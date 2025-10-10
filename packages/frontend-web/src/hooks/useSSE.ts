import { useEffect } from "react";
import { mcpEventBus } from "@/lib/mcp-event-bus";
import type { MCPEvent } from "@/lib/mcp-events";

export function useSSE(onEvent: (event: MCPEvent) => void, url?: string): void {
  useEffect(() => {
    if (typeof url === 'string' && url.length > 0) {
      mcpEventBus.setEventsUrl(url);
    }
    const unsubscribe = mcpEventBus.addTypedListener(onEvent);
    return () => {
      unsubscribe();
    };
  }, [onEvent, url]);
}
