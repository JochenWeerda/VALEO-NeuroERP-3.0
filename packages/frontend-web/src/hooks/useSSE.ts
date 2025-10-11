import { useEffect } from 'react'
import { useSSEContext } from '@/app/providers/SSEProvider'
import type { MCPEvent } from '@/lib/mcp-events'

export function useSSE(onEvent: (event: MCPEvent) => void): void {
  const { addTypedListener } = useSSEContext()

  useEffect(() => {
    const unsubscribe = addTypedListener(onEvent)
    return () => {
      unsubscribe()
    }
  }, [addTypedListener, onEvent])
}
